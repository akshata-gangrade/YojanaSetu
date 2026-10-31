"""Unit tests for the follow-up question selector service.

Product rules:
- Pure Python. No LLM, no database, no network, no randomness.
- Given the profile and candidate "maybe" schemes, selects the single missing field
  appearing in the most candidates, breaks ties by fixed priority order,
  and provides plain-language questions in English and Hindi.
"""

from datetime import UTC, datetime

import pytest

from app.schemas.criteria import Criterion, EligibilityCriteria
from app.schemas.enums import (
    CriterionField,
    CriterionOperator,
    SchemeLevel,
    SocialCategory,
)
from app.schemas.scheme import SchemeBase
from app.schemas.user_profile import UserProfile
from app.services.followup_selector import (
    FIELD_PRIORITY_ORDER,
    FollowupSelectorService,
)
from app.services.rule_engine import (
    EligibilityResult,
    EligibilityStatus,
)


@pytest.fixture
def selector() -> FollowupSelectorService:
    """FollowupSelectorService instance fixture."""
    return FollowupSelectorService()


def _make_scheme(
    slug: str,
    criteria: EligibilityCriteria,
    level: SchemeLevel = SchemeLevel.CENTRAL,
    state: str | None = None,
) -> SchemeBase:
    """Helper creating valid SchemeBase fixture."""
    return SchemeBase(
        slug=slug,
        name=f"Scheme {slug}",
        name_hi=f"योजना {slug}",
        level=level,
        state=state,
        benefit_summary="Assistance benefit text description.",
        benefit_summary_hi="सहायता लाभ विवरण।",
        eligibility_criteria=criteria,
        apply_url="https://example.gov.in/apply",
        source_url="https://example.gov.in/source",
        source_hash="b" * 64,
        last_verified=datetime.now(UTC),
    )


# ==============================================================================
# Frequency and Priority Selection Tests
# ==============================================================================


def test_select_followup_highest_frequency(selector: FollowupSelectorService) -> None:
    """Selects the single field appearing in the most candidate 'maybe' schemes."""
    # Scheme 1 needs age and annual_income
    s1 = _make_scheme(
        "scheme-1",
        EligibilityCriteria(
            all_of=[
                Criterion(field=CriterionField.AGE, op=CriterionOperator.GTE, value=18),
                Criterion(
                    field=CriterionField.ANNUAL_INCOME,
                    op=CriterionOperator.LTE,
                    value=200000.0,
                ),
            ]
        ),
    )
    # Scheme 2 needs annual_income and occupation
    s2 = _make_scheme(
        "scheme-2",
        EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.ANNUAL_INCOME,
                    op=CriterionOperator.LTE,
                    value=300000.0,
                ),
                Criterion(
                    field=CriterionField.OCCUPATION,
                    op=CriterionOperator.EQ,
                    value="farmer",
                ),
            ]
        ),
    )
    # Scheme 3 needs annual_income and gender
    s3 = _make_scheme(
        "scheme-3",
        EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.ANNUAL_INCOME,
                    op=CriterionOperator.LTE,
                    value=250000.0,
                ),
                Criterion(
                    field=CriterionField.GENDER, op=CriterionOperator.EQ, value="female"
                ),
            ]
        ),
    )

    # Empty profile: all fields unknown
    # annual_income appears in 3 schemes, others appear in 1
    profile = UserProfile()
    q = selector.select_followup(profile, [s1, s2, s3])

    assert q is not None
    assert q.field == "annual_income"
    assert q.count == 3
    assert "income" in q.question_en.lower()
    assert "वार्षिक आय" in q.question_hi


def test_select_followup_breaks_ties_by_priority(
    selector: FollowupSelectorService,
) -> None:
    """When fields have identical frequency, ties are broken by fixed priority."""
    # Scheme 1 needs social_category (priority idx 5) and state (priority idx 2)
    s1 = _make_scheme(
        "scheme-1",
        EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.SOCIAL_CATEGORY,
                    op=CriterionOperator.EQ,
                    value="sc",
                ),
                Criterion(
                    field=CriterionField.STATE, op=CriterionOperator.EQ, value="bihar"
                ),
            ]
        ),
    )
    # Scheme 2 needs social_category and state
    s2 = _make_scheme(
        "scheme-2",
        EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.SOCIAL_CATEGORY,
                    op=CriterionOperator.EQ,
                    value="st",
                ),
                Criterion(
                    field=CriterionField.STATE, op=CriterionOperator.EQ, value="bihar"
                ),
            ]
        ),
    )

    # Both social_category and state appear in 2 schemes.
    # In FIELD_PRIORITY_ORDER, "state" (idx 2) precedes "social_category" (idx 5).
    profile = UserProfile()
    q = selector.select_followup(profile, [s1, s2])

    assert q is not None
    assert q.field == "state"
    assert q.count == 2
    assert "state" in q.question_en.lower()


def test_select_followup_priority_age_over_all(
    selector: FollowupSelectorService,
) -> None:
    """Age is highest priority (index 0) in tie-breaking."""
    s1 = _make_scheme(
        "scheme-1",
        EligibilityCriteria(
            all_of=[
                Criterion(field=CriterionField.AGE, op=CriterionOperator.GTE, value=18),
                Criterion(
                    field=CriterionField.OCCUPATION,
                    op=CriterionOperator.EQ,
                    value="farmer",
                ),
            ]
        ),
    )
    profile = UserProfile()
    q = selector.select_followup(profile, [s1])
    assert q is not None
    assert q.field == "age"
    assert q.count == 1


# ==============================================================================
# Filtering Already-Answered Fields
# ==============================================================================


def test_already_known_fields_are_not_selected(
    selector: FollowupSelectorService,
) -> None:
    """Fields the user already answered are excluded from follow-up selection."""
    s1 = _make_scheme(
        "scheme-1",
        EligibilityCriteria(
            all_of=[
                Criterion(field=CriterionField.AGE, op=CriterionOperator.GTE, value=18),
                Criterion(
                    field=CriterionField.ANNUAL_INCOME,
                    op=CriterionOperator.LTE,
                    value=200000.0,
                ),
            ]
        ),
    )
    # Citizen already provided age=22 (known), but annual_income is omitted (unknown)
    profile = UserProfile(age=22, annual_income=None)
    q = selector.select_followup(profile, [s1])

    assert q is not None
    assert q.field == "annual_income"
    assert q.count == 1


def test_prefer_not_to_say_field_is_eligible_for_followup(
    selector: FollowupSelectorService,
) -> None:
    """prefer_not_to_say fields evaluate to unknown and qualify for follow-up."""
    s1 = _make_scheme(
        "scheme-1",
        EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.SOCIAL_CATEGORY,
                    op=CriterionOperator.EQ,
                    value="obc",
                ),
            ]
        ),
    )
    profile = UserProfile(social_category=SocialCategory.PREFER_NOT_TO_SAY)
    q = selector.select_followup(profile, [s1])
    assert q is not None
    assert q.field == "social_category"


# ==============================================================================
# Non-Maybe Schemes and Empty Input Handling
# ==============================================================================


def test_empty_candidates_returns_none(selector: FollowupSelectorService) -> None:
    """Passing empty sequence of candidate schemes returns None."""
    assert selector.select_followup(UserProfile(), []) is None


def test_fully_eligible_schemes_generate_no_followup(
    selector: FollowupSelectorService,
) -> None:
    """Candidates where citizen is already eligible produce no follow-up."""
    s1 = _make_scheme(
        "scheme-1",
        EligibilityCriteria(
            all_of=[
                Criterion(field=CriterionField.AGE, op=CriterionOperator.GTE, value=18),
            ]
        ),
    )
    profile = UserProfile(age=25)
    # Age is known and satisfied -> scheme status is ELIGIBLE -> no follow-up needed
    q = selector.select_followup(profile, [s1])
    assert q is None


def test_not_eligible_schemes_generate_no_followup(
    selector: FollowupSelectorService,
) -> None:
    """Candidates where citizen is disqualified produce no follow-up."""
    s1 = _make_scheme(
        "scheme-1",
        EligibilityCriteria(
            all_of=[
                Criterion(field=CriterionField.AGE, op=CriterionOperator.GTE, value=21),
                Criterion(
                    field=CriterionField.ANNUAL_INCOME,
                    op=CriterionOperator.LTE,
                    value=100000.0,
                ),
            ]
        ),
    )
    # Age 16 fails age condition -> status NOT_ELIGIBLE (even though income is unknown)
    profile = UserProfile(age=16, annual_income=None)
    q = selector.select_followup(profile, [s1])
    assert q is None


# ==============================================================================
# Direct Input Types (EligibilityResult, Tuple, Dict)
# ==============================================================================


def test_select_followup_from_eligibility_results(
    selector: FollowupSelectorService,
) -> None:
    """Directly passing EligibilityResult objects."""
    res1 = EligibilityResult(
        status=EligibilityStatus.MAYBE,
        missing_fields=["age", "state"],
    )
    res2 = EligibilityResult(
        status=EligibilityStatus.MAYBE,
        missing_fields=["state", "occupation"],
    )
    res3 = EligibilityResult(
        status=EligibilityStatus.NOT_ELIGIBLE,
        missing_fields=["gender"],
    )
    profile = UserProfile()
    q = selector.select_followup(profile, [res1, res2, res3])

    assert q is not None
    assert q.field == "state"
    assert q.count == 2


def test_select_followup_from_tuples(selector: FollowupSelectorService) -> None:
    """Passing tuples of (Scheme, EligibilityResult)."""
    s = _make_scheme("scheme-1", EligibilityCriteria())
    res = EligibilityResult(
        status=EligibilityStatus.MAYBE,
        missing_fields=["annual_income"],
    )
    profile = UserProfile()
    q = selector.select_followup(profile, [(s, res)])

    assert q is not None
    assert q.field == "annual_income"
    assert q.count == 1


def test_select_missing_field_convenience_method(
    selector: FollowupSelectorService,
) -> None:
    """select_missing_field returns string name or None."""
    s = _make_scheme(
        "scheme-1",
        EligibilityCriteria(
            all_of=[
                Criterion(field=CriterionField.AGE, op=CriterionOperator.GTE, value=18)
            ]
        ),
    )
    assert selector.select_missing_field(UserProfile(), [s]) == "age"
    assert selector.select_missing_field(UserProfile(age=20), [s]) is None


def test_all_profile_fields_have_bilingual_questions(
    selector: FollowupSelectorService,
) -> None:
    """Every field in FIELD_PRIORITY_ORDER has both English and Hindi questions."""
    for field in FIELD_PRIORITY_ORDER:
        q_en, q_hi = selector.get_question_for_field(field)
        assert len(q_en) > 5
        assert len(q_hi) > 5
        assert "?" in q_en or "." in q_en
        assert "?" in q_hi or "।" in q_hi
