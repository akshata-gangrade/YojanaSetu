"""Unit tests for backend/scripts/review_schemes.py using FakeSchemeRepository and FakeAuditRepository."""

from datetime import UTC, datetime

import pytest

from app.repositories.fakes import FakeAuditRepository, FakeSchemeRepository
from app.schemas.criteria import Criterion, EligibilityCriteria
from app.schemas.enums import SchemeLevel, SchemeStatus
from app.schemas.scheme import SchemeCreate
from scripts.review_schemes import format_criteria_tree, format_criterion, run_review


@pytest.fixture
def sample_needs_review_scheme() -> SchemeCreate:
    return SchemeCreate(
        slug="review-test-scheme",
        name="Review Test Scheme",
        name_hi="समीक्षा टेस्ट योजना",
        level=SchemeLevel.CENTRAL,
        state=None,
        category_tags=["pension"],
        benefit_summary="Monthly stipend of Rs 1,000 for senior citizens.",
        benefit_summary_hi="वरिष्ठ नागरिकों के लिए ₹1,000 का मासिक वजीफा।",
        eligibility_criteria=EligibilityCriteria(
            all_of=[
                Criterion(field="age", op="gte", value=60),
                Criterion(field="annual_income", op="lte", value=200000),
            ]
        ),
        required_documents=["Age Proof", "Income Certificate"],
        application_steps=["Apply at portal", "Submit documents"],
        apply_url="https://pension.gov.in",
        source_url="https://pension.gov.in/gazette.pdf",
        source_hash="b" * 64,
        status=SchemeStatus.NEEDS_REVIEW,
        last_verified=datetime.now(UTC),
        is_sample=True,
    )


@pytest.mark.asyncio
async def test_review_verify_action_sets_verified_and_owner_audit(
    sample_needs_review_scheme: SchemeCreate,
):
    """'y' sets verified status, verified_by 'owner', verified_at now, and logs audit entry."""
    fake_scheme_repo = FakeSchemeRepository()
    fake_audit_repo = FakeAuditRepository()

    await fake_scheme_repo.create_scheme(sample_needs_review_scheme)

    # Input sequence returns 'y'
    inputs = iter(["y"])
    stats = await run_review(
        scheme_repo=fake_scheme_repo,
        audit_repo=fake_audit_repo,
        input_func=lambda _: next(inputs),
    )

    assert stats["reviewed"] == 1
    assert stats["verified"] == 1
    assert stats["rejected"] == 0
    assert stats["skipped"] == 0

    # Verify repository state
    scheme = await fake_scheme_repo.get_by_slug("review-test-scheme")
    assert scheme is not None
    assert scheme.status == SchemeStatus.VERIFIED
    assert scheme.verified_by == "owner"
    assert scheme.verified_at is not None
    assert scheme.last_verified is not None

    # Verify audit trail
    logs = await fake_audit_repo.get_by_target("review-test-scheme")
    assert len(logs) == 1
    assert logs[0].actor == "owner"
    assert logs[0].action == "verify_scheme"
    assert logs[0].diff["status"]["old"] == "needs_review"
    assert logs[0].diff["status"]["new"] == "verified"
    assert logs[0].diff["verified_by"]["new"] == "owner"


@pytest.mark.asyncio
async def test_review_reject_action_sets_draft_and_audit(
    sample_needs_review_scheme: SchemeCreate,
):
    """'n' sets draft status and creates an audit log entry."""
    fake_scheme_repo = FakeSchemeRepository()
    fake_audit_repo = FakeAuditRepository()

    await fake_scheme_repo.create_scheme(sample_needs_review_scheme)

    # Input sequence returns 'n'
    inputs = iter(["n"])
    stats = await run_review(
        scheme_repo=fake_scheme_repo,
        audit_repo=fake_audit_repo,
        input_func=lambda _: next(inputs),
    )

    assert stats["reviewed"] == 1
    assert stats["rejected"] == 1
    assert stats["verified"] == 0
    assert stats["skipped"] == 0

    scheme = await fake_scheme_repo.get_by_slug("review-test-scheme")
    assert scheme is not None
    assert scheme.status == SchemeStatus.DRAFT

    logs = await fake_audit_repo.get_by_target("review-test-scheme")
    assert len(logs) == 1
    assert logs[0].actor == "owner"
    assert logs[0].action == "reject_scheme"
    assert logs[0].diff["status"]["new"] == "draft"


@pytest.mark.asyncio
async def test_review_skip_leaves_scheme_untouched(
    sample_needs_review_scheme: SchemeCreate,
):
    """'s' leaves status as needs_review with zero audit entries."""
    fake_scheme_repo = FakeSchemeRepository()
    fake_audit_repo = FakeAuditRepository()

    await fake_scheme_repo.create_scheme(sample_needs_review_scheme)

    # Input sequence returns 's'
    inputs = iter(["s"])
    stats = await run_review(
        scheme_repo=fake_scheme_repo,
        audit_repo=fake_audit_repo,
        input_func=lambda _: next(inputs),
    )

    assert stats["reviewed"] == 1
    assert stats["skipped"] == 1
    assert stats["verified"] == 0

    scheme = await fake_scheme_repo.get_by_slug("review-test-scheme")
    assert scheme is not None
    assert scheme.status == SchemeStatus.NEEDS_REVIEW

    logs = await fake_audit_repo.get_by_target("review-test-scheme")
    assert len(logs) == 0


@pytest.mark.asyncio
async def test_review_single_slug_argument(sample_needs_review_scheme: SchemeCreate):
    """Reviewing with --slug targets only the specified scheme."""
    fake_scheme_repo = FakeSchemeRepository()
    fake_audit_repo = FakeAuditRepository()

    # Create 2 schemes
    await fake_scheme_repo.create_scheme(sample_needs_review_scheme)
    second_scheme = sample_needs_review_scheme.model_copy(
        update={"slug": "other-scheme", "name": "Other Scheme"}
    )
    await fake_scheme_repo.create_scheme(second_scheme)

    inputs = iter(["y"])
    stats = await run_review(
        slug="other-scheme",
        scheme_repo=fake_scheme_repo,
        audit_repo=fake_audit_repo,
        input_func=lambda _: next(inputs),
    )

    assert stats["reviewed"] == 1
    assert stats["verified"] == 1

    other = await fake_scheme_repo.get_by_slug("other-scheme")
    assert other.status == SchemeStatus.VERIFIED

    # First scheme remained in needs_review
    first = await fake_scheme_repo.get_by_slug("review-test-scheme")
    assert first.status == SchemeStatus.NEEDS_REVIEW


def test_format_criteria_tree_readable():
    """Verify criteria tree string formatting displays field, operator, and values clearly."""
    criteria = EligibilityCriteria(
        all_of=[
            Criterion(field="age", op="gte", value=18),
            Criterion(field="annual_income", op="lte", value=500000),
        ],
        any_of=[Criterion(field="occupation", op="in", value=["farmer", "artisan"])],
    )

    lines = format_criteria_tree(criteria)
    full_text = "\n".join(lines)
    assert "age >= 18" in full_text
    assert "occupation in ['farmer', 'artisan']" in full_text
    assert "annual_income <= 500000" in full_text


@pytest.mark.parametrize(
    "answer",
    ["y", "Y", "yes", "YES", "  y  ", "  Yes  ", "  YES  "],
)
@pytest.mark.asyncio
async def test_review_accepts_verify_forms(
    answer: str, sample_needs_review_scheme: SchemeCreate
) -> None:
    """Item 5: Verify accept answers case-insensitively with surrounding spaces for 'y'/'yes'."""
    fake_scheme_repo = FakeSchemeRepository()
    fake_audit_repo = FakeAuditRepository()
    await fake_scheme_repo.create_scheme(sample_needs_review_scheme)

    inputs = iter([answer])
    prompts_seen = []

    def prompt_func(p: str) -> str:
        prompts_seen.append(p)
        return next(inputs)

    stats = await run_review(
        scheme_repo=fake_scheme_repo,
        audit_repo=fake_audit_repo,
        input_func=prompt_func,
    )

    assert stats["verified"] == 1
    assert prompts_seen[0] == "Verify? [y/n/s/q]: "
    scheme = await fake_scheme_repo.get_by_slug("review-test-scheme")
    assert scheme.status == SchemeStatus.VERIFIED


@pytest.mark.parametrize(
    "answer",
    ["n", "N", "no", "NO", "  n  ", "  No  ", "  NO  "],
)
@pytest.mark.asyncio
async def test_review_accepts_reject_forms(
    answer: str, sample_needs_review_scheme: SchemeCreate
) -> None:
    """Item 5: Reject accept answers case-insensitively with surrounding spaces for 'n'/'no'."""
    fake_scheme_repo = FakeSchemeRepository()
    fake_audit_repo = FakeAuditRepository()
    await fake_scheme_repo.create_scheme(sample_needs_review_scheme)

    inputs = iter([answer])
    stats = await run_review(
        scheme_repo=fake_scheme_repo,
        audit_repo=fake_audit_repo,
        input_func=lambda _: next(inputs),
    )

    assert stats["rejected"] == 1
    scheme = await fake_scheme_repo.get_by_slug("review-test-scheme")
    assert scheme.status == SchemeStatus.DRAFT


@pytest.mark.parametrize(
    "answer",
    ["s", "S", "skip", "SKIP", "  s  ", "  Skip  ", "  SKIP  "],
)
@pytest.mark.asyncio
async def test_review_accepts_skip_forms(
    answer: str, sample_needs_review_scheme: SchemeCreate
) -> None:
    """Item 5: Skip accept answers case-insensitively with surrounding spaces for 's'/'skip'."""
    fake_scheme_repo = FakeSchemeRepository()
    fake_audit_repo = FakeAuditRepository()
    await fake_scheme_repo.create_scheme(sample_needs_review_scheme)

    inputs = iter([answer])
    stats = await run_review(
        scheme_repo=fake_scheme_repo,
        audit_repo=fake_audit_repo,
        input_func=lambda _: next(inputs),
    )

    assert stats["skipped"] == 1
    scheme = await fake_scheme_repo.get_by_slug("review-test-scheme")
    assert scheme.status == SchemeStatus.NEEDS_REVIEW


@pytest.mark.parametrize(
    "answer",
    ["q", "Q", "quit", "QUIT", "  q  ", "  Quit  ", "  QUIT  "],
)
@pytest.mark.asyncio
async def test_review_accepts_quit_forms_and_exits_safely(
    answer: str, sample_needs_review_scheme: SchemeCreate
) -> None:
    """Item 5: Quit accept answers case-insensitively with spaces and exits review safely."""
    fake_scheme_repo = FakeSchemeRepository()
    fake_audit_repo = FakeAuditRepository()

    # Pre-seed 2 schemes
    await fake_scheme_repo.create_scheme(sample_needs_review_scheme)
    second_scheme = sample_needs_review_scheme.model_copy(
        update={"slug": "second-scheme", "name": "Second Scheme"}
    )
    await fake_scheme_repo.create_scheme(second_scheme)

    # First scheme quits immediately
    inputs = iter([answer])
    stats = await run_review(
        scheme_repo=fake_scheme_repo,
        audit_repo=fake_audit_repo,
        input_func=lambda _: next(inputs),
    )

    # Exited safely after first scheme without verifying or touching either
    assert stats["reviewed"] == 1
    assert stats["verified"] == 0
    assert stats["rejected"] == 0
    assert stats["skipped"] == 0

    first = await fake_scheme_repo.get_by_slug("review-test-scheme")
    assert first.status == SchemeStatus.NEEDS_REVIEW
    second = await fake_scheme_repo.get_by_slug("second-scheme")
    assert second.status == SchemeStatus.NEEDS_REVIEW


@pytest.mark.asyncio
async def test_review_invalid_input_prints_hint_and_reprompts(
    sample_needs_review_scheme: SchemeCreate,
    capsys: pytest.CaptureFixture,
) -> None:
    """Item 5: For any other input, print one short hint line and ask again."""
    fake_scheme_repo = FakeSchemeRepository()
    fake_audit_repo = FakeAuditRepository()
    await fake_scheme_repo.create_scheme(sample_needs_review_scheme)

    # Sequence: invalid, another invalid, then valid 'y'
    inputs = iter(["maybe", "invalid-cmd", "y"])
    stats = await run_review(
        scheme_repo=fake_scheme_repo,
        audit_repo=fake_audit_repo,
        input_func=lambda _: next(inputs),
    )

    assert stats["verified"] == 1
    captured = capsys.readouterr()
    assert (
        "Please enter 'y'/'yes' to verify, 'n'/'no' to reject, 's'/'skip' to skip, or 'q'/'quit' to exit."
        in captured.out
    )

