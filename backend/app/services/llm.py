"""LLM utilities for the Rizzard AI microservice."""

from __future__ import annotations

import json
import logging
from typing import Optional

from anthropic import Anthropic
from anthropic._exceptions import AnthropicError

from ..config import Settings
from ..models.schemas import ProfileInput, ScoreBreakdown

logger = logging.getLogger(__name__)


def _get_client(settings: Settings) -> Anthropic:
    if not settings.claude_api_key:
        raise ValueError("Claude API key is not configured. Set CLAUDE_API in the environment.")
    return Anthropic(api_key=settings.claude_api_key)


def _extract_text(response) -> str:
    parts = []
    for block in getattr(response, "content", []) or []:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "".join(parts).strip()


def generate_score_summary(
    *,
    settings: Settings,
    user_query: str,
    profile: ProfileInput,
    scores: ScoreBreakdown,
    rationale: dict,
    max_tokens: int = 250,
) -> Optional[str]:
    """Use Claude to generate a natural language summary of scoring results."""

    try:
        client = _get_client(settings)
    except ValueError as exc:
        logger.warning("Skipping Claude summary generation: %s", exc)
        return None

    payload = {
        "user_query": user_query,
        "profile": {
            "name": profile.name,
            "title": profile.title,
            "department": profile.department,
            "summary": profile.summary,
            "keywords": profile.keywords,
        },
        "scores": {
            "semantic": round(scores.semantic, 4),
            "compatibility": round(scores.compatibility, 4),
            "feasibility": round(scores.feasibility, 4),
            "final_score": round(scores.final_score, 4),
        },
        "rationale": rationale,
    }

    system_prompt = (
        "You are an assistant that writes concise, professional rationales for research "
        "match scoring. Summaries should be one or two sentences, mention the final "
        "score (formatted to two decimal places), highlight the semantic alignment, "
        "and optionally explain compatibility or feasibility factors."
    )

    prompt = (
        "Given the structured data below, produce a short natural-language summary that "
        "explains why the profile earned the indicated scores. Mention the final score "
        "and key supporting details. Do not include bullet points or JSON.\n\n"
        f"Data:\n{json.dumps(payload, indent=2)}\n"
    )

    try:
        response = client.messages.create(
            model=settings.claude_model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )
    except AnthropicError as exc:
        logger.error("Claude API error while generating score summary: %s", exc, exc_info=True)
        return None
    except Exception as exc:  # pragma: no cover - safety net
        logger.error("Unexpected error during Claude summary generation: %s", exc, exc_info=True)
        return None

    text = _extract_text(response)
    return text or None
