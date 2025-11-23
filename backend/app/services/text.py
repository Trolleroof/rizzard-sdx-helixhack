"""Text utilities for the Rizzard AI microservice."""

from __future__ import annotations

import re
from typing import Iterable, List, Optional

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_\-]+")


def extract_tokens(text: str) -> List[str]:
    """Extract simple tokens from free-form text."""
    if not text:
        return []
    return [match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)]


def merge_keywords(*keyword_sets: Iterable[str]) -> List[str]:
    seen = set()
    merged: List[str] = []
    for keywords in keyword_sets:
        for keyword in keywords:
            lowered = keyword.lower()
            if lowered not in seen:
                seen.add(lowered)
                merged.append(lowered)
    return merged


def extract_query_keywords(user_query: str, extra_keywords: Optional[Iterable[str]] = None) -> List[str]:
    tokens = extract_tokens(user_query)
    if extra_keywords:
        tokens.extend(keyword.lower() for keyword in extra_keywords if keyword)
    return merge_keywords(tokens)
