"""Pydantic models for admin_users authentication and authorization collection."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import AdminRole


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
        description="Bcrypt hashed administrative password.",
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
