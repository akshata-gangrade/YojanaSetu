"""Pydantic models for append-only administrative audit log collection."""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditLogBase(BaseModel):
    """Immutable audit trail event properties."""

    model_config = ConfigDict(extra="forbid")

    actor: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Admin email or system process identifier executing the action.",
    )
    action: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Action performed (e.g. verify_scheme, update_scheme).",
    )
    target: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Entity or resource affected by the action (e.g. scheme slug).",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when event occurred.",
    )
    diff: dict[str, Any] | None = Field(
        default=None,
        description="Structured key-value delta of before and after modifications.",
    )


class AuditLogCreate(AuditLogBase):
    """Schema for appending a new entry to the immutable audit log."""

    pass


class AuditLog(AuditLogBase):
    """Audit log record returned from repository queries."""

    id: str | None = Field(
        default=None,
        description="MongoDB document identifier string.",
    )
