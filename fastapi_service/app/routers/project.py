"""Project idea generation endpoints for the Rizzard AI microservice."""

from fastapi import APIRouter, Depends, HTTPException, status

from ..config import Settings, get_settings
from ..models.schemas import ProjectRequest, ProjectResponse

router = APIRouter(prefix="/project", tags=["Project Ideas"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
async def generate_project_ideas(
    payload: ProjectRequest,
    settings: Settings = Depends(get_settings),
) -> ProjectResponse:
    """Generate collaboration project ideas tailored to the user and profile."""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Project idea generation not implemented yet.",
    )
