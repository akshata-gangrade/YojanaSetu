"""Follow-up question selector to resolve citizen eligibility ambiguity.

Product rules:
- Pure Python. No LLM, no database, no network, no randomness.
- Given the profile and all candidate "maybe" schemes, return the single missing
  field that appears in the most candidates (ties broken by fixed priority order),
  plus a plain-language question for it, in English and Hindi.
"""

from collections import Counter
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.enums import CriterionField
from app.schemas.scheme import Scheme, SchemeBase
from app.schemas.user_profile import UserProfile
from app.services.rule_engine import (
    EligibilityResult,
    EligibilityStatus,
    RuleEngineService,
)

# Fixed deterministic priority order for tie-breaking
FIELD_PRIORITY_ORDER: list[str] = [
    CriterionField.AGE.value,
    CriterionField.ANNUAL_INCOME.value,
    CriterionField.STATE.value,
    CriterionField.GENDER.value,
    CriterionField.OCCUPATION.value,
    CriterionField.SOCIAL_CATEGORY.value,
    CriterionField.RESIDENCE_TYPE.value,
    CriterionField.EDUCATION_LEVEL.value,
    CriterionField.MARITAL_STATUS.value,
    CriterionField.DISABILITY_STATUS.value,
    CriterionField.IS_STUDENT.value,
]

# Plain-language question templates in English and Hindi
FIELD_QUESTIONS: dict[str, tuple[str, str]] = {
    CriterionField.AGE.value: (
        "What is your age in completed years?",
        "आपकी उम्र (वर्षों में) कितनी है?",
    ),
    CriterionField.ANNUAL_INCOME.value: (
        "What is your total annual household income in INR?",
        "आपके परिवार की कुल वार्षिक आय (रुपये में) कितनी है?",
    ),
    CriterionField.STATE.value: (
        "Which state or Union Territory do you currently reside in?",
        "आप वर्तमान में किस राज्य या केंद्र शासित प्रदेश में रहते हैं?",
    ),
    CriterionField.GENDER.value: (
        "What is your gender?",
        "आपका लिंग क्या है?",
    ),
    CriterionField.OCCUPATION.value: (
        "What is your primary occupation or source of livelihood?",
        "आपका मुख्य व्यवसाय या आजीविका का साधन क्या है?",
    ),
    CriterionField.SOCIAL_CATEGORY.value: (
        "Which social category do you belong to (General, OBC, SC, ST, EBC)?",
        "आप किस सामाजिक श्रेणी से संबंधित हैं (सामान्य, ओबीसी, एससी, एसटी, ईबीसी)?",
    ),
    CriterionField.RESIDENCE_TYPE.value: (
        "Do you reside in a rural area or an urban area?",
        "क्या आप ग्रामीण क्षेत्र में रहते हैं या शहरी क्षेत्र में?",
    ),
    CriterionField.EDUCATION_LEVEL.value: (
        "What is your highest level of completed education?",
        "आपकी उच्चतम पूर्ण शिक्षा का स्तर क्या है?",
    ),
    CriterionField.MARITAL_STATUS.value: (
        "What is your marital status?",
        "आपकी वैवाहिक स्थिति क्या है?",
    ),
    CriterionField.DISABILITY_STATUS.value: (
        "Do you have any disability (if comfortable sharing)?",
        "क्या आपको कोई दिव्यांगता है (यदि साझा करना चाहें)?",
    ),
    CriterionField.IS_STUDENT.value: (
        "Are you currently enrolled as a student in an educational institution?",
        "क्या आप वर्तमान में किसी शैक्षणिक संस्थान में छात्र हैं?",
    ),
}


class FollowupQuestion(BaseModel):
    """Structured follow-up query presented to citizen in conversational intake."""

    field: str = Field(..., description="Target missing profile attribute.")
    count: int = Field(
        ...,
        ge=1,
        description="Number of candidate 'maybe' schemes asking for this attribute.",
    )
    question_en: str = Field(..., description="Plain-language question in English.")
    question_hi: str = Field(..., description="Plain-language question in Hindi.")


class FollowupSelectorService:
    """Calculates missing profile parameters that maximize qualification clarity.

    Pure Python, deterministic, zero network, zero LLM.
    """

    def __init__(self, rule_engine: RuleEngineService | None = None) -> None:
        self._engine = rule_engine or RuleEngineService()

    def get_question_for_field(self, field: str) -> tuple[str, str]:
        """Return (question_en, question_hi) for a given profile field."""
        if field in FIELD_QUESTIONS:
            return FIELD_QUESTIONS[field]
        field_fmt = field.replace("_", " ")
        return (
            f"Please provide your {field_fmt}.",
            f"कृपया अपना {field_fmt} प्रदान करें।",
        )

    def select_followup(
        self,
        profile: UserProfile | dict[str, Any],
        candidate_schemes: Sequence[Any],
    ) -> FollowupQuestion | None:
        """Select highest-impact missing profile field across candidate 'maybe' schemes.

        Args:
            profile: Citizen UserProfile or dict.
            candidate_schemes: Sequence of Scheme, EligibilityResult, tuple, or dict.

        Returns:
            FollowupQuestion if candidate schemes have unresolved missing fields.
        """
        if not candidate_schemes:
            return None

        if isinstance(profile, dict):
            profile = UserProfile.model_validate(profile)

        missing_field_occurrences: list[str] = []

        for item in candidate_schemes:
            item_result: EligibilityResult | None = None

            if isinstance(item, tuple) and len(item) == 2:
                # tuple of (scheme, result)
                _, res = item
                if isinstance(res, EligibilityResult):
                    item_result = res
            elif isinstance(item, EligibilityResult):
                item_result = item
            elif isinstance(item, Scheme | SchemeBase | dict):
                # Scheme requiring evaluation
                item_result = self._engine.evaluate_scheme(profile, item)

            if item_result is not None:
                # Candidate "maybe" schemes are ambiguous and benefit from follow-up
                if item_result.status == EligibilityStatus.MAYBE:
                    # Collect missing fields that user profile has not answered yet
                    for f in item_result.missing_fields:
                        if profile.is_field_unknown(f):
                            missing_field_occurrences.append(f)

        if not missing_field_occurrences:
            return None

        # Count frequencies
        counts = Counter(missing_field_occurrences)

        # Sort by (-frequency, priority_order_index, field_name)
        def sort_key(field_name: str) -> tuple[int, int, str]:
            freq = counts[field_name]
            try:
                p_idx = FIELD_PRIORITY_ORDER.index(field_name)
            except ValueError:
                p_idx = 999
            return (-freq, p_idx, field_name)

        sorted_fields = sorted(counts.keys(), key=sort_key)
        best_field = sorted_fields[0]
        best_count = counts[best_field]

        q_en, q_hi = self.get_question_for_field(best_field)

        return FollowupQuestion(
            field=best_field,
            count=best_count,
            question_en=q_en,
            question_hi=q_hi,
        )

    def select_missing_field(
        self,
        profile: UserProfile | dict[str, Any],
        candidate_schemes: Sequence[Any],
    ) -> str | None:
        """Convenience method returning top missing field name, or None."""
        res = self.select_followup(profile, candidate_schemes)
        return res.field if res is not None else None
