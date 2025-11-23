"""Embedding endpoints for the Rizzard AI microservice."""

from fastapi import APIRouter, Depends, status

from ..config import Settings, get_settings
from ..models.schemas import EmbedRequest, EmbedResponse
from ..services.embedding import embed_texts

router = APIRouter(prefix="/embed", tags=["Embedding"])


@router.post("", response_model=EmbedResponse, status_code=status.HTTP_200_OK)
async def generate_embeddings(
    payload: EmbedRequest,
    settings: Settings = Depends(get_settings),
) -> EmbedResponse:
    """Generate embeddings for the supplied texts.

    The implementation will load a SentenceTransformers model and return normalized
    vector representations for each input string. This stub exists so the endpoint
    is wired into the app before the ML logic is implemented.
    """

    embeddings, model_name = embed_texts(
        payload.texts,
        normalize=payload.normalize,
        settings=settings,
    )

    return EmbedResponse(embeddings=embeddings, model=model_name)
