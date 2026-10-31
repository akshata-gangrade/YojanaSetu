"""Ephemeral citizen profile schema used for in-memory eligibility evaluation."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import (
    DisabilityStatus,
    EducationLevel,
    Gender,
    IndianState,
    MaritalStatus,
    Occupation,
    ResidenceType,
    SocialCategory,
)


class UserProfile(BaseModel):
    """Citizen demographic profile received ephemerally per request.

    Invariant: User profiles are NEVER stored or persisted to any database.
    Missing fields or 'prefer_not_to_say' signify an unknown value to the rule engine.
    Sensitive fields (social_category, disability_status) are always optional.
    """

    model_config = ConfigDict(extra="forbid")

    age: int | None = Field(
        default=None,
        ge=0,
        le=125,
        description="Citizen age in completed years.",
    )
    gender: Gender | None = Field(
        default=None,
        description="Gender identity.",
    )
    state: IndianState | None = Field(
        default=None,
        description="Domicile state or Union Territory.",
    )
    annual_income: float | None = Field(
        default=None,
        ge=0.0,
        description="Gross annual household income in INR.",
    )
    social_category: SocialCategory | None = Field(
        default=None,
        description="Social category classification (sensitive, optional).",
    )
    occupation: Occupation | None = Field(
        default=None,
        description="Primary employment or vocational status.",
    )
    education_level: EducationLevel | None = Field(
        default=None,
        description="Highest formal educational qualification completed.",
    )
    residence_type: ResidenceType | None = Field(
        default=None,
        description="Habitation category (rural or urban).",
    )
    marital_status: MaritalStatus | None = Field(
        default=None,
        description="Legal marital status.",
    )
    disability_status: DisabilityStatus | None = Field(
        default=None,
        description="Disability categorization (sensitive, optional).",
    )
    is_student: bool | None = Field(
        default=None,
        description="Whether citizen is currently enrolled in formal education.",
    )

    def is_field_unknown(self, field_name: str) -> bool:
        """Return True if profile field is omitted or set to prefer_not_to_say."""
        if not hasattr(self, field_name):
            return True
        val = getattr(self, field_name)
        if val is None:
            return True
        if hasattr(val, "value") and val.value == "prefer_not_to_say":
            return True
        if val == "prefer_not_to_say":
            return True
        return False

    def get_effective_value(self, field_name: str) -> Any:
        """Return concrete value for evaluation, or None if unknown."""
        if self.is_field_unknown(field_name):
            return None
        val = getattr(self, field_name)
        return val.value if hasattr(val, "value") else val
