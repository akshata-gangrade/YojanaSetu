"""Structured eligibility criteria models for deterministic rule evaluation."""

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.enums import CriterionField, CriterionOperator


class Criterion(BaseModel):
    """Single eligibility condition over a whitelisted profile field."""

    model_config = ConfigDict(extra="forbid")

    field: CriterionField = Field(
        ...,
        description="Profile field to evaluate against.",
    )
    op: CriterionOperator = Field(
        ...,
        description="Deterministic comparison operator.",
    )
    value: Any = Field(
        ...,
        description="Value or range against which the field is tested.",
    )
    as_on: date | None = Field(
        default=None,
        description="Optional cut-off date (YYYY-MM-DD) for age evaluation.",
    )

    @model_validator(mode="after")
    def validate_operator_value_compatibility(self) -> "Criterion":
        """Enforce operator and value type constraints."""
        op = self.op
        val = self.value

        if op == CriterionOperator.BETWEEN:
            if not isinstance(val, list | tuple) or len(val) != 2:
                raise ValueError(
                    "Operator 'between' requires exactly 2 elements [min, max]."
                )
            if not all(isinstance(v, int | float) for v in val):
                raise ValueError("Operator 'between' boundaries must both be numeric.")
            if val[0] > val[1]:
                raise ValueError(
                    f"Invalid 'between' range: {val[0]} exceeds upper bound {val[1]}."
                )

        elif op in (CriterionOperator.IN, CriterionOperator.NOT_IN):
            if not isinstance(val, list | tuple):
                raise ValueError(
                    f"Operator '{op.value}' requires a list or tuple of values."
                )
            if len(val) == 0:
                raise ValueError(
                    f"Operator '{op.value}' list must contain at least one item."
                )

        elif op in (CriterionOperator.GTE, CriterionOperator.LTE):
            if not isinstance(val, int | float):
                raise ValueError(
                    f"Operator '{op.value}' requires a numeric comparison value."
                )

        elif op == CriterionOperator.EQ:
            if isinstance(val, list | dict | set):
                raise ValueError(
                    "Operator 'eq' requires a scalar value (str, int, float, bool)."
                )

        return self


class EligibilityCriteria(BaseModel):
    """Composite rule tree evaluated exclusively by the deterministic rule engine."""

    model_config = ConfigDict(extra="forbid")

    all_of: list[Criterion] = Field(
        default_factory=list,
        description="All criteria in this list must be satisfied.",
    )
    any_of: list[Criterion] = Field(
        default_factory=list,
        description="At least one criterion in list must be satisfied (if non-empty).",
    )
    as_on: date | None = Field(
        default=None,
        description="Optional cut-off date (YYYY-MM-DD) for criteria evaluation.",
    )
