"""Pipeline orchestration for scraping and persisting professor profiles."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import List, Optional, Sequence

from ..config import Settings, get_settings
from ..models.schemas import ProfileInput
from .embedding import embed_texts
from .firecrawl_service import FirecrawlService, ScrapedProfessor
from .helixdb_service import HelixDBService

logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    url: str
    success: bool
    helix_id: Optional[str] = None
    error: Optional[str] = None
    profile: Optional[ProfileInput] = None
    embedding_model: Optional[str] = None
    created: Optional[bool] = None


@dataclass
class ScrapeSummary:
    results: List[ScrapeResult]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def success_count(self) -> int:
        return sum(1 for result in self.results if result.success)

    @property
    def failure_count(self) -> int:
        return self.total - self.success_count

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "results": [
                {
                    "url": result.url,
                    "success": result.success,
                    "helix_id": result.helix_id,
                    "error": result.error,
                    "profile": result.profile.model_dump() if result.profile else None,
                    "embedding_model": result.embedding_model,
                    "created": result.created,
                }
                for result in self.results
            ],
        }


class ScrapeOrchestrator:
    """Coordinate Firecrawl scraping, embedding, and HelixDB persistence."""

    def __init__(
        self,
        *,
        settings: Optional[Settings] = None,
        firecrawl_service: Optional[FirecrawlService] = None,
        helix_service: Optional[HelixDBService] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.firecrawl = firecrawl_service or FirecrawlService(settings=self.settings)
        self.helix = helix_service or HelixDBService(settings=self.settings)

    def run(
        self,
        urls: Sequence[str],
        *,
        initialize_schema: bool = False,
    ) -> ScrapeSummary:
        if not urls:
            return ScrapeSummary(results=[])

        if initialize_schema:
            try:
                self.helix.initialize_schema()
            except Exception as exc:
                logger.error("Helix schema initialization failed: %s", exc)
                raise

        raw_payloads = self.firecrawl.scrape_batch(urls)

        structured: List[ScrapedProfessor] = []
        results: List[ScrapeResult] = []
        for payload in raw_payloads:
            url = payload.get("url", "") if isinstance(payload, dict) else ""
            error = payload.get("error") if isinstance(payload, dict) else None
            if error:
                results.append(
                    ScrapeResult(url=url or "unknown", success=False, error=error)
                )
                continue
            try:
                structured.append(self.firecrawl.extract_professor(payload))
            except Exception as exc:
                logger.error("Failed to normalize scraped payload for %s: %s", url, exc)
                results.append(
                    ScrapeResult(url=url or "unknown", success=False, error=str(exc))
                )

        if not structured:
            return ScrapeSummary(results=results)

        summaries = [record.summary or record.name for record in structured]
        embeddings, model_name = embed_texts(summaries, settings=self.settings)
        if len(embeddings) < len(structured):
            logger.warning(
                "Embedding count (%s) does not match scraped profile count (%s)",
                len(embeddings),
                len(structured),
            )

        for idx, record in enumerate(structured):
            embedding = embeddings[idx] if idx < len(embeddings) else []
            # Generate a profile_id if not present
            profile_id = record.url or str(uuid.uuid4())
            profile_payload = {
                "profile_id": profile_id,
                "name": record.name,
                "title": getattr(record, "title", None) or "",
                "department": record.department or "",
                "profile_url": record.url,
                "summary": record.summary or "",
                "keywords": record.keywords or [],
                "activity_signals": None,  # Can be populated later from external sources
                "rerank_strategy": "hybrid",
            }
            try:
                helix_id, created = self.helix.insert_professor(
                    profile_payload, embedding
                )
                profile = ProfileInput(
                    profile_id=helix_id or profile_id,
                    name=record.name,
                    title=getattr(record, "title", None),
                    department=record.department,
                    summary=record.summary,
                    keywords=record.keywords,
                    activity_signals=None,
                )
                results.append(
                    ScrapeResult(
                        url=record.url,
                        success=True,
                        helix_id=helix_id,
                        profile=profile,
                        embedding_model=model_name,
                        created=created,
                    )
                )
            except Exception as exc:
                logger.error("Helix insertion failed for %s: %s", record.url, exc)
                results.append(
                    ScrapeResult(url=record.url, success=False, error=str(exc))
                )

        return ScrapeSummary(results=results)
