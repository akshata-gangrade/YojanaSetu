"""Unit tests for backend/scripts/import_schemes.py using FakeSchemeRepository."""

import json
from pathlib import Path
import tempfile

import pytest

from app.repositories.fakes import FakeSchemeRepository
from app.schemas.enums import SchemeLevel, SchemeStatus
from app.schemas.scheme import SchemeCreate
from scripts.import_schemes import run_import


@pytest.fixture
def sample_valid_scheme_dict() -> dict:
    return {
        "slug": "valid-test-scheme-1",
        "name": "Valid Test Scheme 1",
        "name_hi": "वैध टेस्ट योजना 1",
        "level": "central",
        "state": None,
        "category_tags": ["agriculture"],
        "benefit_summary": "Financial support of Rs 6,000 per year.",
        "benefit_summary_hi": "प्रति वर्ष ₹6,000 की वित्तीय सहायता।",
        "eligibility_criteria": {
            "all_of": [{"field": "occupation", "op": "eq", "value": "farmer"}]
        },
        "required_documents": ["Land Record"],
        "application_steps": ["Apply online"],
        "apply_url": "https://agri.gov.in/apply",
        "source_url": "https://agri.gov.in/guidelines.pdf",
        "source_hash": "a" * 64,
        "status": "verified",  # Invariant check: should be forced to needs_review!
        "last_verified": "2026-11-01T00:00:00Z",
        "is_sample": True,
    }


@pytest.mark.asyncio
async def test_import_template_json_validates_successfully():
    """Verify backend/data/scheme_drafts/template.json validates with 100% success."""
    fake_repo = FakeSchemeRepository()
    template_path = Path(__file__).parents[2] / "data" / "scheme_drafts" / "template.json"
    assert template_path.is_file()

    stats = await run_import(file_path=template_path, apply=True, scheme_repo=fake_repo)
    assert stats["total"] >= 1
    assert stats["invalid"] == 0
    assert stats["valid"] == stats["total"]
    assert stats["created"] == stats["total"]


@pytest.mark.asyncio
async def test_import_schemes_dry_run_default(sample_valid_scheme_dict):
    """Dry run validates and reports counts without writing to the repository."""
    fake_repo = FakeSchemeRepository()

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump([sample_valid_scheme_dict], f)
        temp_path = f.name

    try:
        stats = await run_import(file_path=temp_path, apply=False, scheme_repo=fake_repo)
        assert stats["total"] == 1
        assert stats["valid"] == 1
        assert stats["invalid"] == 0
        assert stats["created"] == 1  # Planned creation

        # Invariant: Nothing committed to repository in dry run
        existing = await fake_repo.get_by_slug("valid-test-scheme-1")
        assert existing is None
    finally:
        Path(temp_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_import_schemes_apply_creates_needs_review(sample_valid_scheme_dict):
    """When --apply is passed, creates scheme with status strictly forced to needs_review."""
    fake_repo = FakeSchemeRepository()

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump([sample_valid_scheme_dict], f)
        temp_path = f.name

    try:
        stats = await run_import(file_path=temp_path, apply=True, scheme_repo=fake_repo)
        assert stats["total"] == 1
        assert stats["valid"] == 1
        assert stats["created"] == 1

        created = await fake_repo.get_by_slug("valid-test-scheme-1")
        assert created is not None
        assert created.name == "Valid Test Scheme 1"
        # Invariant: Must NEVER be set to verified upon import
        assert created.status == SchemeStatus.NEEDS_REVIEW
        assert created.verified_by is None
        assert created.verified_at is None
    finally:
        Path(temp_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_import_schemes_skip_existing_unless_update(sample_valid_scheme_dict):
    """Existing slugs are skipped by default, and updated when update=True."""
    fake_repo = FakeSchemeRepository()

    # Pre-seed existing scheme
    pre_existing = SchemeCreate.model_validate(sample_valid_scheme_dict)
    pre_existing.benefit_summary = "Old benefit summary text here."
    await fake_repo.create_scheme(pre_existing)

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        # File has updated benefit summary
        updated_dict = dict(sample_valid_scheme_dict)
        updated_dict["benefit_summary"] = "New updated benefit summary text."
        json.dump([updated_dict], f)
        temp_path = f.name

    try:
        # 1. Without update flag: skipped
        stats_skip = await run_import(
            file_path=temp_path, apply=True, update=False, scheme_repo=fake_repo
        )
        assert stats_skip["skipped"] == 1
        current = await fake_repo.get_by_slug("valid-test-scheme-1")
        assert current.benefit_summary == "Old benefit summary text here."

        # 2. With update flag: updated
        stats_update = await run_import(
            file_path=temp_path, apply=True, update=True, scheme_repo=fake_repo
        )
        assert stats_update["updated"] == 1
        updated = await fake_repo.get_by_slug("valid-test-scheme-1")
        assert updated.benefit_summary == "New updated benefit summary text."
        assert updated.status == SchemeStatus.NEEDS_REVIEW
    finally:
        Path(temp_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_import_schemes_validation_errors_dont_stop_processing(sample_valid_scheme_dict):
    """Invalid items print precise field errors without stopping processing of valid items."""
    fake_repo = FakeSchemeRepository()

    invalid_scheme_1 = {
        "slug": "INVALID SLUG WITH SPACES",  # Invalid regex pattern
        "name": "X",  # Too short
        "level": "central",
        "state": "madhya_pradesh",  # Invariant error: central schemes cannot have state
        "apply_url": "ftp://bad-scheme.com",  # Not http/https
        "source_url": "https://gov.in",
        "source_hash": "short",  # Too short (<16 chars)
        "benefit_summary": "Too short",  # <10 chars
    }

    valid_scheme_2 = dict(sample_valid_scheme_dict)
    valid_scheme_2["slug"] = "valid-test-scheme-2"
    valid_scheme_2["name"] = "Valid Test Scheme 2"

    items = [invalid_scheme_1, valid_scheme_2]

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(items, f)
        temp_path = f.name

    try:
        stats = await run_import(file_path=temp_path, apply=True, scheme_repo=fake_repo)
        assert stats["total"] == 2
        assert stats["invalid"] == 1
        assert stats["valid"] == 1
        assert stats["created"] == 1

        # Valid scheme was created despite earlier item failing validation
        assert await fake_repo.get_by_slug("valid-test-scheme-2") is not None
    finally:
        Path(temp_path).unlink(missing_ok=True)


class FailingWriteSchemeRepository(FakeSchemeRepository):
    """Fake repository that simulates write failure for a specific slug."""

    def __init__(self, fail_slug: str):
        super().__init__()
        self.fail_slug = fail_slug

    async def create_scheme(self, scheme: SchemeCreate):
        if scheme.slug == self.fail_slug:
            raise RuntimeError(f"Database write failed for {scheme.slug}: Simulated write conflict")
        return await super().create_scheme(scheme)


@pytest.mark.asyncio
async def test_import_schemes_write_failure_does_not_abort_others(
    sample_valid_scheme_dict: dict,
    capsys: pytest.CaptureFixture,
) -> None:
    """Item 3: One write failure never aborts others. Print slug, keep going, report counts."""
    failing_repo = FailingWriteSchemeRepository(fail_slug="failing-scheme-1")

    item1 = dict(sample_valid_scheme_dict)
    item1["slug"] = "failing-scheme-1"
    item1["name"] = "Failing Scheme 1"

    item2 = dict(sample_valid_scheme_dict)
    item2["slug"] = "succeeding-scheme-2"
    item2["name"] = "Succeeding Scheme 2"

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump([item1, item2], f)
        temp_path = f.name

    try:
        stats = await run_import(
            file_path=temp_path,
            apply=True,
            scheme_repo=failing_repo,
        )

        # First item failed write, second item succeeded
        assert stats["total"] == 2
        assert stats["valid"] == 2
        assert stats["created"] == 1
        assert stats["failed"] == 1

        # Second scheme was successfully inserted
        assert await failing_repo.get_by_slug("succeeding-scheme-2") is not None

        # Verify console output
        captured = capsys.readouterr()
        err_out = captured.err
        std_out = captured.out

        # Printed slug and short error
        assert "failing-scheme-1" in err_out or "failing-scheme-1" in std_out
        assert "Simulated write conflict" in err_out or "Simulated write conflict" in std_out

        # Counts for created, updated, skipped, and failed are shown
        assert "Created         : 1" in std_out
        assert "Failed          : 1" in std_out
        assert "Skipped         : 0" in std_out
        assert "Updated         : 0" in std_out

        # Invariant: Never prints connection string
        assert "mongodb://" not in std_out
        assert "mongodb://" not in err_out
    finally:
        Path(temp_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_import_schemes_async_main_exits_nonzero_on_failure(
    sample_valid_scheme_dict: dict,
) -> None:
    """Item 3: _async_main returns non-zero when any item fails."""
    from scripts.import_schemes import _async_main
    from unittest.mock import MagicMock

    failing_repo = FailingWriteSchemeRepository(fail_slug="fail-item")

    item = dict(sample_valid_scheme_dict)
    item["slug"] = "fail-item"

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump([item], f)
        temp_path = f.name

    try:
        mock_args = MagicMock()
        mock_args.file = temp_path
        mock_args.apply = True
        mock_args.update = False

        # Run with failing write
        with pytest.MonkeyPatch.context() as mp:
            from scripts import import_schemes
            mp.setattr(import_schemes, "SchemeRepository", lambda db: failing_repo)
            exit_code = await _async_main(mock_args)
            assert exit_code != 0
    finally:
        Path(temp_path).unlink(missing_ok=True)

