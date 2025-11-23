"""Scoring endpoints for the Rizzard AI microservice."""

from fastapi import APIRouter, Depends, status

from ..config import Settings, get_settings
from ..models.schemas import ScoreRequest, ScoreResponse
from ..services.match import score_profiles as score_profiles_service

router = APIRouter(prefix="/score", tags=["Scoring"])


@router.post("/", response_model=ScoreResponse, status_code=status.HTTP_200_OK)
async def score_profiles(
    payload: ScoreRequest,
    settings: Settings = Depends(get_settings),
) -> ScoreResponse:
    """Calculate semantic, compatibility, and feasibility scores for profiles."""

    return score_profiles_service(payload, settings=settings)
