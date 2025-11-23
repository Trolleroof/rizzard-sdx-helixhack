"""Match scoring orchestration for the Rizzard AI microservice."""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from ..config import Settings, get_settings
from ..models.schemas import ProfileInput, ScoreRequest, ScoreResponse, ScoreResult
from .embedding import embed_texts
from .scoring import (
    aggregate_scores,
    compute_compatibility_scores,
    compute_feasibility_scores,
)
from .similarity import cosine_similarity_matrix
from .text import extract_query_keywords, extract_tokens, merge_keywords


def _build_profile_text(profile: ProfileInput) -> str:
    parts: List[str] = []
    if profile.summary:
        parts.append(profile.summary)
    if profile.keywords:
        parts.append(" ".join(profile.keywords))
    if profile.department:
        parts.append(profile.department)
    if profile.title:
        parts.append(profile.title)
    return " ".join(parts)


def _profile_tokens(profile: ProfileInput) -> List[str]:
    tokens = list(profile.keywords)
    tokens.extend(extract_tokens(profile.summary))
    if profile.department:
        tokens.extend(extract_tokens(profile.department))
    return merge_keywords(tokens)


def _prepare_embeddings(
    user_query: str,
    profiles: Sequence[ProfileInput],
    settings: Optional[Settings] = None,
) -> Tuple[List[float], List[List[float]], str]:
    app_settings = settings or get_settings()

    profile_texts = [_build_profile_text(profile) for profile in profiles]
    profile_embeddings, model_name = embed_texts(
        profile_texts,
        normalize=True,
        settings=app_settings,
    )

    query_embeddings, _ = embed_texts(
        [user_query],
        normalize=True,
        settings=app_settings,
    )

    query_embedding = query_embeddings[0] if query_embeddings else []

    return query_embedding, profile_embeddings, model_name


def score_profiles(
    payload: ScoreRequest,
    *,
    settings: Optional[Settings] = None,
) -> ScoreResponse:
    profiles = payload.profiles
    if not profiles:
        return ScoreResponse(results=[])

    app_settings = settings or get_settings()

    query_tokens = extract_query_keywords(payload.user_query)
    profile_keyword_sets = [_profile_tokens(profile) for profile in profiles]

    query_embedding, profile_embeddings, model_name = _prepare_embeddings(
        payload.user_query,
        profiles,
        settings=app_settings,
    )

    if not query_embedding or not profile_embeddings:
        semantic_scores = [0.0 for _ in profiles]
    else:
        similarity_matrix = cosine_similarity_matrix([query_embedding], profile_embeddings)
        semantic_scores = similarity_matrix[0].tolist()

    compatibility_scores, compatibility_details = compute_compatibility_scores(
        query_tokens,
        profiles,
        profile_keyword_sets,
    )

    feasibility_scores, feasibility_details = compute_feasibility_scores(profiles)

    breakdowns, _ = aggregate_scores(
        semantic_scores,
        compatibility_scores,
        feasibility_scores,
    )

    results: List[ScoreResult] = []
    for profile, breakdown, comp_detail, feas_detail, semantic in zip(
        profiles,
        breakdowns,
        compatibility_details,
        feasibility_details,
        semantic_scores,
    ):
        rationale: Dict[str, object] = {
            "semantic_score": semantic,
            "compatibility_details": comp_detail,
            "feasibility_details": feas_detail,
            "embedding_model": model_name,
        }
        results.append(
            ScoreResult(
                profile=profile,
                scores=breakdown,
                rationale=rationale,
            )
        )

    return ScoreResponse(results=results)
