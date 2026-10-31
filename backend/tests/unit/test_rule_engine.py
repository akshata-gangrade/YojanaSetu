"""Unit tests for the deterministic Python rule engine.

Product rules:
- Pure Python. No LLM, no database, no network, no randomness.
- Target: 95%+ line coverage for rule_engine.py.
- Proves: every operator; boundary values; missing/prefer_not_to_say gives maybe;
  one failed condition beats unknowns; any_of with unknowns; state mismatch;
  central vs state schemes; sensitive field omitted; empty criteria;
  malformed criteria; determinism; and age 'as on' cut-off date.
"""

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from app.schemas.criteria import Criterion, EligibilityCriteria
from app.schemas.enums import (
    CriterionField,
    CriterionOperator,
    DisabilityStatus,
    Gender,
    IndianState,
    Occupation,
    SchemeLevel,
    SocialCategory,
)
from app.schemas.scheme import SchemeBase
from app.schemas.user_profile import UserProfile
from app.services.rule_engine import (
    EligibilityStatus,
    RuleEngineService,
)


@pytest.fixture
def engine() -> RuleEngineService:
    """RuleEngineService instance fixture."""
    return RuleEngineService()


# ==============================================================================
# 1. Every Operator Tests (eq, in, not_in, gte, lte, between)
# ==============================================================================


def test_operator_eq_pass_and_fail(engine: RuleEngineService) -> None:
    """Test EQ operator with exact matches, case insensitivity, and mismatches."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.GENDER,
                op=CriterionOperator.EQ,
                value="female",
            )
        ]
    )
    # Match
    p_pass = UserProfile(gender=Gender.FEMALE)
    res_pass = engine.evaluate(p_pass, crit)
    assert res_pass.status == EligibilityStatus.ELIGIBLE
    assert len(res_pass.passed_conditions) == 1
    assert "✓" in res_pass.passed_conditions[0]
    assert "female" in res_pass.passed_conditions[0]

    # Mismatch
    p_fail = UserProfile(gender=Gender.MALE)
    res_fail = engine.evaluate(p_fail, crit)
    assert res_fail.status == EligibilityStatus.NOT_ELIGIBLE
    assert len(res_fail.failed_conditions) == 1
    assert "✗" in res_fail.failed_conditions[0]


def test_operator_eq_boolean(engine: RuleEngineService) -> None:
    """Test EQ operator on boolean fields."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.IS_STUDENT,
                op=CriterionOperator.EQ,
                value=True,
            )
        ]
    )
    res1 = engine.evaluate(UserProfile(is_student=True), crit)
    assert res1.status == EligibilityStatus.ELIGIBLE

    res2 = engine.evaluate(UserProfile(is_student=False), crit)
    assert res2.status == EligibilityStatus.NOT_ELIGIBLE


def test_operator_in_pass_and_fail(engine: RuleEngineService) -> None:
    """Test IN operator with membership in allowed collection."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.OCCUPATION,
                op=CriterionOperator.IN,
                value=["farmer", "artisan"],
            )
        ]
    )
    res_pass1 = engine.evaluate(UserProfile(occupation=Occupation.FARMER), crit)
    assert res_pass1.status == EligibilityStatus.ELIGIBLE

    res_pass2 = engine.evaluate(UserProfile(occupation=Occupation.ARTISAN), crit)
    assert res_pass2.status == EligibilityStatus.ELIGIBLE

    res_fail = engine.evaluate(UserProfile(occupation=Occupation.SALARIED), crit)
    assert res_fail.status == EligibilityStatus.NOT_ELIGIBLE
    assert "✗" in res_fail.failed_conditions[0]


def test_operator_not_in_pass_and_fail(engine: RuleEngineService) -> None:
    """Test NOT_IN operator ensuring disallowed values fail."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.SOCIAL_CATEGORY,
                op=CriterionOperator.NOT_IN,
                value=["general"],
            )
        ]
    )
    res_pass = engine.evaluate(UserProfile(social_category=SocialCategory.OBC), crit)
    assert res_pass.status == EligibilityStatus.ELIGIBLE

    res_fail = engine.evaluate(
        UserProfile(social_category=SocialCategory.GENERAL), crit
    )
    assert res_fail.status == EligibilityStatus.NOT_ELIGIBLE


def test_operator_gte_pass_and_fail(engine: RuleEngineService) -> None:
    """Test GTE operator for numbers and ages."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.GTE,
                value=21,
            )
        ]
    )
    assert (
        engine.evaluate(UserProfile(age=25), crit).status == EligibilityStatus.ELIGIBLE
    )
    assert (
        engine.evaluate(UserProfile(age=20), crit).status
        == EligibilityStatus.NOT_ELIGIBLE
    )


def test_operator_lte_pass_and_fail(engine: RuleEngineService) -> None:
    """Test LTE operator for income ceilings."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.ANNUAL_INCOME,
                op=CriterionOperator.LTE,
                value=250000.0,
            )
        ]
    )
    assert (
        engine.evaluate(UserProfile(annual_income=200000.0), crit).status
        == EligibilityStatus.ELIGIBLE
    )
    assert (
        engine.evaluate(UserProfile(annual_income=300000.0), crit).status
        == EligibilityStatus.NOT_ELIGIBLE
    )


def test_operator_between_pass_and_fail(engine: RuleEngineService) -> None:
    """Test BETWEEN operator for age brackets."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.BETWEEN,
                value=[18, 30],
            )
        ]
    )
    assert (
        engine.evaluate(UserProfile(age=22), crit).status == EligibilityStatus.ELIGIBLE
    )
    assert (
        engine.evaluate(UserProfile(age=16), crit).status
        == EligibilityStatus.NOT_ELIGIBLE
    )
    assert (
        engine.evaluate(UserProfile(age=35), crit).status
        == EligibilityStatus.NOT_ELIGIBLE
    )


# ==============================================================================
# 2. Boundary Values (gte min, lte cap, between bounds)
# ==============================================================================


def test_boundary_age_exact_minimum_passes(engine: RuleEngineService) -> None:
    """Age 18 with a minimum of 18 passes."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.GTE,
                value=18,
            )
        ]
    )
    res_18 = engine.evaluate(UserProfile(age=18), crit)
    assert res_18.status == EligibilityStatus.ELIGIBLE
    assert "✓" in res_18.passed_conditions[0]

    res_17 = engine.evaluate(UserProfile(age=17), crit)
    assert res_17.status == EligibilityStatus.NOT_ELIGIBLE
    assert "✗" in res_17.failed_conditions[0]


def test_boundary_income_exact_cap_passes(engine: RuleEngineService) -> None:
    """Income equal to the cap passes when the criterion is lte."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.ANNUAL_INCOME,
                op=CriterionOperator.LTE,
                value=300000.0,
            )
        ]
    )
    res_exact = engine.evaluate(UserProfile(annual_income=300000.0), crit)
    assert res_exact.status == EligibilityStatus.ELIGIBLE
    assert "✓" in res_exact.passed_conditions[0]

    res_above = engine.evaluate(UserProfile(annual_income=300001.0), crit)
    assert res_above.status == EligibilityStatus.NOT_ELIGIBLE
    assert "✗" in res_above.failed_conditions[0]


def test_boundary_between_exact_lower_and_upper_pass(engine: RuleEngineService) -> None:
    """Both lower and upper endpoints of between [18, 30] pass inclusively."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.BETWEEN,
                value=[18, 30],
            )
        ]
    )
    # Lower bound
    res_lower = engine.evaluate(UserProfile(age=18), crit)
    assert res_lower.status == EligibilityStatus.ELIGIBLE

    # Upper bound
    res_upper = engine.evaluate(UserProfile(age=30), crit)
    assert res_upper.status == EligibilityStatus.ELIGIBLE

    # Just below
    res_below = engine.evaluate(UserProfile(age=17), crit)
    assert res_below.status == EligibilityStatus.NOT_ELIGIBLE

    # Just above
    res_above = engine.evaluate(UserProfile(age=31), crit)
    assert res_above.status == EligibilityStatus.NOT_ELIGIBLE


# ==============================================================================
# 3. Missing and 'prefer_not_to_say' Fields Give 'maybe', NEVER 'not_eligible'
# ==============================================================================


def test_missing_age_yields_maybe(engine: RuleEngineService) -> None:
    """Omitted age criterion produces 'maybe', never 'not_eligible'."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.GTE,
                value=18,
            )
        ]
    )
    res = engine.evaluate(UserProfile(age=None), crit)
    assert res.status == EligibilityStatus.MAYBE
    assert "age" in res.missing_fields
    assert len(res.failed_conditions) == 0


def test_prefer_not_to_say_gender_yields_maybe(engine: RuleEngineService) -> None:
    """prefer_not_to_say for gender evaluates to unknown -> maybe."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.GENDER,
                op=CriterionOperator.EQ,
                value="female",
            )
        ]
    )
    res = engine.evaluate(UserProfile(gender=Gender.PREFER_NOT_TO_SAY), crit)
    assert res.status == EligibilityStatus.MAYBE
    assert "gender" in res.missing_fields
    assert len(res.failed_conditions) == 0


def test_prefer_not_to_say_social_category_yields_maybe(
    engine: RuleEngineService,
) -> None:
    """prefer_not_to_say for social_category evaluates to unknown -> maybe."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.SOCIAL_CATEGORY,
                op=CriterionOperator.IN,
                value=["sc", "st"],
            )
        ]
    )
    res = engine.evaluate(
        UserProfile(social_category=SocialCategory.PREFER_NOT_TO_SAY), crit
    )
    assert res.status == EligibilityStatus.MAYBE
    assert "social_category" in res.missing_fields
    assert len(res.failed_conditions) == 0


def test_prefer_not_to_say_disability_yields_maybe(engine: RuleEngineService) -> None:
    """prefer_not_to_say for disability_status yields maybe."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.DISABILITY_STATUS,
                op=CriterionOperator.NOT_IN,
                value=["none"],
            )
        ]
    )
    res = engine.evaluate(
        UserProfile(disability_status=DisabilityStatus.PREFER_NOT_TO_SAY), crit
    )
    assert res.status == EligibilityStatus.MAYBE
    assert "disability_status" in res.missing_fields


def test_multiple_unknown_fields_accumulate_in_missing_fields(
    engine: RuleEngineService,
) -> None:
    """Multiple missing fields appear in missing_fields without duplicates."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.BETWEEN,
                value=[18, 30],
            ),
            Criterion(
                field=CriterionField.ANNUAL_INCOME,
                op=CriterionOperator.LTE,
                value=200000.0,
            ),
            Criterion(
                field=CriterionField.OCCUPATION,
                op=CriterionOperator.EQ,
                value="farmer",
            ),
        ]
    )
    profile = UserProfile(
        age=None, annual_income=None, occupation=Occupation.PREFER_NOT_TO_SAY
    )
    res = engine.evaluate(profile, crit)
    assert res.status == EligibilityStatus.MAYBE
    assert res.missing_fields == ["age", "annual_income", "occupation"]
    assert len(res.failed_conditions) == 0


# ==============================================================================
# 4. One Failed Condition Beats Unknowns
# ==============================================================================


def test_one_failed_condition_beats_unknowns(engine: RuleEngineService) -> None:
    """In all_of: any false means not_eligible even when other fields are unknown."""
    crit = EligibilityCriteria(
        all_of=[
            # Failed condition
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.GTE,
                value=18,
            ),
            # Unknown condition
            Criterion(
                field=CriterionField.ANNUAL_INCOME,
                op=CriterionOperator.LTE,
                value=300000.0,
            ),
            # Unknown condition
            Criterion(
                field=CriterionField.OCCUPATION,
                op=CriterionOperator.EQ,
                value="farmer",
            ),
        ]
    )
    # Citizen is 15 (definitely fails age) with income and occupation unknown
    profile = UserProfile(age=15, annual_income=None, occupation=None)
    res = engine.evaluate(profile, crit)

    assert res.status == EligibilityStatus.NOT_ELIGIBLE
    assert len(res.failed_conditions) == 1
    assert "Age at least 18" in res.failed_conditions[0]
    assert "15 ✗" in res.failed_conditions[0]


def test_one_failed_beats_passed_and_unknowns(engine: RuleEngineService) -> None:
    """One failed condition with passed and unknown conditions yields not_eligible."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.GENDER, op=CriterionOperator.EQ, value="female"
            ),
            Criterion(field=CriterionField.AGE, op=CriterionOperator.LTE, value=25),
            Criterion(
                field=CriterionField.ANNUAL_INCOME,
                op=CriterionOperator.LTE,
                value=100000.0,
            ),
        ]
    )
    # Female (pass), Age 30 (fail), Income unknown (unknown)
    profile = UserProfile(gender=Gender.FEMALE, age=30, annual_income=None)
    res = engine.evaluate(profile, crit)
    assert res.status == EligibilityStatus.NOT_ELIGIBLE
    assert len(res.passed_conditions) == 1
    assert len(res.failed_conditions) == 1


# ==============================================================================
# 5. any_of with Unknowns
# ==============================================================================


def test_any_of_one_true_satisfies_even_with_unknown(engine: RuleEngineService) -> None:
    """For any_of: any true means satisfied, regardless of unknowns in any_of."""
    crit = EligibilityCriteria(
        any_of=[
            Criterion(
                field=CriterionField.OCCUPATION, op=CriterionOperator.EQ, value="farmer"
            ),
            Criterion(
                field=CriterionField.DISABILITY_STATUS,
                op=CriterionOperator.NOT_IN,
                value=["none"],
            ),
        ]
    )
    # Occupation is farmer (True), disability is unknown
    profile = UserProfile(occupation=Occupation.FARMER, disability_status=None)
    res = engine.evaluate(profile, crit)
    assert res.status == EligibilityStatus.ELIGIBLE
    assert len(res.passed_conditions) == 1
    assert len(res.failed_conditions) == 0


def test_any_of_all_false_means_not_satisfied(engine: RuleEngineService) -> None:
    """For any_of: all false means not satisfied (not_eligible)."""
    crit = EligibilityCriteria(
        any_of=[
            Criterion(
                field=CriterionField.OCCUPATION, op=CriterionOperator.EQ, value="farmer"
            ),
            Criterion(
                field=CriterionField.OCCUPATION,
                op=CriterionOperator.EQ,
                value="artisan",
            ),
        ]
    )
    profile = UserProfile(occupation=Occupation.SALARIED)
    res = engine.evaluate(profile, crit)
    assert res.status == EligibilityStatus.NOT_ELIGIBLE
    assert len(res.failed_conditions) == 2


def test_any_of_false_and_unknown_yields_maybe(engine: RuleEngineService) -> None:
    """For any_of: no true branch and an unknown branch yields unknown (maybe)."""
    crit = EligibilityCriteria(
        any_of=[
            Criterion(
                field=CriterionField.OCCUPATION, op=CriterionOperator.EQ, value="farmer"
            ),
            Criterion(
                field=CriterionField.DISABILITY_STATUS,
                op=CriterionOperator.NOT_IN,
                value=["none"],
            ),
        ]
    )
    # Occupation salaried (False), disability unknown (Unknown)
    profile = UserProfile(occupation=Occupation.SALARIED, disability_status=None)
    res = engine.evaluate(profile, crit)
    assert res.status == EligibilityStatus.MAYBE
    assert "disability_status" in res.missing_fields


def test_any_of_all_unknown_yields_maybe(engine: RuleEngineService) -> None:
    """any_of with all branches unknown yields maybe."""
    crit = EligibilityCriteria(
        any_of=[
            Criterion(
                field=CriterionField.OCCUPATION, op=CriterionOperator.EQ, value="farmer"
            ),
            Criterion(
                field=CriterionField.DISABILITY_STATUS,
                op=CriterionOperator.NOT_IN,
                value=["none"],
            ),
        ]
    )
    profile = UserProfile(occupation=None, disability_status=None)
    res = engine.evaluate(profile, crit)
    assert res.status == EligibilityStatus.MAYBE
    assert "occupation" in res.missing_fields
    assert "disability_status" in res.missing_fields


# ==============================================================================
# 6. State Mismatch & Level Checks
# ==============================================================================


def _create_sample_scheme(
    level: SchemeLevel,
    state: str | None,
    criteria: EligibilityCriteria | None = None,
) -> SchemeBase:
    """Helper creating SchemeBase instance with valid invariants."""
    return SchemeBase(
        slug="test-scheme-slug",
        name="Test Scheme",
        name_hi="परीक्षण योजना",
        level=level,
        state=state,
        benefit_summary="Direct financial assistance of Rs 5000.",
        benefit_summary_hi="₹5000 की प्रत्यक्ष वित्तीय सहायता।",
        eligibility_criteria=criteria or EligibilityCriteria(),
        apply_url="https://example.gov.in/apply",
        source_url="https://example.gov.in/source",
        source_hash="a" * 64,
        last_verified=datetime.now(UTC),
    )


def test_state_scheme_mismatch_fails(engine: RuleEngineService) -> None:
    """State scheme for Karnataka fails for a citizen residing in Maharashtra."""
    scheme = _create_sample_scheme(level=SchemeLevel.STATE, state="karnataka")
    profile = UserProfile(state=IndianState.MAHARASHTRA)

    res = engine.evaluate_scheme(profile, scheme)
    assert res.status == EligibilityStatus.NOT_ELIGIBLE
    assert any("State must be karnataka" in f for f in res.failed_conditions)
    assert any("maharashtra ✗" in f for f in res.failed_conditions)


def test_state_scheme_matching_state_passes(engine: RuleEngineService) -> None:
    """State scheme for Maharashtra passes for a citizen in Maharashtra."""
    scheme = _create_sample_scheme(level=SchemeLevel.STATE, state="maharashtra")
    profile = UserProfile(state=IndianState.MAHARASHTRA)

    res = engine.evaluate_scheme(profile, scheme)
    assert res.status == EligibilityStatus.ELIGIBLE
    assert any("State maharashtra" in p for p in res.passed_conditions)


def test_state_scheme_unknown_state_gives_maybe(engine: RuleEngineService) -> None:
    """State scheme with unknown state gives 'maybe' and records 'state' as missing."""
    scheme = _create_sample_scheme(level=SchemeLevel.STATE, state="odisha")
    profile = UserProfile(state=None)

    res = engine.evaluate_scheme(profile, scheme)
    assert res.status == EligibilityStatus.MAYBE
    assert "state" in res.missing_fields


# ==============================================================================
# 7. Central versus State Schemes & Pre-filtering
# ==============================================================================


def test_central_scheme_applies_to_any_state(engine: RuleEngineService) -> None:
    """Central schemes qualify citizens across all states, even if state is unknown."""
    central = _create_sample_scheme(level=SchemeLevel.CENTRAL, state=None)

    # State 1
    res1 = engine.evaluate_scheme(UserProfile(state=IndianState.BIHAR), central)
    assert res1.status == EligibilityStatus.ELIGIBLE

    # State 2
    res2 = engine.evaluate_scheme(UserProfile(state=IndianState.KERALA), central)
    assert res2.status == EligibilityStatus.ELIGIBLE

    # Unknown State
    res3 = engine.evaluate_scheme(UserProfile(state=None), central)
    assert res3.status == EligibilityStatus.ELIGIBLE


def test_prefilter_schemes_filters_mismatched_state_schemes(
    engine: RuleEngineService,
) -> None:
    """prefilter_schemes retains central & matching state schemes and drops others."""
    schemes = [
        _create_sample_scheme(level=SchemeLevel.CENTRAL, state=None),
        _create_sample_scheme(level=SchemeLevel.STATE, state="punjab"),
        _create_sample_scheme(level=SchemeLevel.STATE, state="haryana"),
        _create_sample_scheme(level=SchemeLevel.STATE, state="punjab"),
    ]
    # Citizen in Punjab
    profile = UserProfile(state=IndianState.PUNJAB)
    filtered = engine.prefilter_schemes(schemes, profile)

    assert len(filtered) == 3
    assert filtered[0].level == SchemeLevel.CENTRAL
    assert filtered[1].state == "punjab"
    assert filtered[2].state == "punjab"


def test_prefilter_schemes_unknown_state_keeps_all(engine: RuleEngineService) -> None:
    """When state is unknown, prefilter retains all schemes (central and state)."""
    schemes = [
        _create_sample_scheme(level=SchemeLevel.CENTRAL, state=None),
        _create_sample_scheme(level=SchemeLevel.STATE, state="gujarat"),
        _create_sample_scheme(level=SchemeLevel.STATE, state="assam"),
    ]
    profile = UserProfile(state=None)
    filtered = engine.prefilter_schemes(schemes, profile)
    assert len(filtered) == 3


# ==============================================================================
# 8. Sensitive Fields Omitted
# ==============================================================================


def test_sensitive_social_category_omitted_gives_maybe(
    engine: RuleEngineService,
) -> None:
    """Sensitive field social_category omitted leaves condition unknown -> maybe."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.SOCIAL_CATEGORY,
                op=CriterionOperator.EQ,
                value="sc",
            )
        ]
    )
    profile = UserProfile(social_category=None)
    res = engine.evaluate(profile, crit)
    assert res.status == EligibilityStatus.MAYBE
    assert "social_category" in res.missing_fields
    assert len(res.failed_conditions) == 0


def test_sensitive_disability_omitted_gives_maybe(engine: RuleEngineService) -> None:
    """Sensitive field disability_status omitted leaves condition unknown -> maybe."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.DISABILITY_STATUS,
                op=CriterionOperator.EQ,
                value="locomotor",
            )
        ]
    )
    profile = UserProfile(disability_status=None)
    res = engine.evaluate(profile, crit)
    assert res.status == EligibilityStatus.MAYBE
    assert "disability_status" in res.missing_fields


# ==============================================================================
# 9. Empty Criteria
# ==============================================================================


def test_empty_criteria_evaluates_to_eligible(engine: RuleEngineService) -> None:
    """A scheme with empty criteria (open to all) evaluates to eligible."""
    crit = EligibilityCriteria(all_of=[], any_of=[])
    profile = UserProfile(age=25, gender=Gender.FEMALE)
    res = engine.evaluate(profile, crit)

    assert res.status == EligibilityStatus.ELIGIBLE
    assert res.passed_conditions == []
    assert res.failed_conditions == []
    assert res.missing_fields == []


# ==============================================================================
# 10. Malformed Criteria and Input Type Checking
# ==============================================================================


def test_invalid_profile_type_raises_type_error(engine: RuleEngineService) -> None:
    """Non-UserProfile and non-dict profile raises TypeError."""
    with pytest.raises(TypeError):
        engine.evaluate("invalid_profile_string", EligibilityCriteria())  # type: ignore


def test_invalid_criteria_type_raises_type_error(engine: RuleEngineService) -> None:
    """Non-EligibilityCriteria and non-dict criteria raises TypeError."""
    with pytest.raises(TypeError):
        engine.evaluate(UserProfile(), 12345)  # type: ignore


def test_malformed_dict_profile_raises_value_error(engine: RuleEngineService) -> None:
    """Malformed profile dictionary raises ValueError."""
    with pytest.raises(ValueError, match="Malformed UserProfile"):
        engine.evaluate({"age": -10}, EligibilityCriteria())


def test_malformed_dict_criteria_raises_value_error(engine: RuleEngineService) -> None:
    """Malformed criteria dictionary raises ValueError."""
    with pytest.raises(ValueError, match="Malformed EligibilityCriteria"):
        engine.evaluate(UserProfile(), {"all_of": [{"field": "unknown_field"}]})


def test_invalid_criterion_instance_raises_type_error(
    engine: RuleEngineService,
) -> None:
    """Invalid criterion object in evaluate_criterion raises TypeError."""
    with pytest.raises(TypeError):
        engine.evaluate_criterion(UserProfile(), "not_a_criterion")  # type: ignore


# ==============================================================================
# 11. Determinism: Same Input Always Gives Same Result
# ==============================================================================


def test_evaluation_determinism(engine: RuleEngineService) -> None:
    """Evaluating identical profile and criteria 20 times produces identical results."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE, op=CriterionOperator.BETWEEN, value=[18, 35]
            ),
            Criterion(
                field=CriterionField.ANNUAL_INCOME,
                op=CriterionOperator.LTE,
                value=250000.0,
            ),
            Criterion(
                field=CriterionField.OCCUPATION, op=CriterionOperator.EQ, value="farmer"
            ),
        ]
    )
    profile = UserProfile(age=28, annual_income=200000.0, occupation=Occupation.FARMER)

    baseline = engine.evaluate(profile, crit)
    for _ in range(20):
        repeat = engine.evaluate(profile, crit)
        assert repeat.status == baseline.status
        assert repeat.passed_conditions == baseline.passed_conditions
        assert repeat.failed_conditions == baseline.failed_conditions
        assert repeat.missing_fields == baseline.missing_fields


# ==============================================================================
# 12. Age "as on" a Cut-off Date (Past and Future)
# ==============================================================================


def test_age_as_on_past_cutoff_whole_range_passes(engine: RuleEngineService) -> None:
    """Past cut-off date where entire possible age range qualifies."""
    # Ref: 2026-10-31, Age: 25 -> on 2024-01-01, possible ages are {22, 23}
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.GTE,
                value=18,
                as_on=date(2024, 1, 1),
            )
        ]
    )
    profile = UserProfile(age=25)
    res = engine.evaluate(profile, crit, reference_date=date(2026, 10, 31))
    assert res.status == EligibilityStatus.ELIGIBLE
    assert len(res.passed_conditions) == 1
    assert "✓" in res.passed_conditions[0]


def test_age_as_on_past_cutoff_whole_range_fails(engine: RuleEngineService) -> None:
    """Past cut-off date where entire possible age range fails."""
    # Ref: 2026-10-31, Age: 25 -> on 2024-01-01, possible ages are {22, 23}
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.GTE,
                value=25,
                as_on=date(2024, 1, 1),
            )
        ]
    )
    profile = UserProfile(age=25)
    res = engine.evaluate(profile, crit, reference_date=date(2026, 10, 31))
    assert res.status == EligibilityStatus.NOT_ELIGIBLE
    assert len(res.failed_conditions) == 1
    assert "✗" in res.failed_conditions[0]


def test_age_as_on_past_cutoff_straddles_boundary(engine: RuleEngineService) -> None:
    """Past cut-off date where age range straddles boundary -> maybe."""
    # Ref: 2026-10-31, Age: 25 -> on 2024-01-01, possible ages are {22, 23}
    # 23 passes GTE 23, 22 fails GTE 23 -> straddles!
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.GTE,
                value=23,
                as_on=date(2024, 1, 1),
            )
        ]
    )
    profile = UserProfile(age=25)
    res = engine.evaluate(profile, crit, reference_date=date(2026, 10, 31))
    assert res.status == EligibilityStatus.MAYBE
    assert "age" in res.missing_fields
    assert len(res.failed_conditions) == 0


def test_age_as_on_future_cutoff_whole_range_passes(engine: RuleEngineService) -> None:
    """Future cut-off date where entire possible age range qualifies."""
    # Ref: 2026-10-31, Age: 20 -> on 2028-06-01, possible ages are {21, 22}
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.GTE,
                value=18,
                as_on=date(2028, 6, 1),
            )
        ]
    )
    profile = UserProfile(age=20)
    res = engine.evaluate(profile, crit, reference_date=date(2026, 10, 31))
    assert res.status == EligibilityStatus.ELIGIBLE
    assert len(res.passed_conditions) == 1


def test_age_as_on_future_cutoff_whole_range_fails(engine: RuleEngineService) -> None:
    """Future cut-off date where entire possible age range fails."""
    # Ref: 2026-10-31, Age: 20 -> on 2028-06-01, possible ages are {21, 22}
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.LTE,
                value=20,
                as_on=date(2028, 6, 1),
            )
        ]
    )
    profile = UserProfile(age=20)
    res = engine.evaluate(profile, crit, reference_date=date(2026, 10, 31))
    assert res.status == EligibilityStatus.NOT_ELIGIBLE
    assert len(res.failed_conditions) == 1


def test_age_as_on_future_cutoff_straddles_boundary(engine: RuleEngineService) -> None:
    """Future cut-off date where age range straddles boundary -> maybe."""
    # Ref: 2026-10-31, Age: 20 -> on 2028-06-01, possible ages are {21, 22}
    # 22 passes GTE 22, 21 fails GTE 22 -> straddles!
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.GTE,
                value=22,
                as_on=date(2028, 6, 1),
            )
        ]
    )
    profile = UserProfile(age=20)
    res = engine.evaluate(profile, crit, reference_date=date(2026, 10, 31))
    assert res.status == EligibilityStatus.MAYBE
    assert "age" in res.missing_fields


def test_criteria_level_as_on_date(engine: RuleEngineService) -> None:
    """Cut-off date specified at EligibilityCriteria level applies to age criteria."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.BETWEEN,
                value=[20, 30],
            )
        ],
        as_on=date(2025, 6, 1),
    )
    # Citizen is currently 25 -> on 2025-06-01, possible ages {23, 24}
    p = UserProfile(age=25)
    res = engine.evaluate(p, crit, reference_date=date(2026, 10, 31))
    assert res.status == EligibilityStatus.ELIGIBLE


def test_as_on_iso_string_conversion_and_malformed_validation() -> None:
    """Pydantic converts valid ISO strings to date and rejects malformed strings."""
    # Valid ISO string converts to date
    c = Criterion(
        field=CriterionField.AGE,
        op=CriterionOperator.GTE,
        value=18,
        as_on="2026-01-01",  # type: ignore[arg-type]
    )
    assert isinstance(c.as_on, date)
    assert c.as_on == date(2026, 1, 1)

    # Malformed string raises ValidationError on Criterion
    with pytest.raises(ValidationError):
        Criterion(
            field=CriterionField.AGE,
            op=CriterionOperator.GTE,
            value=18,
            as_on="not-a-valid-date",  # type: ignore[arg-type]
        )

    # Malformed string raises ValidationError on EligibilityCriteria
    with pytest.raises(ValidationError):
        EligibilityCriteria(as_on="invalid-year-format")  # type: ignore[arg-type]


# ==============================================================================
# 13. Bilingual Templates (English and Hindi)
# ==============================================================================


def test_bilingual_reason_generation(engine: RuleEngineService) -> None:
    """Reason templates in English and Hindi match formatting expectations."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.BETWEEN,
                value=[18, 30],
            ),
            Criterion(
                field=CriterionField.ANNUAL_INCOME,
                op=CriterionOperator.LTE,
                value=300000.0,
            ),
        ]
    )
    profile = UserProfile(age=22, annual_income=250000.0)

    # English evaluation (default)
    res_en = engine.evaluate(profile, crit, lang="en")
    assert res_en.status == EligibilityStatus.ELIGIBLE
    assert "Age 18 to 30: your age is 22 ✓" in res_en.passed_conditions
    assert (
        "Annual income up to ₹300,000: your income is ₹250,000 ✓"
        in res_en.passed_conditions
    )

    # Hindi evaluation
    res_hi = engine.evaluate(profile, crit, lang="hi")
    assert res_hi.status == EligibilityStatus.ELIGIBLE
    assert "आयु 18 से 30: आपकी आयु 22 है ✓" in res_hi.passed_conditions
    assert "वार्षिक आय अधिकतम ₹300,000: आपकी आय ₹250,000 है ✓" in res_hi.passed_conditions


def test_bilingual_reason_failure(engine: RuleEngineService) -> None:
    """Failed condition reason strings in English and Hindi."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.BETWEEN,
                value=[18, 30],
            )
        ]
    )
    profile = UserProfile(age=35)

    res_en = engine.evaluate(profile, crit, lang="en")
    assert "Age 18 to 30: your age is 35 ✗" in res_en.failed_conditions

    res_hi = engine.evaluate(profile, crit, lang="hi")
    assert "आयु 18 से 30: आपकी आयु 35 है ✗" in res_hi.failed_conditions


# ==============================================================================
# 14. Edge Cases, Coverage & Helper Function Tests
# ==============================================================================


def test_age_as_on_without_age_yields_unknown(
    engine: RuleEngineService,
) -> None:
    """Age criterion with cut-off date when age is omitted yields unknown."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(
                field=CriterionField.AGE,
                op=CriterionOperator.GTE,
                value=18,
                as_on=date(2026, 1, 1),
            )
        ]
    )
    profile = UserProfile(age=None)
    res = engine.evaluate(profile, crit)
    assert res.status == EligibilityStatus.MAYBE
    assert "age" in res.missing_fields


def test_prefilter_and_evaluate_with_dict_inputs(engine: RuleEngineService) -> None:
    """Passing dicts instead of model instances for profile and scheme."""
    scheme = _create_sample_scheme(level=SchemeLevel.STATE, state="punjab")
    # Prefilter with dict profile
    filtered = engine.prefilter_schemes([scheme], {"state": "punjab"})  # type: ignore
    assert len(filtered) == 1

    # Evaluate with dict profile and dict scheme
    res = engine.evaluate_scheme({"state": "punjab"}, scheme.model_dump())  # type: ignore
    assert res.status == EligibilityStatus.ELIGIBLE


def test_non_income_lte_and_non_age_gte(engine: RuleEngineService) -> None:
    """Test LTE on age and GTE on income to verify general numeric paths."""
    crit = EligibilityCriteria(
        all_of=[
            Criterion(field=CriterionField.AGE, op=CriterionOperator.LTE, value=40),
            Criterion(
                field=CriterionField.ANNUAL_INCOME,
                op=CriterionOperator.GTE,
                value=50000.0,
            ),
        ]
    )
    res_pass = engine.evaluate(UserProfile(age=30, annual_income=60000.0), crit)
    assert res_pass.status == EligibilityStatus.ELIGIBLE

    # LTE unknown on age
    res_unknown = engine.evaluate(UserProfile(age=None, annual_income=60000.0), crit)
    assert res_unknown.status == EligibilityStatus.MAYBE


def test_eval_operator_unsupported_raises_error() -> None:
    """_eval_operator with invalid operator string raises ValueError."""
    from app.services.rule_engine import _eval_operator

    with pytest.raises(ValueError, match="Unsupported CriterionOperator"):
        _eval_operator("unknown_op", 10, 10)  # type: ignore


def test_formatting_helpers_edge_cases() -> None:
    """Test format_value_en and format_value_hi for floats, bools, and none."""
    from app.services.rule_engine import (
        _format_value_en,
        _format_value_hi,
    )

    assert _format_value_en(None) == "not provided"
    assert _format_value_hi(None) == "जानकारी नहीं दी गई"
    assert _format_value_en(1500.5) == "1,500.50"
    assert _format_value_hi(1500.5) == "1,500.50"
    assert _format_value_en(1500.0) == "1,500"
    assert _format_value_hi(1500.0) == "1,500"
    assert _format_value_en(True) == "Yes"
    assert _format_value_hi(True) == "हाँ"
    assert _format_value_en(False) == "No"
    assert _format_value_hi(False) == "नहीं"
