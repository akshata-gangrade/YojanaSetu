"""Deterministic Python rule engine for citizen scheme eligibility.

Product rule: The LLM extracts information and writes explanations.
It NEVER decides eligibility. Eligibility is decided ONLY by this rule engine.
Pure Python: No LLM, no database, no network, no randomness.
"""

from collections.abc import Sequence
from datetime import date, timedelta
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.schemas.criteria import Criterion, EligibilityCriteria
from app.schemas.enums import (
    CriterionField,
    CriterionOperator,
    SchemeLevel,
)
from app.schemas.scheme import Scheme, SchemeBase
from app.schemas.user_profile import UserProfile


class EligibilityStatus(str, Enum):
    """Deterministic eligibility status for a scheme evaluation."""

    ELIGIBLE = "eligible"
    MAYBE = "maybe"
    NOT_ELIGIBLE = "not_eligible"


class ThreeValuedLogic(str, Enum):
    """Three-valued logic state for criteria conditions."""

    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


class ConditionDetail(BaseModel):
    """Detailed deterministic outcome of a single criterion condition."""

    field: str = Field(..., description="Target profile field.")
    op: str = Field(..., description="Operator evaluated.")
    expected: Any = Field(..., description="Condition expected value or boundary.")
    actual: Any = Field(default=None, description="Citizen actual value.")
    status: ThreeValuedLogic = Field(..., description="Three-valued result.")
    reason_en: str = Field(..., description="Human-readable reason in English.")
    reason_hi: str = Field(..., description="Human-readable reason in Hindi.")


class EligibilityResult(BaseModel):
    """Deterministic result of evaluating a citizen profile against scheme criteria."""

    status: EligibilityStatus = Field(..., description="Overall qualification status.")
    passed_conditions: list[str] = Field(
        default_factory=list,
        description="List of human-readable passed conditions in requested language.",
    )
    failed_conditions: list[str] = Field(
        default_factory=list,
        description="List of human-readable failed conditions in requested language.",
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description="List of unknown or omitted profile fields required for certainty.",
    )
    passed_conditions_en: list[str] = Field(
        default_factory=list, description="Passed conditions in English."
    )
    passed_conditions_hi: list[str] = Field(
        default_factory=list, description="Passed conditions in Hindi."
    )
    failed_conditions_en: list[str] = Field(
        default_factory=list, description="Failed conditions in English."
    )
    failed_conditions_hi: list[str] = Field(
        default_factory=list, description="Failed conditions in Hindi."
    )
    details: list[ConditionDetail] = Field(
        default_factory=list, description="Full structured condition details."
    )


# Human-readable labels for fields
FIELD_LABELS: dict[str, tuple[str, str]] = {
    CriterionField.AGE.value: ("Age", "आयु"),
    CriterionField.GENDER.value: ("Gender", "लिंग"),
    CriterionField.STATE.value: ("State", "राज्य"),
    CriterionField.ANNUAL_INCOME.value: ("Annual income", "वार्षिक आय"),
    CriterionField.SOCIAL_CATEGORY.value: ("Social category", "सामाजिक श्रेणी"),
    CriterionField.OCCUPATION.value: ("Occupation", "व्यवसाय"),
    CriterionField.EDUCATION_LEVEL.value: ("Education level", "शिक्षा का स्तर"),
    CriterionField.RESIDENCE_TYPE.value: ("Residence type", "निवास का प्रकार"),
    CriterionField.MARITAL_STATUS.value: ("Marital status", "वैवाहिक स्थिति"),
    CriterionField.DISABILITY_STATUS.value: (
        "Disability status",
        "दिव्यांगता की स्थिति",
    ),
    CriterionField.IS_STUDENT.value: ("Student status", "छात्र स्थिति"),
}

# Display mappings for enum values in English and Hindi
VALUE_TRANSLATIONS: dict[str, tuple[str, str]] = {
    # Gender
    "female": ("female", "महिला"),
    "male": ("male", "पुरुष"),
    "transgender": ("transgender", "ट्रांसजेंडर"),
    "other": ("other", "अन्य"),
    # Social Category
    "general": ("General", "सामान्य"),
    "obc": ("OBC", "ओबीसी"),
    "sc": ("SC", "एससी"),
    "st": ("ST", "एसटी"),
    "ebc": ("EBC", "ईबीसी"),
    # Residence
    "rural": ("rural", "ग्रामीण"),
    "urban": ("urban", "शहरी"),
    # Marital Status
    "single": ("single", "अविवाहित"),
    "married": ("married", "विवाहित"),
    "widowed": ("widowed", "विधवा/विधुर"),
    "divorced": ("divorced", "तलाकशुदा"),
    "separated": ("separated", "अलग"),
    # Occupation
    "farmer": ("farmer", "किसान"),
    "artisan": ("artisan", "कारीगर"),
    "student": ("student", "छात्र"),
    "salaried": ("salaried", "वेतनभोगी"),
    "self_employed": ("self-employed", "स्वरोजगार"),
    "daily_wage": ("daily-wage worker", "दैनिक वेतनभोगी"),
    "unemployed": ("unemployed", "बेरोजगार"),
    "homemaker": ("homemaker", "गृहिणी"),
    "retired": ("retired", "सेवानिवृत्त"),
    # Disability
    "none": ("none", "कोई नहीं"),
    "locomotor": ("locomotor", "चलने-फिरने में अक्षम"),
    "visual": ("visual", "दृष्टिबाधित"),
    "hearing": ("hearing", "श्रवण बाधित"),
    "speech_and_language": ("speech & language", "वाणी एवं भाषा"),
    "intellectual": ("intellectual", "बौद्धिक"),
    "mental_illness": ("mental illness", "मानसिक अस्वस्थता"),
    "multiple": ("multiple disabilities", "बहु-दिव्यांगता"),
    # Education
    "primary": ("primary", "प्राथमिक"),
    "secondary": ("secondary", "माध्यमिक"),
    "higher_secondary": ("higher secondary", "उच्च माध्यमिक"),
    "diploma": ("diploma", "डिप्लोमा"),
    "graduate": ("graduate", "स्नातक"),
    "post_graduate": ("post graduate", "स्नातकोत्तर"),
    "doctorate": ("doctorate", "डॉक्टरेट"),
    # Boolean
    "true": ("Yes", "हाँ"),
    "false": ("No", "नहीं"),
}


def _format_value_en(val: Any) -> str:
    """Format value for English reason string."""
    if val is None:
        return "not provided"
    if isinstance(val, bool):
        return "Yes" if val else "No"
    if isinstance(val, float):
        if val.is_integer():
            return f"{int(val):,}"
        return f"{val:,.2f}"
    if isinstance(val, int):
        return f"{val:,}"
    if isinstance(val, list | tuple):
        return ", ".join(_format_value_en(v) for v in val)
    s = str(val)
    if s.lower() in VALUE_TRANSLATIONS:
        return VALUE_TRANSLATIONS[s.lower()][0]
    return s.replace("_", " ").title()


def _format_value_hi(val: Any) -> str:
    """Format value for Hindi reason string."""
    if val is None:
        return "जानकारी नहीं दी गई"
    if isinstance(val, bool):
        return "हाँ" if val else "नहीं"
    if isinstance(val, float):
        if val.is_integer():
            return f"{int(val):,}"
        return f"{val:,.2f}"
    if isinstance(val, int):
        return f"{val:,}"
    if isinstance(val, list | tuple):
        return ", ".join(_format_value_hi(v) for v in val)
    s = str(val)
    if s.lower() in VALUE_TRANSLATIONS:
        return VALUE_TRANSLATIONS[s.lower()][1]
    return s.replace("_", " ")


def _format_currency_en(val: float | int) -> str:
    """Format Indian Rupees in English."""
    return f"₹{val:,.0f}" if isinstance(val, int | float) else f"₹{val}"


def _format_currency_hi(val: float | int) -> str:
    """Format Indian Rupees in Hindi."""
    return f"₹{val:,.0f}" if isinstance(val, int | float) else f"₹{val}"


def _build_reason_templates(
    field: str,
    op: CriterionOperator,
    expected: Any,
    actual: Any,
    status: ThreeValuedLogic,
) -> tuple[str, str]:
    """Build English and Hindi deterministic reason strings from templates."""
    field_en, field_hi = FIELD_LABELS.get(
        field, (field.replace("_", " ").title(), field)
    )
    symbol = (
        "✓"
        if status == ThreeValuedLogic.TRUE
        else ("✗" if status == ThreeValuedLogic.FALSE else "?")
    )

    # Handle Unknown
    if status == ThreeValuedLogic.UNKNOWN:
        if (
            op == CriterionOperator.BETWEEN
            and isinstance(expected, list | tuple)
            and len(expected) == 2
        ):
            cond_en = f"{field_en} {expected[0]} to {expected[1]}"
            cond_hi = f"{field_hi} {expected[0]} से {expected[1]}"
        elif op == CriterionOperator.GTE:
            cond_en = f"{field_en} at least {expected}"
            cond_hi = f"{field_hi} न्यूनतम {expected}"
        elif op == CriterionOperator.LTE:
            if field == CriterionField.ANNUAL_INCOME.value:
                cond_en = f"{field_en} up to {_format_currency_en(expected)}"
                cond_hi = f"{field_hi} अधिकतम {_format_currency_hi(expected)}"
            else:
                cond_en = f"{field_en} up to {expected}"
                cond_hi = f"{field_hi} अधिकतम {expected}"
        elif op == CriterionOperator.EQ:
            cond_en = f"{field_en} must be {_format_value_en(expected)}"
            cond_hi = f"{field_hi} {_format_value_hi(expected)} होना चाहिए"
        elif op == CriterionOperator.IN:
            cond_en = f"{field_en} in [{_format_value_en(expected)}]"
            cond_hi = f"{field_hi} [{_format_value_hi(expected)}] में से"
        elif op == CriterionOperator.NOT_IN:
            cond_en = f"{field_en} not in [{_format_value_en(expected)}]"
            cond_hi = f"{field_hi} [{_format_value_hi(expected)}] में नहीं"
        else:
            cond_en = f"{field_en} criteria"
            cond_hi = f"{field_hi} मानदंड"

        en = f"{cond_en}: {field_en.lower()} not provided {symbol}"
        hi = f"{cond_hi}: {field_hi} की जानकारी नहीं दी गई {symbol}"
        return en, hi

    # Handle True or False with concrete actual values
    if (
        op == CriterionOperator.BETWEEN
        and isinstance(expected, list | tuple)
        and len(expected) == 2
    ):
        en = (
            f"{field_en} {expected[0]} to {expected[1]}: "
            f"your {field_en.lower()} is {actual} {symbol}"
        )
        hi = (
            f"{field_hi} {expected[0]} से {expected[1]}: "
            f"आपकी {field_hi} {actual} है {symbol}"
        )
        return en, hi

    if op == CriterionOperator.GTE:
        if field == CriterionField.AGE.value:
            en = f"Age at least {expected}: your age is {actual} {symbol}"
            hi = f"आयु कम से कम {expected}: आपकी आयु {actual} है {symbol}"
        else:
            v_en = _format_value_en(expected)
            a_en = _format_value_en(actual)
            v_hi = _format_value_hi(expected)
            a_hi = _format_value_hi(actual)
            en = (
                f"{field_en} at least {v_en}: "
                f"your {field_en.lower()} is {a_en} {symbol}"
            )
            hi = f"{field_hi} कम से कम {v_hi}: आपकी {field_hi} {a_hi} है {symbol}"
        return en, hi

    if op == CriterionOperator.LTE:
        if field == CriterionField.ANNUAL_INCOME.value:
            exp_curr_en = _format_currency_en(expected)
            act_curr_en = _format_currency_en(actual)
            exp_curr_hi = _format_currency_hi(expected)
            act_curr_hi = _format_currency_hi(actual)
            en = (
                f"Annual income up to {exp_curr_en}: "
                f"your income is {act_curr_en} {symbol}"
            )
            hi = f"वार्षिक आय अधिकतम {exp_curr_hi}: " f"आपकी आय {act_curr_hi} है {symbol}"
        else:
            v_en = _format_value_en(expected)
            a_en = _format_value_en(actual)
            v_hi = _format_value_hi(expected)
            a_hi = _format_value_hi(actual)
            en = (
                f"{field_en} at most {v_en}: "
                f"your {field_en.lower()} is {a_en} {symbol}"
            )
            hi = f"{field_hi} अधिकतम {v_hi}: आपकी {field_hi} {a_hi} है {symbol}"
        return en, hi

    if op == CriterionOperator.EQ:
        v_en = _format_value_en(expected)
        a_en = _format_value_en(actual)
        v_hi = _format_value_hi(expected)
        a_hi = _format_value_hi(actual)
        en = f"{field_en} must be {v_en}: your {field_en.lower()} is {a_en} {symbol}"
        hi = f"{field_hi} {v_hi} होना चाहिए: आपकी {field_hi} {a_hi} है {symbol}"
        return en, hi

    if op == CriterionOperator.IN:
        v_en = _format_value_en(expected)
        a_en = _format_value_en(actual)
        v_hi = _format_value_hi(expected)
        a_hi = _format_value_hi(actual)
        en = (
            f"{field_en} one of [{v_en}]: "
            f"your {field_en.lower()} is {a_en} {symbol}"
        )
        hi = f"{field_hi} [{v_hi}] में से एक: आपकी {field_hi} {a_hi} है {symbol}"
        return en, hi

    if op == CriterionOperator.NOT_IN:
        v_en = _format_value_en(expected)
        a_en = _format_value_en(actual)
        v_hi = _format_value_hi(expected)
        a_hi = _format_value_hi(actual)
        en = (
            f"{field_en} not in [{v_en}]: "
            f"your {field_en.lower()} is {a_en} {symbol}"
        )
        hi = f"{field_hi} [{v_hi}] में नहीं: आपकी {field_hi} {a_hi} है {symbol}"
        return en, hi

    en = f"{field_en} condition: evaluated {actual} {symbol}"
    hi = f"{field_hi} शर्त: परिणाम {actual} {symbol}"
    return en, hi


def _normalize_str(val: Any) -> str:
    """Normalize string for safe case-insensitive comparison."""
    if hasattr(val, "value"):
        val = val.value
    return str(val).strip().lower()


def _is_leap_year(year: int) -> bool:
    """Return True if Gregorian year is a leap year."""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def _compute_possible_age_range_at_cutoff(
    current_age: int,
    ref_date: date,
    cut_off_date: date,
) -> set[int]:
    """Compute possible completed ages at cut_off_date from current age."""

    def _calc_age(b_year: int, b_month: int, b_day: int, target: date) -> int:
        return target.year - b_year - ((target.month, target.day) < (b_month, b_day))

    # Youngest possible birth: celebrated birthday on ref_date
    y_year = ref_date.year - current_age
    y_month = ref_date.month
    y_day = (
        28
        if (ref_date.month == 2 and ref_date.day == 29 and not _is_leap_year(y_year))
        else ref_date.day
    )
    age_youngest = _calc_age(y_year, y_month, y_day, cut_off_date)

    # Oldest possible birth: turns current_age + 1 on the day after ref_date
    day_after = ref_date + timedelta(days=1)
    o_year = ref_date.year - current_age - 1
    o_month = day_after.month
    o_day = (
        28
        if (day_after.month == 2 and day_after.day == 29 and not _is_leap_year(o_year))
        else day_after.day
    )
    age_oldest = _calc_age(o_year, o_month, o_day, cut_off_date)

    min_a = min(age_youngest, age_oldest)
    max_a = max(age_youngest, age_oldest)
    return set(range(min_a, max_a + 1))


def _eval_operator(op: CriterionOperator, actual: Any, expected: Any) -> bool:
    """Evaluate deterministic operator against concrete actual and expected values."""
    if op == CriterionOperator.EQ:
        if isinstance(actual, str) or isinstance(expected, str):
            return _normalize_str(actual) == _normalize_str(expected)
        if isinstance(actual, bool) or isinstance(expected, bool):
            return bool(actual) is bool(expected)
        return actual == expected

    if op == CriterionOperator.IN:
        if not isinstance(expected, list | tuple):
            return False
        if isinstance(actual, str):
            norm_actual = _normalize_str(actual)
            norm_list = [_normalize_str(e) for e in expected]
            return norm_actual in norm_list
        return actual in expected

    if op == CriterionOperator.NOT_IN:
        if not isinstance(expected, list | tuple):
            return True
        if isinstance(actual, str):
            norm_actual = _normalize_str(actual)
            norm_list = [_normalize_str(e) for e in expected]
            return norm_actual not in norm_list
        return actual not in expected

    if op == CriterionOperator.GTE:
        return float(actual) >= float(expected)

    if op == CriterionOperator.LTE:
        return float(actual) <= float(expected)

    if op == CriterionOperator.BETWEEN:
        if not isinstance(expected, list | tuple) or len(expected) != 2:
            return False
        return float(expected[0]) <= float(actual) <= float(expected[1])

    raise ValueError(f"Unsupported CriterionOperator: '{op}'")


class RuleEngineService:
    """Deterministic, pure-Python rule engine for citizen scheme qualification.

    Invariants:
    - Zero LLM, zero network, zero database interaction.
    - Three-valued logic: True, False, Unknown.
    - Missing or 'prefer_not_to_say' yields Unknown, NEVER False.
    - In all_of: any False yields not_eligible; otherwise any Unknown
      yields maybe; otherwise eligible.
    - In any_of: any True satisfies any_of; all False fails; otherwise Unknown.
    - One failed condition beats unknowns.
    - Age 'as on' cut-off date is evaluated with mathematical precision when specified.
    """

    def evaluate_criterion(
        self,
        profile: UserProfile,
        criterion: Criterion,
        cut_off_date: date | str | None = None,
        reference_date: date | None = None,
    ) -> ConditionDetail:
        """Evaluate single criterion against profile under three-valued logic."""
        if not isinstance(criterion, Criterion):
            raise TypeError(f"Expected Criterion instance, got {type(criterion)}")

        field_name = criterion.field.value
        op = criterion.op
        expected = criterion.value
        as_on = criterion.as_on or cut_off_date

        # Special handling for age with cut-off date
        if criterion.field == CriterionField.AGE and as_on is not None:
            as_on_date = date.fromisoformat(as_on) if isinstance(as_on, str) else as_on
            if profile.age is not None:
                ref_d = reference_date or date.today()
                possible_ages = _compute_possible_age_range_at_cutoff(
                    profile.age, ref_d, as_on_date
                )
                results = {_eval_operator(op, a, expected) for a in possible_ages}
                if results == {True}:
                    status = ThreeValuedLogic.TRUE
                    actual_val = profile.age
                elif results == {False}:
                    status = ThreeValuedLogic.FALSE
                    actual_val = profile.age
                else:
                    # Straddles boundary -> unknown (maybe)
                    status = ThreeValuedLogic.UNKNOWN
                    actual_val = None
            else:
                status = ThreeValuedLogic.UNKNOWN
                actual_val = None

            reason_en, reason_hi = _build_reason_templates(
                field_name, op, expected, actual_val, status
            )
            return ConditionDetail(
                field=field_name,
                op=op.value,
                expected=expected,
                actual=actual_val,
                status=status,
                reason_en=reason_en,
                reason_hi=reason_hi,
            )

        # Standard field evaluation
        if profile.is_field_unknown(field_name):
            status = ThreeValuedLogic.UNKNOWN
            actual_val = None
        else:
            actual_val = profile.get_effective_value(field_name)
            try:
                is_satisfied = _eval_operator(op, actual_val, expected)
                status = (
                    ThreeValuedLogic.TRUE if is_satisfied else ThreeValuedLogic.FALSE
                )
            except Exception as err:
                raise ValueError(
                    f"Error evaluating operator '{op.value}' on field '{field_name}' "
                    f"with actual={actual_val} and expected={expected}: {err}"
                ) from err

        reason_en, reason_hi = _build_reason_templates(
            field_name, op, expected, actual_val, status
        )
        return ConditionDetail(
            field=field_name,
            op=op.value,
            expected=expected,
            actual=actual_val,
            status=status,
            reason_en=reason_en,
            reason_hi=reason_hi,
        )

    def evaluate(
        self,
        profile: UserProfile | dict[str, Any],
        criteria: EligibilityCriteria | dict[str, Any],
        lang: str = "en",
        reference_date: date | None = None,
    ) -> EligibilityResult:
        """Deterministically evaluate a citizen profile against EligibilityCriteria.

        Args:
            profile: Validated UserProfile or dict.
            criteria: Validated EligibilityCriteria or dict.
            lang: Output language for passed/failed conditions ("en" or "hi").
            reference_date: Optional reference date for relative age evaluation.

        Returns:
            EligibilityResult with status (eligible, maybe, not_eligible),
            passed conditions, failed conditions, and missing fields.
        """
        # Validate profile input
        if isinstance(profile, dict):
            try:
                profile = UserProfile.model_validate(profile)
            except ValidationError as e:
                raise ValueError(f"Malformed UserProfile input: {e}") from e
        elif not isinstance(profile, UserProfile):
            raise TypeError(
                f"Expected UserProfile or dict, got {type(profile).__name__}"
            )

        # Validate criteria input
        if isinstance(criteria, dict):
            try:
                criteria = EligibilityCriteria.model_validate(criteria)
            except ValidationError as e:
                raise ValueError(f"Malformed EligibilityCriteria input: {e}") from e
        elif not isinstance(criteria, EligibilityCriteria):
            raise TypeError(
                f"Expected EligibilityCriteria or dict, got {type(criteria).__name__}"
            )

        # Fast path: empty criteria means universally open eligibility
        if not criteria.all_of and not criteria.any_of:
            return EligibilityResult(
                status=EligibilityStatus.ELIGIBLE,
                passed_conditions=[],
                failed_conditions=[],
                missing_fields=[],
                passed_conditions_en=[],
                passed_conditions_hi=[],
                failed_conditions_en=[],
                failed_conditions_hi=[],
                details=[],
            )

        cut_off_date = criteria.as_on

        all_of_passed: list[ConditionDetail] = []
        all_of_failed: list[ConditionDetail] = []
        all_of_unknown: list[ConditionDetail] = []
        missing_fields: list[str] = []

        # 1. Evaluate all_of
        for c in criteria.all_of:
            detail = self.evaluate_criterion(
                profile, c, cut_off_date=cut_off_date, reference_date=reference_date
            )
            if detail.status == ThreeValuedLogic.TRUE:
                all_of_passed.append(detail)
            elif detail.status == ThreeValuedLogic.FALSE:
                all_of_failed.append(detail)
            else:
                all_of_unknown.append(detail)
                if detail.field not in missing_fields:
                    missing_fields.append(detail.field)

        # Determine all_of block outcome
        if all_of_failed:
            all_of_status = ThreeValuedLogic.FALSE
        elif all_of_unknown:
            all_of_status = ThreeValuedLogic.UNKNOWN
        else:
            all_of_status = ThreeValuedLogic.TRUE

        # 2. Evaluate any_of (if present)
        any_of_passed: list[ConditionDetail] = []
        any_of_failed: list[ConditionDetail] = []
        any_of_unknown: list[ConditionDetail] = []

        if not criteria.any_of:
            any_of_status = ThreeValuedLogic.TRUE
        else:
            for c in criteria.any_of:
                detail = self.evaluate_criterion(
                    profile, c, cut_off_date=cut_off_date, reference_date=reference_date
                )
                if detail.status == ThreeValuedLogic.TRUE:
                    any_of_passed.append(detail)
                elif detail.status == ThreeValuedLogic.FALSE:
                    any_of_failed.append(detail)
                else:
                    any_of_unknown.append(detail)

            if any_of_passed:
                any_of_status = ThreeValuedLogic.TRUE
            elif len(any_of_failed) == len(criteria.any_of):
                any_of_status = ThreeValuedLogic.FALSE
            else:
                any_of_status = ThreeValuedLogic.UNKNOWN
                # Since no any_of branch is satisfied, unknowns are candidates
                for d in any_of_unknown:
                    if d.field not in missing_fields:
                        missing_fields.append(d.field)

        # 3. Combine under conjunction: all_of AND any_of
        # Rule: One failed condition beats unknowns
        if (
            all_of_status == ThreeValuedLogic.FALSE
            or any_of_status == ThreeValuedLogic.FALSE
        ):
            overall_status = EligibilityStatus.NOT_ELIGIBLE
        elif (
            all_of_status == ThreeValuedLogic.UNKNOWN
            or any_of_status == ThreeValuedLogic.UNKNOWN
        ):
            overall_status = EligibilityStatus.MAYBE
        else:
            overall_status = EligibilityStatus.ELIGIBLE

        # Compile passed conditions
        passed_details = all_of_passed + any_of_passed
        passed_en = [d.reason_en for d in passed_details]
        passed_hi = [d.reason_hi for d in passed_details]

        # Compile failed conditions
        failed_details: list[ConditionDetail] = list(all_of_failed)
        if any_of_status == ThreeValuedLogic.FALSE:
            failed_details.extend(any_of_failed)

        failed_en = [d.reason_en for d in failed_details]
        failed_hi = [d.reason_hi for d in failed_details]

        # Select language for default lists
        is_hi = str(lang).lower().startswith("hi")
        passed_conditions = passed_hi if is_hi else passed_en
        failed_conditions = failed_hi if is_hi else failed_en

        all_details = (
            all_of_passed
            + all_of_failed
            + all_of_unknown
            + any_of_passed
            + any_of_failed
            + any_of_unknown
        )

        return EligibilityResult(
            status=overall_status,
            passed_conditions=passed_conditions,
            failed_conditions=failed_conditions,
            missing_fields=missing_fields,
            passed_conditions_en=passed_en,
            passed_conditions_hi=passed_hi,
            failed_conditions_en=failed_en,
            failed_conditions_hi=failed_hi,
            details=all_details,
        )

    def prefilter_schemes(
        self,
        schemes: Sequence[Scheme | SchemeBase],
        profile: UserProfile,
    ) -> list[Scheme | SchemeBase]:
        """Pre-filter schemes by level and state before full evaluation.

        - Central schemes are never filtered out.
        - State schemes are retained if state matches, or if state is unknown.
        - State schemes are dropped if citizen state is known and mismatched.
        """
        if not isinstance(profile, UserProfile):
            profile = UserProfile.model_validate(profile)

        # Retain all schemes if citizen state is unknown
        if profile.is_field_unknown("state"):
            return list(schemes)

        user_state = profile.get_effective_value("state")
        norm_user_state = _normalize_str(user_state)

        filtered: list[Scheme | SchemeBase] = []
        for s in schemes:
            if s.level == SchemeLevel.CENTRAL:
                filtered.append(s)
            elif s.level == SchemeLevel.STATE and s.state:
                if _normalize_str(s.state) == norm_user_state:
                    filtered.append(s)

        return filtered

    def evaluate_scheme(
        self,
        profile: UserProfile | dict[str, Any],
        scheme: Scheme | SchemeBase | dict[str, Any],
        lang: str = "en",
        reference_date: date | None = None,
    ) -> EligibilityResult:
        """Evaluate citizen profile against full scheme record (including state)."""
        if isinstance(profile, dict):
            profile = UserProfile.model_validate(profile)
        if isinstance(scheme, dict):
            scheme = SchemeBase.model_validate(scheme)

        # 1. State and level validation
        is_hi = str(lang).lower().startswith("hi")
        state_failed = False
        state_unknown = False
        state_passed = False
        user_state_val = profile.get_effective_value("state")

        state_detail: ConditionDetail | None = None

        if scheme.level == SchemeLevel.STATE and scheme.state:
            s_name_en = _format_value_en(scheme.state)
            s_name_hi = _format_value_hi(scheme.state)
            if profile.is_field_unknown("state"):
                state_unknown = True
                state_detail = ConditionDetail(
                    field="state",
                    op=CriterionOperator.EQ.value,
                    expected=scheme.state,
                    actual=None,
                    status=ThreeValuedLogic.UNKNOWN,
                    reason_en=f"State must be {s_name_en}: state not provided ?",
                    reason_hi=(
                        f"राज्य {s_name_hi} होना चाहिए: " f"राज्य की जानकारी नहीं दी गई ?"
                    ),
                )
            else:
                if _normalize_str(user_state_val) == _normalize_str(scheme.state):
                    state_passed = True
                    state_detail = ConditionDetail(
                        field="state",
                        op=CriterionOperator.EQ.value,
                        expected=scheme.state,
                        actual=user_state_val,
                        status=ThreeValuedLogic.TRUE,
                        reason_en=(
                            f"State {scheme.state}: "
                            f"your state is {user_state_val} ✓"
                        ),
                        reason_hi=(
                            f"राज्य {scheme.state}: " f"आपका राज्य {user_state_val} है ✓"
                        ),
                    )
                else:
                    state_failed = True
                    state_detail = ConditionDetail(
                        field="state",
                        op=CriterionOperator.EQ.value,
                        expected=scheme.state,
                        actual=user_state_val,
                        status=ThreeValuedLogic.FALSE,
                        reason_en=(
                            f"State must be {scheme.state}: "
                            f"your state is {user_state_val} ✗"
                        ),
                        reason_hi=(
                            f"राज्य {scheme.state} होना चाहिए: "
                            f"आपका राज्य {user_state_val} है ✗"
                        ),
                    )

        # 2. Evaluate criteria
        result = self.evaluate(
            profile,
            scheme.eligibility_criteria,
            lang=lang,
            reference_date=reference_date,
        )

        # If central scheme or no state condition, return criteria result directly
        if state_detail is None:
            return result

        # 3. Merge state condition with criteria result
        passed_en = list(result.passed_conditions_en)
        passed_hi = list(result.passed_conditions_hi)
        failed_en = list(result.failed_conditions_en)
        failed_hi = list(result.failed_conditions_hi)
        missing_fields = list(result.missing_fields)
        details = list(result.details) + [state_detail]

        if state_passed:
            passed_en.append(state_detail.reason_en)
            passed_hi.append(state_detail.reason_hi)
        elif state_failed:
            failed_en.append(state_detail.reason_en)
            failed_hi.append(state_detail.reason_hi)
        elif state_unknown:
            if "state" not in missing_fields:
                missing_fields.append("state")

        # Recompute overall status
        if state_failed or result.status == EligibilityStatus.NOT_ELIGIBLE:
            overall_status = EligibilityStatus.NOT_ELIGIBLE
        elif state_unknown or result.status == EligibilityStatus.MAYBE:
            overall_status = EligibilityStatus.MAYBE
        else:
            overall_status = EligibilityStatus.ELIGIBLE

        return EligibilityResult(
            status=overall_status,
            passed_conditions=passed_hi if is_hi else passed_en,
            failed_conditions=failed_hi if is_hi else failed_en,
            missing_fields=missing_fields,
            passed_conditions_en=passed_en,
            passed_conditions_hi=passed_hi,
            failed_conditions_en=failed_en,
            failed_conditions_hi=failed_hi,
            details=details,
        )
