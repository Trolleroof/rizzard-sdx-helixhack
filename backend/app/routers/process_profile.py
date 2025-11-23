"""Profile processing endpoints for the Rizzard AI microservice."""

from fastapi import APIRouter, Depends, HTTPException, status

from ..config import Settings, get_settings
from ..models.schemas import ProcessProfileRequest, ProcessProfileResponse

router = APIRouter(prefix="/process-profile", tags=["Profile Processing"])


@router.post("/", response_model=ProcessProfileResponse, status_code=status.HTTP_200_OK)
async def process_profile(
    payload: ProcessProfileRequest,
    settings: Settings = Depends(get_settings),
) -> ProcessProfileResponse:
    """Clean and enrich a scraped profile prior to scoring."""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Profile processing not implemented yet.",
    )
