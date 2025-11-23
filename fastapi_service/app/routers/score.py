"""Scoring endpoints for the Rizzard AI microservice."""

from fastapi import APIRouter, Depends, HTTPException, status

from ..config import Settings, get_settings
from ..models.schemas import ScoreRequest, ScoreResponse

router = APIRouter(prefix="/score", tags=["Scoring"])


@router.post("/", response_model=ScoreResponse, status_code=status.HTTP_200_OK)
async def score_profiles(
    payload: ScoreRequest,
    settings: Settings = Depends(get_settings),
) -> ScoreResponse:
    """Calculate semantic, compatibility, and feasibility scores for profiles."""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Scoring pipeline not implemented yet.",
    )
