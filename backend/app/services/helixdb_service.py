"""HelixDB client helpers built around HelixQL queries."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..config import Settings, get_settings

try:  # pragma: no cover - optional dependency until installed
    import helix
except ImportError:  # pragma: no cover - handled gracefully for docs/tests
    helix = None


logger = logging.getLogger(__name__)

SCHEMA_FILENAME = "schema.hql"
DEFAULT_LIMIT = 20


class HelixDBService:
    """Minimal wrapper for issuing HelixQL queries via helix-py."""

    def __init__(self, *, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.project_root = Path(__file__).resolve().parents[2]
        self._client = self._create_client()

    @property
    def client(self):
        if self._client is None:
            raise RuntimeError(
                "Helix client is unavailable. Ensure helix-py is installed and configured."
            )
        return self._client

    def _create_client(self):  # pragma: no cover - requires helix runtime
        if helix is None:
            logger.warning(
                "helix-py is not installed; HelixDBService cannot be used until it is."
            )
            return None

        config_path = self.project_root / "helix.toml"
        kwargs: Dict[str, Any] = {}
        if config_path.exists():
            kwargs["config_path"] = str(config_path)

        if self.settings.helixdb_endpoint:
            kwargs["endpoint"] = self.settings.helixdb_endpoint
        if self.settings.helixdb_api_key:
            kwargs["api_key"] = self.settings.helixdb_api_key
        if self.settings.helixdb_verbose:
            kwargs["verbose"] = True
        # 'local' is a required parameter for Helix Client
        kwargs["local"] = self.settings.helixdb_local

        attempt_kwargs = dict(kwargs)
        while True:
            try:
                return helix.Client(**attempt_kwargs)
            except TypeError as exc:
                message = str(exc)
                if "unexpected keyword argument" in message:
                    # Drop the unsupported kwarg and retry.
                    start = message.find("'") + 1
                    end = message.find("'", start)
                    bad_key = message[start:end]
                    attempt_kwargs.pop(bad_key, None)
                    continue
                raise
            except Exception as exc:
                logger.error("Unable to initialize HelixDB client: %s", exc)
                raise

    def initialize_schema(self, schema_path: Optional[Path] = None) -> bool:
        """Load the HelixQL schema/queries into the running HelixDB instance."""

        path = schema_path or (self.project_root / SCHEMA_FILENAME)
        if not path.exists():
            logger.warning("HelixQL schema file %s not found", path)
            return False

        schema_text = path.read_text(encoding="utf-8")
        applied = False
        for method_name in ("apply_schema", "schema", "apply"):
            method = getattr(self.client, method_name, None)
            if callable(method):
                try:
                    method(schema_text)
                    applied = True
                    break
                except Exception as exc:
                    logger.error("Helix schema application via %s failed: %s", method_name, exc)
                    raise

        if not applied:
            logger.info(
                "Helix client did not expose a schema apply helper; ensure schema is loaded via CLI."
            )
        return applied

    def get_professor_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        if not url:
            return None
        payload = {"url": url}
        result = self.client.query("GetProfessorByUrl", payload)
        if isinstance(result, list) and result:
            return result[0]
        if isinstance(result, dict):
            inner = result.get("professor") or result.get("result")
            if isinstance(inner, list) and inner:
                return inner[0]
        return None

    def insert_professor(
        self, profile_data: Dict[str, Any], embedding: List[float]
    ) -> Tuple[str, bool]:
        profile_url = profile_data.get("profile_url")
        if profile_url:
            existing = self.get_professor_by_url(profile_url)
            if existing:
                return _extract_vertex_id(existing), False

        # Extract activity_signals if present
        activity_signals = profile_data.get("activity_signals") or {}
        if isinstance(activity_signals, dict):
            recent_publications = activity_signals.get("recent_publications") or []
            news_mentions = activity_signals.get("news_mentions") or []
            hiring = activity_signals.get("hiring", False)
            last_updated = activity_signals.get("last_updated") or ""
        else:
            recent_publications = []
            news_mentions = []
            hiring = False
            last_updated = ""

        payload = {
            "profile_id": profile_data.get("profile_id", ""),
            "name": profile_data.get("name", ""),
            "title": profile_data.get("title", ""),
            "department": profile_data.get("department", ""),
            "profile_url": profile_url or "",
            "summary": profile_data.get("summary", ""),
            "keywords": profile_data.get("keywords", []),
            "recent_publications": recent_publications,
            "news_mentions": news_mentions,
            "hiring": hiring,
            "last_updated": last_updated,
            "rerank_strategy": profile_data.get("rerank_strategy", "hybrid"),
            "vector": embedding,
        }

        logger.debug("Inserting professor profile for %s", payload["profile_url"])
        result = self.client.query("InsertProfessor", payload)
        return _extract_vertex_id(result), True

    def batch_insert_professors(
        self, entries: Iterable[Dict[str, Any]]
    ) -> List[str]:
        ids: List[str] = []
        for entry in entries:
            try:
                profile = entry["profile"]
                embedding = entry["embedding"]
                helix_id, _ = self.insert_professor(profile, embedding)
                ids.append(helix_id)
            except Exception as exc:
                logger.error(
                    "Failed to insert profile for %s: %s",
                    entry.get("profile", {}).get("profile_url"),
                    exc,
                )
        return ids

    def search_similar_professors(
        self,
        embedding: List[float],
        *,
        limit: int = DEFAULT_LIMIT,
    ) -> List[Dict[str, Any]]:
        payload = {"vector": embedding, "limit": int(limit)}
        try:
            raw = self.client.query("SearchSimilarProfessors", payload)
        except Exception as exc:
            error_msg = str(exc).lower()
            # Check if it's a schema/index initialization error
            if "no entry point" in error_msg or "hnsw index" in error_msg:
                logger.warning(
                    "Vector index not found. This usually means the database is empty. "
                    "Initialize the schema and insert some data first."
                )
                # Try to initialize schema, but this won't create the index without data
                try:
                    self.initialize_schema()
                    logger.info("Schema initialized. Insert some professors before searching.")
                except Exception as init_exc:
                    logger.debug("Schema initialization: %s", init_exc)
                # Return empty results - user needs to insert data first
                return []
            else:
                logger.error("Search query failed: %s", exc)
                raise
        
        records = _normalize_search_results(raw)
        return [_extract_professor_properties(record) for record in records]


def _extract_vertex_id(result: Any) -> str:
    if isinstance(result, dict):
        for key in ("id", "vertex_id", "_id"):
            if result.get(key):
                return str(result[key])
        if result:
            first_value = next(iter(result.values()))
            if isinstance(first_value, dict) and first_value.get("id"):
                return str(first_value["id"])
    return str(result)


def _normalize_search_results(raw: Any) -> List[Dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, list):
        # If it's a list, check if items are nested (e.g., [{"professors": [...]}])
        if raw and isinstance(raw[0], dict) and "professors" in raw[0]:
            # Unwrap nested structure: [{"professors": [...]}] -> [...]
            return raw[0]["professors"]
        return [record for record in raw if isinstance(record, dict)]
    if isinstance(raw, dict):
        # Check for nested professors list first
        if "professors" in raw and isinstance(raw["professors"], list):
            return raw["professors"]
        for key in ("results", "data", "items"):
            value = raw.get(key)
            if isinstance(value, list):
                return [record for record in value if isinstance(record, dict)]
        # If it's a single dict that looks like a professor record, return it as a list
        if raw.get("name") or raw.get("profile_id") or raw.get("id"):
            return [raw]
    return []


def _extract_professor_properties(record: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(record, dict):
        return {}

    properties = dict(record)
    node_props = record.get("properties")
    if isinstance(node_props, dict):
        properties.update(node_props)

    keywords = properties.get("keywords") or []
    if isinstance(keywords, str):
        keywords = [keyword.strip() for keyword in keywords.split(",") if keyword.strip()]
    elif not isinstance(keywords, list):
        keywords = [str(keywords)]

    properties["keywords"] = keywords
    
    # Set default values for all fields
    properties.setdefault("profile_id", record.get("profile_id", ""))
    properties.setdefault("profile_url", record.get("profile_url"))
    properties.setdefault("name", record.get("name"))
    properties.setdefault("title", record.get("title", ""))
    properties.setdefault("department", record.get("department"))
    properties.setdefault("summary", record.get("summary"))
    properties.setdefault("recent_publications", record.get("recent_publications", []))
    properties.setdefault("news_mentions", record.get("news_mentions", []))
    properties.setdefault("hiring", record.get("hiring", False))
    properties.setdefault("last_updated", record.get("last_updated", ""))
    properties.setdefault("rerank_strategy", record.get("rerank_strategy", "hybrid"))

    # Reconstruct activity_signals if needed for API compatibility
    if "activity_signals" not in properties:
        properties["activity_signals"] = {
            "recent_publications": properties.get("recent_publications", []),
            "news_mentions": properties.get("news_mentions", []),
            "hiring": properties.get("hiring", False),
            "last_updated": properties.get("last_updated", ""),
        }

    identifier = (
        properties.get("id")
        or record.get("id")
        or record.get("_id")
        or properties.get("profile_id")
        or properties.get("profile_url")
    )
    if identifier:
        properties["id"] = str(identifier)

    return properties
