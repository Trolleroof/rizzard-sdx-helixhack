"""Embedding utilities for the Rizzard AI microservice."""

from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from ..config import Settings, get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_model(model_name: str) -> SentenceTransformer:
    """Return a cached SentenceTransformer instance."""
    logger.info("Loading SentenceTransformer model: %s", model_name)
    return SentenceTransformer(model_name)


def normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
    """L2 normalize embeddings along the last axis."""
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return embeddings / norms


def embed_texts(
    texts: list[str],
    *,
    normalize: bool = True,
    settings: Settings | None = None,
) -> tuple[list[list[float]], str]:
    """Generate embeddings for the provided texts.

    Returns a tuple of embedding vectors and the model name used.
    """
    if not texts:
        return [], (settings.embedding_model_name if settings else "")

    app_settings = settings or get_settings()
    model = get_model(app_settings.embedding_model_name)

    embeddings = model.encode(texts, convert_to_numpy=True)

    if normalize:
        embeddings = normalize_embeddings(embeddings)

    return embeddings.tolist(), app_settings.embedding_model_name
