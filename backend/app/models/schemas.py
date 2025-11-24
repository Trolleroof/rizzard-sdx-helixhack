"""Pydantic models defining the API contract for the AI microservice."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class EmbedRequest(BaseModel):
    """Request payload for generating embeddings."""

    texts: list[str] = Field(..., description="Text inputs to embed")
    normalize: bool = Field(True, description="Whether to L2-normalize the embeddings")


class EmbedResponse(BaseModel):
    """Response payload containing generated embeddings."""

    embeddings: list[list[float]] = Field(..., description="Embedding vectors matching the order of input texts")
    model: str = Field(..., description="Identifier of the embedding model used")


class ProfileActivitySignals(BaseModel):
    """Structured activity indicators extracted from scrapers."""

    recent_publications: Optional[list[str]] = None
    news_mentions: Optional[list[str]] = None
    hiring: Optional[bool] = None
    last_updated: Optional[str] = Field(
        None, description="ISO timestamp of the latest profile update if available"
    )

    def recency_score(self) -> float:
        """Heuristic readiness score based on available signals (0-1)."""
        score = 0.0
        weights = {
            "recent_publications": 0.4,
            "news_mentions": 0.3,
            "hiring": 0.2,
            "last_updated": 0.1,
        }

        if self.recent_publications:
            score += weights["recent_publications"]
        if self.news_mentions:
            score += weights["news_mentions"]
        if self.hiring:
            score += weights["hiring"]
        if self.last_updated:
            score += weights["last_updated"]

        return min(score, 1.0)


class ProfileInput(BaseModel):
    """Minimal profile representation received from the Node orchestrator."""

    profile_id: str = Field(..., description="Unique identifier for the researcher profile")
    name: str = Field(..., description="Researcher full name")
    title: Optional[str] = Field(None, description="Academic title or role")
    department: Optional[str] = Field(None, description="Department affiliation")
    summary: str = Field(..., description="Free-form summary text of the research focus")
    keywords: list[str] = Field(default_factory=list, description="Key topics or methods")
    activity_signals: Optional[ProfileActivitySignals] = None


class ScoreBreakdown(BaseModel):
    """Breakdown of the match scoring components."""

    semantic: float = Field(..., ge=0.0, le=1.0)
    compatibility: float = Field(..., ge=0.0, le=1.0)
    feasibility: float = Field(..., ge=0.0, le=1.0)
    final_score: float = Field(..., ge=0.0, le=1.0)


class ScoreResult(BaseModel):
    """Score output for a single profile."""

    profile: ProfileInput
    scores: ScoreBreakdown
    rationale: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional structured rationale explaining the score components",
    )
    summary_text: Optional[str] = Field(
        None,
        description="Natural-language summary of the match score and rationale",
    )


class ScoreRequest(BaseModel):
    """Request payload for match scoring."""

    user_query: str = Field(..., description="Original user intent text")
    profiles: list[ProfileInput] = Field(..., description="Profiles to evaluate")
    rerank_strategy: Literal["semantic", "hybrid"] = Field(
        "hybrid", description="Optional rerank hint for the scoring pipeline"
    )


class ScoreResponse(BaseModel):
    """Response payload containing match results."""

    results: list[ScoreResult]


class EmailRequest(BaseModel):
    """Request payload for email generation."""

    profile: ProfileInput
    user_background: str = Field(..., description="Information about the student or sender")
    tone: Literal["friendly", "formal", "enthusiastic"] = Field(
        "friendly", description="Desired tone of the outreach email"
    )


class EmailResponse(BaseModel):
    """Generated cold outreach email."""

    subject: str
    body: str


class ProjectRequest(BaseModel):
    """Request payload for project idea generation."""

    profile: ProfileInput
    user_skills: list[str] = Field(..., description="Skills the user brings to the collaboration")
    collaboration_horizon: Literal["short", "medium", "long"] = Field(
        "medium", description="Expected timeframe for the potential collaboration"
    )


class ProjectIdea(BaseModel):
    """Represents a single proposed collaboration idea."""

    title: str
    description: str
    expected_outcomes: list[str] = Field(default_factory=list)


class ProjectResponse(BaseModel):
    """Generated project ideas tailored to the user and profile."""

    ideas: list[ProjectIdea]


class ProcessProfileRequest(BaseModel):
    """Request payload for profile normalization and enrichment."""

    profile: ProfileInput


class ProcessedProfile(BaseModel):
    """Structured profile returned after NLP processing."""

    profile: ProfileInput
    extracted_methods: list[str] = Field(default_factory=list)
    extracted_topics: list[str] = Field(default_factory=list)
    research_summary: Optional[str] = None
    love_languages: list[str] = Field(
        default_factory=list,
        description="Communication or collaboration preferences inferred from the profile",
    )


class ProcessProfileResponse(BaseModel):
    """Response containing enriched profile data."""

    processed: ProcessedProfile


class ScrapeProfessorsRequest(BaseModel):
    """Request payload for orchestrated professor scraping."""

    urls: list[str] = Field(..., description="Professor profile URLs to scrape")
    initialize_schema: bool = Field(
        False,
        description="Whether to attempt applying the Helix schema before scraping",
    )


class ScrapeProfessorResult(BaseModel):
    """Outcome for a single scraped professor URL."""

    url: str
    success: bool
    helix_id: Optional[str] = None
    error: Optional[str] = None
    profile: Optional[ProfileInput] = None
    embedding_model: Optional[str] = None


class ScrapeProfessorsResponse(BaseModel):
    """Aggregate response for a scrape batch."""

    total: int
    success_count: int
    failure_count: int
    results: list[ScrapeProfessorResult]
