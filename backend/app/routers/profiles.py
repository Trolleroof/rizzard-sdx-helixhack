"""Profile endpoints for fetching and managing professor profiles."""

from __future__ import annotations

import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..config import Settings, get_settings
from ..models.schemas import ProfileInput, ScoreRequest, ScoreResponse
from ..services.embedding import embed_texts
from ..services.helixdb_service import HelixDBService
from ..services.match import score_profiles as score_profiles_service
from ..services.scrape_orchestrator import ScrapeOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("/search", response_model=ScoreResponse, status_code=status.HTTP_200_OK)
async def search_profiles(
    query: str = Query(..., description="Semantic search query for finding professors"),
    limit: int = Query(20, ge=1, le=100, description="Number of profiles to return"),
    urls: Optional[List[str]] = Query(
        None,
        description="Optional list of profile URLs that should be scraped/refreshed before searching",
    ),
    initialize_schema: bool = Query(
        False,
        description="If true, apply the Helix schema before inserting missing professors",
    ),
    settings: Settings = Depends(get_settings),
) -> ScoreResponse:
    """Search HelixDB for relevant professors, scraping new URLs on-demand."""

    try:
        helix_service = HelixDBService(settings=settings)
    except Exception as exc:  # pragma: no cover - Helix env issues
        logger.error("Unable to initialize Helix service: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="HelixDB connection could not be established. Check configuration.",
        ) from exc

    scrape_summary = None
    if urls:
        try:
            orchestrator = ScrapeOrchestrator(settings=settings, helix_service=helix_service)
            scrape_summary = orchestrator.run(
                urls,
                initialize_schema=initialize_schema,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - network/db failures
            logger.error("Scraping pipeline failure: %s", exc)
            raise HTTPException(
                status_code=502,
                detail="Failed to scrape one or more URLs. Check logs for details.",
            ) from exc

    query_embeddings, _ = embed_texts([query], settings=settings)
    if not query_embeddings:
        return ScoreResponse(results=[])

    search_records = helix_service.search_similar_professors(
        query_embeddings[0],
        limit=limit,
    )
    if not search_records:
        return ScoreResponse(results=[])

    profiles = _records_to_profiles(search_records)
    if not profiles:
        return ScoreResponse(results=[])

    score_request = ScoreRequest(
        user_query=query,
        profiles=profiles,
        rerank_strategy="hybrid",
    )

    response = score_profiles_service(score_request, settings=settings)

    if scrape_summary:
        logger.info(
            "Scraped %s/%s URLs prior to search",
            scrape_summary.success_count,
            scrape_summary.total,
        )

    return response


def _records_to_profiles(records: List[dict]) -> List[ProfileInput]:
    profiles: List[ProfileInput] = []
    for record in records:
        props = record if isinstance(record, dict) else {}
        if not props:
            continue
        keywords = props.get("keywords") or []
        if isinstance(keywords, str):
            keywords = [part.strip() for part in keywords.split(",") if part.strip()]
        elif not isinstance(keywords, list):
            keywords = [str(keywords)]

        profile_id = (
            props.get("profile_id")
            or props.get("id")
            or props.get("_id")
            or props.get("profile_url")
            or str(uuid.uuid4())
        )
        name = props.get("name") or props.get("profile_url") or "Unknown Professor"
        summary = props.get("summary") or ""

        # Extract activity_signals from flattened fields or nested object
        from ..models.schemas import ProfileActivitySignals

        activity_signals = None
        if props.get("activity_signals"):
            signals_data = props.get("activity_signals")
            if isinstance(signals_data, dict):
                activity_signals = ProfileActivitySignals(**signals_data)
            elif isinstance(signals_data, ProfileActivitySignals):
                activity_signals = signals_data
        elif any(
            props.get(key)
            for key in ["recent_publications", "news_mentions", "hiring", "last_updated"]
        ):
            activity_signals = ProfileActivitySignals(
                recent_publications=props.get("recent_publications") or [],
                news_mentions=props.get("news_mentions") or [],
                hiring=props.get("hiring", False),
                last_updated=props.get("last_updated") or "",
            )

        try:
            profile = ProfileInput(
                profile_id=str(profile_id),
                name=str(name),
                title=props.get("title"),
                department=props.get("department"),
                summary=str(summary),
                keywords=[str(keyword) for keyword in keywords if keyword],
                activity_signals=activity_signals,
            )
        except Exception as exc:
            logger.debug("Skipping malformed Helix record %s: %s", props, exc)
            continue
        profiles.append(profile)

    return profiles
