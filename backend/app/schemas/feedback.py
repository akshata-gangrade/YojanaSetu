"""Pydantic models for anonymous scheme feedback collection."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import FeedbackVote


class FeedbackBase(BaseModel):
    """Anonymous citizen feedback without any user identifiers."""

    model_config = ConfigDict(extra="forbid")

    scheme_id: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Scheme slug or identifier the feedback applies to.",
    )
    vote: FeedbackVote = Field(
        ...,
        description="Anonymous sentiment vote (helpful or not_helpful).",
    )
    comment: str | None = Field(
        default=None,
        max_length=500,
        description="Optional anonymous textual feedback note.",
    )


class FeedbackCreate(FeedbackBase):
    """Schema for submitting feedback."""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Feedback submission timestamp indexed with a 90-day TTL.",
    )


class Feedback(FeedbackBase):
    """Feedback document returned from repository queries."""

    id: str | None = Field(
        default=None,
        description="MongoDB document identifier string.",
    )
    created_at: datetime
