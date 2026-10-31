"""Request and response models for versioned API endpoints."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import SchemeLevel
from app.schemas.scheme import Scheme
from app.schemas.user_profile import UserProfile


class IntakeExtractRequest(BaseModel):
    """Payload for POST /api/v1/intake/extract."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Citizen natural language situation description (max 1000 characters).",
    )
    language: str = Field(
        default="en",
        description="Session language ('en' or 'hi').",
    )
    current_profile: UserProfile | None = Field(
        default=None,
        description="Existing ephemeral profile state from browser memory.",
    )


class IntakeExtractResponse(BaseModel):
    """Response returned by POST /api/v1/intake/extract."""

    model_config = ConfigDict(extra="forbid")

    profile_updates: dict[str, Any] = Field(
        default_factory=dict,
        description="Newly detected and normalized profile fields.",
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="Missing fields across candidate 'maybe' schemes.",
    )
    next_question: str | None = Field(
        default=None,
        description="High-impact clarification question in requested language.",
    )
    pii_notice: str | None = Field(
        default=None,
        description="User advisory notice if sensitive PII was detected and stripped.",
    )


class MatchRequest(BaseModel):
    """Payload for POST /api/v1/match."""

    model_config = ConfigDict(extra="forbid")

    profile: UserProfile = Field(
        ...,
        description="Citizen demographic profile evaluated deterministically.",
    )
    language: str = Field(
        default="en",
        description="Requested language for evaluation reasons ('en' or 'hi').",
    )


class SchemeMatchItem(BaseModel):
    """Individual evaluated scheme with deterministic qualification reasons."""

    model_config = ConfigDict(extra="forbid")

    slug: str
    name: str
    name_hi: str
    level: SchemeLevel
    state: str | None = None
    category_tags: list[str] = Field(default_factory=list)
    benefit_summary: str
    benefit_summary_hi: str
    apply_url: str
    source_url: str
    last_verified: datetime
    reasons: list[str] = Field(default_factory=list)
    status: str = Field(description="Qualification status ('eligible', 'maybe', 'not_eligible').")


class MatchResponse(BaseModel):
    """Response returned by POST /api/v1/match."""

    model_config = ConfigDict(extra="forbid")

    eligible: list[SchemeMatchItem] = Field(default_factory=list)
    maybe: list[SchemeMatchItem] = Field(default_factory=list)
    not_eligible: list[SchemeMatchItem] = Field(default_factory=list)


class PaginatedSchemesResponse(BaseModel):
    """Paginated list of verified schemes for GET /api/v1/schemes."""

    model_config = ConfigDict(extra="forbid")

    items: list[Scheme] = Field(default_factory=list)
    total: int = Field(ge=0)
    skip: int = Field(ge=0)
    limit: int = Field(ge=1)


class SchemeAskRequest(BaseModel):
    """Payload for POST /api/v1/schemes/{slug}/ask."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Question regarding official scheme guidelines.",
    )
    language: str = Field(
        default="en",
        description="Requested answer language ('en' or 'hi').",
    )


class SchemeAskResponse(BaseModel):
    """Response returned by POST /api/v1/schemes/{slug}/ask."""

    model_config = ConfigDict(extra="forbid")

    answer: str
    citations: list[str] = Field(default_factory=list)
    answerable: bool = False


class FeedbackResponse(BaseModel):
    """Response returned by POST /api/v1/feedback."""

    model_config = ConfigDict(extra="forbid")

    status: str = "ok"
    id: str | None = None

