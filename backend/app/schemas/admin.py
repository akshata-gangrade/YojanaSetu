"""Pydantic models for admin_users authentication and authorization collection."""

from datetime import UTC, datetime
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.audit import AuditLog
from app.schemas.criteria import EligibilityCriteria
from app.schemas.enums import AdminRole, SchemeLevel, SchemeStatus
from app.schemas.scheme import Scheme


def validate_gov_nic_url(url: str) -> str:
    """Validate that a URL strictly uses HTTPS and resolves to an official .gov.in or .nic.in host."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("URL must use HTTPS protocol.")
    host = (parsed.hostname or "").lower()
    if not (
        host.endswith(".gov.in")
        or host.endswith(".nic.in")
        or host in ("gov.in", "nic.in")
    ):
        raise ValueError("URL host must be on a .gov.in or .nic.in domain.")
    return url


class AdminUserBase(BaseModel):
    """Core administrative user attributes."""

    model_config = ConfigDict(extra="forbid")

    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="Unique verified administrative user email.",
    )
    role: AdminRole = Field(
        default=AdminRole.REVIEWER,
        description="Authorization role for administrative actions.",
    )


class AdminUserCreate(AdminUserBase):
    """Schema for provisioning a new administrator account."""

    password_hash: str = Field(
        ...,
        min_length=20,
        description="Argon2id hashed administrative password.",
    )
    failed_logins: int = Field(
        default=0,
        ge=0,
        description="Consecutive failed authentication attempts.",
    )
    locked_until: datetime | None = Field(
        default=None,
        description="Account lockout timestamp after repeated authentication failures.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Account creation timestamp.",
    )


class AdminUserInDB(AdminUserCreate):
    """Database model including MongoDB document identifier."""

    id: str | None = Field(
        default=None, description="MongoDB document identifier string."
    )


class AdminUser(AdminUserBase):
    """Public administrator representation omitting security credentials."""

    id: str | None = Field(
        default=None, description="MongoDB document identifier string."
    )
    failed_logins: int
    locked_until: datetime | None
    created_at: datetime


class AdminLoginRequest(BaseModel):
    """Administrative login credentials payload."""

    model_config = ConfigDict(extra="forbid")

    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=256)


class AdminTokenResponse(BaseModel):
    """Administrative authentication response with JWT access token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    role: AdminRole


class AdminSchemeCreate(BaseModel):
    """Schema for administrative scheme creation.

    Invariants:
    - Always saved as needs_review.
    - Criteria deterministically validated against EligibilityCriteria model.
    - apply_url and source_url strictly require HTTPS and a .gov.in or .nic.in host.
    """

    model_config = ConfigDict(extra="forbid")

    slug: str = Field(
        ...,
        min_length=3,
        max_length=120,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="Unique URL-friendly scheme slug.",
    )
    name: str = Field(..., min_length=2, max_length=255)
    name_hi: str = Field(..., min_length=2, max_length=255)
    level: SchemeLevel
    state: str | None = None
    category_tags: list[str] = Field(default_factory=list)
    benefit_summary: str = Field(..., min_length=10, max_length=2000)
    benefit_summary_hi: str = Field(..., min_length=10, max_length=2000)
    eligibility_criteria: EligibilityCriteria = Field(default_factory=EligibilityCriteria)
    required_documents: list[str] = Field(default_factory=list)
    application_steps: list[str] = Field(default_factory=list)
    apply_url: str = Field(...)
    source_url: str = Field(...)
    source_hash: str = Field(..., min_length=16)
    last_verified: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_sample: bool = False

    @field_validator("apply_url", "source_url")
    @classmethod
    def check_urls(cls, v: str) -> str:
        return validate_gov_nic_url(v)

    @model_validator(mode="after")
    def validate_level_and_state(self) -> "AdminSchemeCreate":
        if self.level == SchemeLevel.CENTRAL and self.state is not None:
            raise ValueError("Central schemes must have state set to None.")
        if self.level == SchemeLevel.STATE and not self.state:
            raise ValueError("State schemes must have a specified state.")
        return self


class AdminSchemeUpdate(BaseModel):
    """Schema for administrative scheme editing.

    Invariants:
    - Any edit to a verified scheme resets it to needs_review.
    - apply_url and source_url strictly require HTTPS and a .gov.in or .nic.in host if provided.
    """

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
    last_verified: datetime | None = None
    is_sample: bool | None = None

    @field_validator("apply_url", "source_url")
    @classmethod
    def check_urls(cls, v: str | None) -> str | None:
        if v is not None:
            return validate_gov_nic_url(v)
        return v


class AdminVerifyRequest(BaseModel):
    """Payload for scheme verification."""

    model_config = ConfigDict(extra="forbid")

    source_url: str | None = None
    last_verified: datetime | None = None

    @field_validator("source_url")
    @classmethod
    def check_url(cls, v: str | None) -> str | None:
        if v is not None:
            return validate_gov_nic_url(v)
        return v


class AdminRejectRequest(BaseModel):
    """Payload for rejecting a scheme with mandatory reason."""

    model_config = ConfigDict(extra="forbid")

    reason: str = Field(..., min_length=3, max_length=1000)


class AdminSchemeListResponse(BaseModel):
    """Paginated administrative schemes list."""

    items: list[Scheme]
    total: int
    skip: int
    limit: int


class AuditLogListResponse(BaseModel):
    """Paginated administrative audit logs list."""

    items: list[AuditLog]
    total: int
    skip: int
    limit: int
