"""API endpoints for professor scraping orchestration."""

from fastapi import APIRouter, Depends, HTTPException, status

from ..config import Settings, get_settings
from ..models.schemas import ScrapeProfessorsRequest, ScrapeProfessorsResponse
from ..services.scrape_orchestrator import ScrapeOrchestrator


router = APIRouter(prefix="/scrape", tags=["Scraping"])


def get_scrape_orchestrator(settings: Settings = Depends(get_settings)) -> ScrapeOrchestrator:
    return ScrapeOrchestrator(settings=settings)


@router.post(
    "/professors",
    response_model=ScrapeProfessorsResponse,
    status_code=status.HTTP_200_OK,
)
async def scrape_professors(
    payload: ScrapeProfessorsRequest,
    orchestrator: ScrapeOrchestrator = Depends(get_scrape_orchestrator),
) -> ScrapeProfessorsResponse:
    if not payload.urls:
        raise HTTPException(status_code=400, detail="At least one URL is required.")

    summary = orchestrator.run(
        payload.urls,
        initialize_schema=payload.initialize_schema,
    )

    return ScrapeProfessorsResponse(**summary.to_dict())

