"""Pydantic models defining the API contract for the AI microservice."""

from __future__ import annotations

from typing import Any, Literal

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

    recent_publications: list[str] | None = None
    news_mentions: list[str] | None = None
    hiring: bool | None = None
    last_updated: str | None = Field(
        None, description="ISO timestamp of the latest profile update if available"
    )


class ProfileInput(BaseModel):
    """Minimal profile representation received from the Node orchestrator."""

    profile_id: str = Field(..., description="Unique identifier for the researcher profile")
    name: str = Field(..., description="Researcher full name")
    title: str | None = Field(None, description="Academic title or role")
    department: str | None = Field(None, description="Department affiliation")
    summary: str = Field(..., description="Free-form summary text of the research focus")
    keywords: list[str] = Field(default_factory=list, description="Key topics or methods")
    activity_signals: ProfileActivitySignals | None = None


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
    research_summary: str | None = None
    love_languages: list[str] = Field(
        default_factory=list,
        description="Communication or collaboration preferences inferred from the profile",
    )


class ProcessProfileResponse(BaseModel):
    """Response containing enriched profile data."""

    processed: ProcessedProfile


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""

    role: Literal["user", "assistant"] = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """Request payload for chat endpoint."""

    messages: list[ChatMessage] = Field(..., description="Conversation history")


class ChatResponse(BaseModel):
    """Response payload for chat endpoint (non-streaming)."""

    message: ChatMessage = Field(..., description="Assistant's response message")
