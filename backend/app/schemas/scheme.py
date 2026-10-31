"""Pydantic models for schemes collection."""

from datetime import UTC, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.schemas.criteria import EligibilityCriteria
from app.schemas.enums import SchemeLevel, SchemeStatus


class SchemeBase(BaseModel):
    """Base scheme properties shared between creation, persistence, and responses."""

    model_config = ConfigDict(extra="forbid")

    slug: str = Field(
        ...,
        min_length=3,
        max_length=120,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="Unique URL-friendly scheme slug.",
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Scheme title in English.",
    )
    name_hi: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Scheme title in Hindi (Devanagari).",
    )
    level: SchemeLevel = Field(
        ...,
        description="Administrative level (central or state).",
    )
    state: str | None = Field(
        default=None,
        description="Target Indian State (null for central schemes).",
    )
    category_tags: list[str] = Field(
        default_factory=list,
        description="Category classification tags.",
    )
    benefit_summary: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Summary of financial or in-kind benefits in English.",
    )
    benefit_summary_hi: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Summary of benefits in Hindi.",
    )
    eligibility_criteria: EligibilityCriteria = Field(
        default_factory=EligibilityCriteria,
        description="Structured criteria evaluated deterministically.",
    )
    required_documents: list[str] = Field(
        default_factory=list,
        description="Mandatory and supporting application documents.",
    )
    application_steps: list[str] = Field(
        default_factory=list,
        description="Sequential instructions to apply.",
    )
    apply_url: str = Field(
        ...,
        description="Direct link to official application portal.",
    )
    source_url: str = Field(
        ...,
        description="Official ministry source link.",
    )
    source_hash: str = Field(
        ...,
        min_length=16,
        description="Cryptographic SHA-256 hash of official source document.",
    )
    status: SchemeStatus = Field(
        default=SchemeStatus.DRAFT,
        description="Verification lifecycle status.",
    )
    verified_by: str | None = Field(
        default=None,
        description="Admin username or ID who verified against official source.",
    )
    verified_at: datetime | None = Field(
        default=None,
        description="Timestamp of administrator verification.",
    )
    last_verified: datetime = Field(
        ...,
        description="Timestamp indicating when source validity was last confirmed.",
    )
    is_sample: bool = Field(
        default=False,
        description="Fictional test data excluded from production.",
    )

    @field_validator("apply_url", "source_url")
    @classmethod
    def validate_urls(cls, v: str) -> str:
        """Validate URL protocol strictly (must be http or https)."""
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @model_validator(mode="after")
    def validate_level_and_state(self) -> "SchemeBase":
        """Enforce level-state relationship invariants."""
        if self.level == SchemeLevel.CENTRAL and self.state is not None:
            raise ValueError("Central schemes must have state set to None.")
        if self.level == SchemeLevel.STATE and not self.state:
            raise ValueError("State schemes must have a specified state.")
        return self


class SchemeCreate(SchemeBase):
    """Schema for inserting a new scheme into the database."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SchemeUpdate(BaseModel):
    """Schema for updating an existing scheme. Extra fields strictly forbidden."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=2, max_length=255)
    name_hi: str | None = Field(default=None, min_length=2, max_length=255)
    level: SchemeLevel | None = None
    state: str | None = None
    category_tags: list[str] | None = None
    benefit_summary: str | None = Field(default=None, min_length=10, max_length=2000)
    benefit_summary_hi: str | None = Field(default=None, min_length=10, max_length=2000)
    eligibility_criteria: EligibilityCriteria | None = None
    required_documents: list[str] | None = None
    application_steps: list[str] | None = None
    apply_url: str | None = None
    source_url: str | None = None
    source_hash: str | None = None
    status: SchemeStatus | None = None
    verified_by: str | None = None
    verified_at: datetime | None = None
    last_verified: datetime | None = None
    is_sample: bool | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Scheme(SchemeBase):
    """Public scheme representation returned by repository queries and APIs."""

    id: str | None = Field(
        default=None,
        description="MongoDB document identifier string.",
    )
    created_at: datetime
    updated_at: datetime
