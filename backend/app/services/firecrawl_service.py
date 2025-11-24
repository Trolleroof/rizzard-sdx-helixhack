"""Utilities for scraping professor profile pages with Firecrawl."""

from __future__ import annotations

import logging
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

import requests

from ..config import Settings, get_settings
from .text import extract_tokens, merge_keywords

try:  # pragma: no cover - optional dependency during offline development
    from firecrawl import FirecrawlApp
except ImportError:  # pragma: no cover - handled gracefully at runtime
    FirecrawlApp = None


logger = logging.getLogger(__name__)


HEADING_RE = re.compile(r"^#{1,3}\s+(?P<title>[^\n#]+)$", re.MULTILINE)
DEPARTMENT_RE = re.compile(
    r"(?P<label>Department of|Dept\. of|School of)\s+(?P<value>[^\n\r]+)",
    re.IGNORECASE,
)


@dataclass
class ScrapedProfessor:
    """Normalized representation of a scraped professor profile."""

    url: str
    name: str
    department: Optional[str]
    summary: str
    keywords: List[str]
    markdown: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "name": self.name,
            "department": self.department,
            "summary": self.summary,
            "keywords": self.keywords,
            "markdown": self.markdown,
            "metadata": self.metadata,
        }


class FirecrawlService:
    """Wrapper around Firecrawl's API with lightweight extraction helpers."""

    API_BASE = "https://api.firecrawl.dev/v1"

    def __init__(
        self,
        *,
        settings: Optional[Settings] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.settings = settings or get_settings()
        if not self.settings.firecrawl_api_key:
            raise ValueError(
                "FIRECRAWL_API key is missing. Provide it via env or .env file."
            )
        self._session = session or requests.Session()
        self._client = self._initialize_client()

    def _initialize_client(self):  # pragma: no cover - depends on optional library
        if FirecrawlApp is None:
            logger.debug("firecrawl-py not available; using HTTP fallback client")
            return None
        try:
            return FirecrawlApp(api_key=self.settings.firecrawl_api_key)
        except Exception as exc:  # pragma: no cover - safety net
            logger.warning(
                "Unable to initialize FirecrawlApp client (%s). Falling back to HTTP session.",
                exc,
            )
            return None

    def _http_scrape(self, url: str) -> Dict[str, Any]:
        endpoint = f"{self.API_BASE}/scrape"
        payload = {
            "url": url,
            "formats": ["markdown", "metadata"],
        }
        headers = {"Authorization": f"Bearer {self.settings.firecrawl_api_key}"}
        try:
            response = self._session.post(endpoint, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Firecrawl HTTP request failed for {url}: {exc}") from exc

        data = response.json()
        if isinstance(data, dict):
            data.setdefault("url", url)
        return data

    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape a single URL and normalize the payload."""

        if not url:
            raise ValueError("URL must be provided for scraping")

        if self._client is not None:  # pragma: no cover - requires firecrawl service
            scrape_fn = getattr(self._client, "scrape_url", None) or getattr(
                self._client, "scrape", None
            )
            if callable(scrape_fn):
                try:
                    result = scrape_fn(url=url, formats=["markdown", "metadata"])
                    if isinstance(result, dict):
                        result.setdefault("url", url)
                    return result
                except Exception as exc:  # pragma: no cover - best effort safeguard
                    logger.warning(
                        "Firecrawl client scrape failed for %s, retrying via HTTP: %s",
                        url,
                        exc,
                    )

        return self._http_scrape(url)

    def scrape_batch(self, urls: Iterable[str]) -> List[Dict[str, Any]]:
        """Scrape multiple URLs sequentially, logging failures instead of raising."""

        results: List[Dict[str, Any]] = []
        for url in urls:
            try:
                results.append(self.scrape_url(url))
            except Exception as exc:
                logger.error("Failed to scrape %s: %s", url, exc)
                results.append({"url": url, "error": str(exc)})
        return results

    def extract_professor(self, payload: Dict[str, Any]) -> ScrapedProfessor:
        """Convert a Firecrawl payload into a structured professor record."""

        url = payload.get("url", "")
        markdown = payload.get("markdown") or payload.get("markdown_content") or ""
        metadata = payload.get("metadata") or {}

        name = metadata.get("title") or _first_heading(markdown) or url
        summary = metadata.get("description") or _first_paragraph(markdown) or name
        department = _extract_department(markdown)
        keyword_candidates: List[str] = []
        meta_keywords = metadata.get("keywords")
        if isinstance(meta_keywords, str):
            keyword_candidates.extend([k.strip() for k in meta_keywords.split(",") if k.strip()])
        elif isinstance(meta_keywords, list):
            keyword_candidates.extend(str(k) for k in meta_keywords if k)

        keywords = _derive_keywords(markdown, summary, keyword_candidates)

        return ScrapedProfessor(
            url=url,
            name=name.strip() if isinstance(name, str) else str(name),
            department=department.strip() if department else None,
            summary=summary.strip(),
            keywords=keywords,
            markdown=markdown,
            metadata=metadata,
        )


def _first_heading(markdown: str) -> Optional[str]:
    match = HEADING_RE.search(markdown or "")
    if match:
        return match.group("title").strip()
    return None


def _first_paragraph(markdown: str) -> Optional[str]:
    if not markdown:
        return None
    blocks = [block.strip() for block in markdown.split("\n\n")]
    for block in blocks:
        if len(block) >= 40:
            return block.replace("\n", " ")
    return blocks[0] if blocks else None


def _extract_department(markdown: str) -> Optional[str]:
    if not markdown:
        return None
    match = DEPARTMENT_RE.search(markdown)
    if match:
        return match.group("value").strip()
    return None


def _derive_keywords(markdown: str, summary: str, seed: Iterable[str]) -> List[str]:
    tokens = extract_tokens((markdown or "") + " " + (summary or ""))
    freq = Counter(tokens)
    top_tokens = [token for token, _ in freq.most_common(12)]
    return merge_keywords(seed, top_tokens)

