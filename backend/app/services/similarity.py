"""Similarity utilities for the Rizzard AI microservice."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Compute cosine similarity between two vectors."""
    vec_a = np.asarray(a, dtype=np.float32)
    vec_b = np.asarray(b, dtype=np.float32)

    if vec_a.ndim != 1 or vec_b.ndim != 1:
        raise ValueError("cosine_similarity expects 1D vectors")

    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


def cosine_similarity_matrix(
    query: Sequence[Sequence[float]],
    candidates: Sequence[Sequence[float]],
) -> np.ndarray:
    """Compute cosine similarity between query vectors and candidate vectors."""
    if not query or not candidates:
        return np.zeros((len(query), len(candidates)), dtype=np.float32)

    query_matrix = np.asarray(query, dtype=np.float32)
    candidate_matrix = np.asarray(candidates, dtype=np.float32)

    # Normalize if they are not already normalized.
    query_norms = np.linalg.norm(query_matrix, axis=1, keepdims=True)
    candidate_norms = np.linalg.norm(candidate_matrix, axis=1, keepdims=True)

    query_norms[query_norms == 0.0] = 1.0
    candidate_norms[candidate_norms == 0.0] = 1.0

    normalized_query = query_matrix / query_norms
    normalized_candidates = candidate_matrix / candidate_norms

    return normalized_query @ normalized_candidates.T
