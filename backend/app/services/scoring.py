"""Scoring logic for the Rizzard AI microservice."""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

import numpy as np

from ..models.schemas import ProfileInput, ScoreBreakdown

SEMANTIC_WEIGHT = 0.6
COMPATIBILITY_WEIGHT = 0.2
FEASIBILITY_WEIGHT = 0.2


def keyword_overlap_score(query_tokens: Iterable[str], profile_tokens: Iterable[str]) -> float:
    """Compute keyword overlap ratio between query and profile tokens."""
    query_set = {token.lower() for token in query_tokens if token}
    profile_set = {token.lower() for token in profile_tokens if token}

    if not query_set or not profile_set:
        return 0.0

    overlap = query_set.intersection(profile_set)
    return len(overlap) / len(query_set)


def department_diversity_bonus(profile: ProfileInput, seen_departments: set[str]) -> float:
    """Reward profiles from new departments to encourage diversity."""
    department = (profile.department or "").strip().lower()
    if not department:
        return 0.0

    return 0.1 if department not in seen_departments else 0.0


def normalize_scores(scores: List[float]) -> List[float]:
    arr = np.asarray(scores, dtype=np.float32)
    if arr.size == 0:
        return []
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))
    if max_val - min_val < 1e-6:
        return [0.0 for _ in scores]
    return [float((s - min_val) / (max_val - min_val)) for s in scores]


def compute_compatibility_scores(
    query_tokens: Iterable[str],
    profiles: Sequence[ProfileInput],
    profile_keywords: Sequence[Sequence[str]],
) -> Tuple[List[float], List[dict]]:
    raw_scores: List[float] = []
    details: List[dict] = []
    seen_departments: set[str] = set()

    for profile, keywords in zip(profiles, profile_keywords):
        keyword_score = keyword_overlap_score(query_tokens, keywords)
        diversity_bonus = department_diversity_bonus(profile, seen_departments)
        seniority_bonus = 0.0
        if profile.title:
            lowered_title = profile.title.lower()
            if "assistant" in lowered_title or "associate" in lowered_title:
                seniority_bonus = 0.05

        total_score = keyword_score + diversity_bonus + seniority_bonus
        raw_scores.append(total_score)
        details.append(
            {
                "keyword_overlap": keyword_score,
                "department_bonus": diversity_bonus,
                "seniority_bonus": seniority_bonus,
                "raw_score": total_score,
            }
        )

        if profile.department:
            seen_departments.add(profile.department.strip().lower())

    normalized = normalize_scores(raw_scores)
    for detail, norm in zip(details, normalized):
        detail["normalized_score"] = norm

    return normalized, details


def compute_feasibility_scores(profiles: Sequence[ProfileInput]) -> Tuple[List[float], List[dict]]:
    raw_scores: List[float] = []
    details: List[dict] = []
    for profile in profiles:
        signals = profile.activity_signals
        score = signals.recency_score() if signals else 0.5
        raw_scores.append(score)
        details.append(
            {
                "has_activity_signals": bool(signals),
                "raw_score": score,
            }
        )

    normalized = normalize_scores(raw_scores)
    for detail, norm in zip(details, normalized):
        detail["normalized_score"] = norm

    return normalized, details


def aggregate_scores(
    semantic: List[float],
    compatibility: List[float],
    feasibility: List[float],
) -> Tuple[List[ScoreBreakdown], List[float]]:
    breakdowns: List[ScoreBreakdown] = []
    final_scores: List[float] = []

    for s, c, f in zip(semantic, compatibility, feasibility):
        final = (
            SEMANTIC_WEIGHT * s
            + COMPATIBILITY_WEIGHT * c
            + FEASIBILITY_WEIGHT * f
        )
        breakdowns.append(
            ScoreBreakdown(
                semantic=max(0.0, min(1.0, s)),
                compatibility=max(0.0, min(1.0, c)),
                feasibility=max(0.0, min(1.0, f)),
                final_score=max(0.0, min(1.0, final)),
            )
        )
        final_scores.append(max(0.0, min(1.0, final)))

    return breakdowns, final_scores
