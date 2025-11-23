"""Embedding endpoints for the Rizzard AI microservice."""

from fastapi import APIRouter, Depends, HTTPException, status

from ..config import Settings, get_settings
from ..models.schemas import EmbedRequest, EmbedResponse

router = APIRouter(prefix="/embed", tags=["Embedding"])


@router.post("/", response_model=EmbedResponse, status_code=status.HTTP_200_OK)
async def generate_embeddings(
    payload: EmbedRequest,
    settings: Settings = Depends(get_settings),
) -> EmbedResponse:
    """Generate embeddings for the supplied texts.

    The implementation will load a SentenceTransformers model and return normalized
    vector representations for each input string. This stub exists so the endpoint
    is wired into the app before the ML logic is implemented.
    """

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Embedding generation not implemented yet.",
    )
