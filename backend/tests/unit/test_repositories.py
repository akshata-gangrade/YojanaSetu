"""Unit tests for repository implementations using isolated in-memory test fakes."""

from datetime import UTC, datetime, timedelta

import pytest

from app.repositories.fakes import (
    FakeAdminRepository,
    FakeAuditRepository,
    FakeChunkRepository,
    FakeFeedbackRepository,
    FakeSchemeRepository,
)
from app.schemas.admin import AdminRole, AdminUserCreate
from app.schemas.chunk import ChunkSection, SchemeChunkCreate
from app.schemas.criteria import Criterion, EligibilityCriteria
from app.schemas.enums import (
    CriterionField,
    CriterionOperator,
    FeedbackVote,
    SchemeLevel,
    SchemeStatus,
)
from app.schemas.feedback import FeedbackCreate
from app.schemas.scheme import SchemeCreate, SchemeUpdate

# ==================== Scheme Repository Unit Tests ====================


@pytest.fixture
def sample_scheme_create() -> SchemeCreate:
    """Fixture providing a verified scheme create model."""
    now = datetime.now(UTC)
    return SchemeCreate(
        slug="pm-kisan-test",
        name="PM Kisan Test Scheme",
        name_hi="पीएम किसान टेस्ट योजना",
        level=SchemeLevel.CENTRAL,
        state=None,
        category_tags=["agriculture"],
        benefit_summary="Direct financial support of Rs 6,000 per year.",
        benefit_summary_hi="प्रति वर्ष ₹6,000 की प्रत्यक्ष वित्तीय सहायता।",
        eligibility_criteria=EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.OCCUPATION,
                    op=CriterionOperator.EQ,
                    value="farmer",
                )
            ]
        ),
        required_documents=["Land Record"],
        application_steps=["Apply online at portal"],
        apply_url="https://pmkisan.gov.in",
        source_url="https://pmkisan.gov.in/guidelines.pdf",
        source_hash="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        status=SchemeStatus.VERIFIED,
        verified_by="admin@internal.gov",
        verified_at=now,
        last_verified=now,
        is_sample=False,
    )


@pytest.mark.asyncio
async def test_scheme_repo_create_and_get_by_slug(
    sample_scheme_create: SchemeCreate,
) -> None:
    """Test inserting and retrieving a scheme by its unique slug."""
    repo = FakeSchemeRepository()
    created = await repo.create_scheme(sample_scheme_create)

    assert created.slug == "pm-kisan-test"
    assert created.id is not None

    retrieved = await repo.get_by_slug("pm-kisan-test")
    assert retrieved is not None
    assert retrieved.name == "PM Kisan Test Scheme"

    missing = await repo.get_by_slug("non-existent-slug")
    assert missing is None


@pytest.mark.asyncio
async def test_scheme_repo_only_returns_verified_schemes(
    sample_scheme_create: SchemeCreate,
) -> None:
    """Invariant: Only schemes with status 'verified' are returned to users."""
    repo = FakeSchemeRepository()

    # 1. Verified scheme
    await repo.create_scheme(sample_scheme_create)

    # 2. Draft scheme (should be excluded)
    draft_scheme = sample_scheme_create.model_copy(
        update={"slug": "draft-scheme", "status": SchemeStatus.DRAFT}
    )
    await repo.create_scheme(draft_scheme)

    # 3. Needs review scheme (should be excluded)
    review_scheme = sample_scheme_create.model_copy(
        update={"slug": "review-scheme", "status": SchemeStatus.NEEDS_REVIEW}
    )
    await repo.create_scheme(review_scheme)

    verified_list = await repo.get_verified_schemes()
    assert len(verified_list) == 1
    assert verified_list[0].slug == "pm-kisan-test"

    count = await repo.count_verified()
    assert count == 1


@pytest.mark.asyncio
async def test_scheme_repo_sample_exclusion_and_purge(
    sample_scheme_create: SchemeCreate,
) -> None:
    """Invariant: Sample schemes (is_sample: true) are excluded from responses."""
    repo = FakeSchemeRepository()

    # Production scheme
    await repo.create_scheme(sample_scheme_create)

    # Sample scheme
    sample = sample_scheme_create.model_copy(
        update={"slug": "sample-scheme-1", "is_sample": True}
    )
    await repo.create_scheme(sample)

    # By default, sample is excluded
    verified_default = await repo.get_verified_schemes(include_samples=False)
    assert len(verified_default) == 1
    assert verified_default[0].slug == "pm-kisan-test"

    # With include_samples=True
    verified_with_samples = await repo.get_verified_schemes(include_samples=True)
    assert len(verified_with_samples) == 2

    # Purge samples
    deleted = await repo.delete_sample_schemes()
    assert deleted == 1

    remaining = await repo.get_verified_schemes(include_samples=True)
    assert len(remaining) == 1
    assert remaining[0].slug == "pm-kisan-test"


@pytest.mark.asyncio
async def test_scheme_repo_respects_include_sample_schemes_setting(
    sample_scheme_create: SchemeCreate,
) -> None:
    """Verify default query filtering respects INCLUDE_SAMPLE_SCHEMES setting."""
    sample = sample_scheme_create.model_copy(
        update={"slug": "sample-scheme-1", "is_sample": True}
    )

    # 1. When INCLUDE_SAMPLE_SCHEMES is False (default)
    repo_default = FakeSchemeRepository(include_sample_schemes=False)
    await repo_default.create_scheme(sample_scheme_create)
    await repo_default.create_scheme(sample)

    results_default = await repo_default.get_verified_schemes()
    assert len(results_default) == 1
    assert results_default[0].slug == "pm-kisan-test"
    assert await repo_default.count_verified() == 1

    # 2. When INCLUDE_SAMPLE_SCHEMES is True
    repo_enabled = FakeSchemeRepository(include_sample_schemes=True)
    await repo_enabled.create_scheme(sample_scheme_create)
    await repo_enabled.create_scheme(sample)

    results_enabled = await repo_enabled.get_verified_schemes()
    assert len(results_enabled) == 2
    assert await repo_enabled.count_verified() == 2


@pytest.mark.asyncio
async def test_purge_samples_preserves_real_schemes(
    sample_scheme_create: SchemeCreate,
) -> None:
    """Item 4: Confirm purge-samples deletes ONLY samples and real schemes survive."""
    repo = FakeSchemeRepository()

    # 2 Real schemes
    real_scheme_1 = sample_scheme_create.model_copy(
        update={"slug": "real-scheme-alpha", "is_sample": False}
    )
    real_scheme_2 = sample_scheme_create.model_copy(
        update={"slug": "real-scheme-beta", "is_sample": False}
    )
    await repo.create_scheme(real_scheme_1)
    await repo.create_scheme(real_scheme_2)

    # 2 Sample schemes
    sample_scheme_1 = sample_scheme_create.model_copy(
        update={"slug": "sample-scheme-one", "is_sample": True}
    )
    sample_scheme_2 = sample_scheme_create.model_copy(
        update={"slug": "sample-scheme-two", "is_sample": True}
    )
    await repo.create_scheme(sample_scheme_1)
    await repo.create_scheme(sample_scheme_2)

    # Total schemes initially = 4
    all_schemes = await repo.get_verified_schemes(include_samples=True)
    assert len(all_schemes) == 4

    # Execute purge
    deleted_count = await repo.delete_sample_schemes()
    assert deleted_count == 2

    # Verify real schemes survived intact
    alpha = await repo.get_by_slug("real-scheme-alpha")
    beta = await repo.get_by_slug("real-scheme-beta")
    assert alpha is not None and alpha.is_sample is False
    assert beta is not None and beta.is_sample is False

    # Verify sample schemes were completely removed
    assert await repo.get_by_slug("sample-scheme-one") is None
    assert await repo.get_by_slug("sample-scheme-two") is None

    # Remaining verified count
    remaining = await repo.get_verified_schemes(include_samples=True)
    assert len(remaining) == 2


@pytest.mark.asyncio
async def test_scheme_repo_update(sample_scheme_create: SchemeCreate) -> None:
    """Test partial scheme update and timestamp refresh."""
    repo = FakeSchemeRepository()
    await repo.create_scheme(sample_scheme_create)

    update_payload = SchemeUpdate(
        benefit_summary="Updated enhanced benefit description.",
    )
    updated = await repo.update_scheme("pm-kisan-test", update_payload)
    assert updated is not None
    assert updated.benefit_summary == "Updated enhanced benefit description."

    # Update nonexistent scheme returns None
    missing = await repo.update_scheme("does-not-exist", update_payload)
    assert missing is None


# ==================== Chunk Repository Unit Tests ====================


@pytest.mark.asyncio
async def test_chunk_repo_create_retrieve_and_delete() -> None:
    """Test chunk storage, retrieval by scheme, and deletion."""
    repo = FakeChunkRepository()

    chunks = [
        SchemeChunkCreate(
            scheme_id="scheme-abc",
            section=ChunkSection.ELIGIBILITY,
            text="Eligibility criteria: farmers with arable land.",
            embedding=[1.0, 0.0, 0.0],
            source_url="https://example.gov.in/doc.pdf",
            page=1,
        ),
        SchemeChunkCreate(
            scheme_id="scheme-abc",
            section=ChunkSection.BENEFITS,
            text="Benefits: direct financial transfer.",
            embedding=[0.0, 1.0, 0.0],
            source_url="https://example.gov.in/doc.pdf",
            page=2,
        ),
        SchemeChunkCreate(
            scheme_id="scheme-xyz",
            section=ChunkSection.DOCUMENTS,
            text="Documents for scheme xyz.",
            embedding=[0.0, 0.0, 1.0],
            source_url="https://example.gov.in/xyz.pdf",
            page=1,
        ),
    ]

    ids = await repo.create_chunks(chunks)
    assert len(ids) == 3

    # Retrieve by scheme
    abc_chunks = await repo.get_chunks_by_scheme_id("scheme-abc")
    assert len(abc_chunks) == 2

    # Vector search with cosine similarity
    query_vector = [0.99, 0.01, 0.0]
    results = await repo.vector_search(query_vector=query_vector, limit=2)
    assert len(results) == 2
    assert results[0].section == ChunkSection.ELIGIBILITY
    assert results[0].score is not None and results[0].score > 0.9

    # Delete by scheme
    deleted_count = await repo.delete_chunks_by_scheme_id("scheme-abc")
    assert deleted_count == 2
    remaining = await repo.get_chunks_by_scheme_id("scheme-abc")
    assert len(remaining) == 0


# ==================== Admin Repository Unit Tests ====================


@pytest.mark.asyncio
async def test_admin_repo_lifecycle_and_lockout() -> None:
    """Test admin creation, case-insensitive fetch, lockout tracking, and reset."""
    repo = FakeAdminRepository()

    admin = AdminUserCreate(
        email="Reviewer.One@YojanaSetu.gov.in",
        password_hash="$2b$12$e80yV9u5ZlP4aP.sXQZ2Eep0uK7B5b8pXq...",
        role=AdminRole.ADMIN,
    )
    created = await repo.create_admin(admin)
    assert created.email == "reviewer.one@yojanasetu.gov.in"

    # Case-insensitive fetch
    found = await repo.get_by_email("REVIEWER.ONE@yojanasetu.gov.in")
    assert found is not None
    assert found.role == AdminRole.ADMIN

    # Update failed login attempts and lockout
    lock_time = datetime.now(UTC) + timedelta(minutes=15)
    updated = await repo.update_login_attempts(
        email="reviewer.one@yojanasetu.gov.in",
        failed_logins=5,
        locked_until=lock_time,
    )
    assert updated is True

    locked_admin = await repo.get_by_email("reviewer.one@yojanasetu.gov.in")
    assert locked_admin is not None
    assert locked_admin.failed_logins == 5
    assert locked_admin.locked_until == lock_time

    # Reset failed logins
    reset_ok = await repo.reset_failed_logins("reviewer.one@yojanasetu.gov.in")
    assert reset_ok is True

    cleared = await repo.get_by_email("reviewer.one@yojanasetu.gov.in")
    assert cleared is not None
    assert cleared.failed_logins == 0
    assert cleared.locked_until is None


# ==================== Audit Repository Unit Tests ====================


@pytest.mark.asyncio
async def test_audit_repo_append_only_and_ordering() -> None:
    """Test append-only audit logging and reverse chronological ordering."""
    repo = FakeAuditRepository()

    # Log 3 events
    await repo.log_event(
        actor="admin@yojanasetu.gov.in",
        action="verify_scheme",
        target="pm-kisan-slug",
        diff={"status": {"old": "needs_review", "new": "verified"}},
    )
    await repo.log_event(
        actor="admin@yojanasetu.gov.in",
        action="update_benefit",
        target="pm-kisan-slug",
        diff={"benefit_summary": {"old": "A", "new": "B"}},
    )
    await repo.log_event(
        actor="admin@yojanasetu.gov.in",
        action="create_scheme",
        target="other-slug",
        diff=None,
    )

    history = await repo.get_by_target("pm-kisan-slug")
    assert len(history) == 2
    assert history[0].action == "update_benefit"
    assert history[1].action == "verify_scheme"

    # Invariant: Verify AuditRepository has no delete or update methods
    assert not hasattr(repo, "delete_event")
    assert not hasattr(repo, "update_event")


# ==================== Feedback Repository Unit Tests ====================


@pytest.mark.asyncio
async def test_feedback_repo_anonymous_entry() -> None:
    """Test recording anonymous feedback and querying by scheme."""
    repo = FakeFeedbackRepository()

    fb1 = FeedbackCreate(
        scheme_id="pm-kisan-test",
        vote=FeedbackVote.HELPFUL,
        comment="Clear criteria breakdown.",
    )
    fb2 = FeedbackCreate(
        scheme_id="pm-kisan-test",
        vote=FeedbackVote.NOT_HELPFUL,
        comment="Application link was slow.",
    )
    await repo.create_feedback(fb1)
    await repo.create_feedback(fb2)

    feedback_list = await repo.get_feedback_by_scheme("pm-kisan-test")
    assert len(feedback_list) == 2
    assert feedback_list[0].vote == FeedbackVote.NOT_HELPFUL
    assert feedback_list[1].vote == FeedbackVote.HELPFUL
