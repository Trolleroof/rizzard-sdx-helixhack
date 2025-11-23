"""Email generation endpoints for the Rizzard AI microservice."""

from fastapi import APIRouter, Depends, HTTPException, status

from ..config import Settings, get_settings
from ..models.schemas import EmailRequest, EmailResponse

router = APIRouter(prefix="/email", tags=["Email"])


@router.post("/", response_model=EmailResponse, status_code=status.HTTP_200_OK)
async def generate_email(
    payload: EmailRequest,
    settings: Settings = Depends(get_settings),
) -> EmailResponse:
    """Produce a personalized outreach email for a researcher."""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Email generation not implemented yet.",
    )
