"""Unit tests for Pydantic schema models, invariants, and validators."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.admin import AdminUserCreate
from app.schemas.chunk import SchemeChunkCreate
from app.schemas.criteria import Criterion, EligibilityCriteria
from app.schemas.enums import (
    AdminRole,
    ChunkSection,
    CriterionField,
    CriterionOperator,
    DisabilityStatus,
    EducationLevel,
    FeedbackVote,
    Gender,
    IndianState,
    MaritalStatus,
    Occupation,
    ResidenceType,
    SchemeLevel,
    SchemeStatus,
    SocialCategory,
)
from app.schemas.feedback import FeedbackCreate
from app.schemas.scheme import SchemeCreate
from app.schemas.user_profile import UserProfile

# ==================== UserProfile Tests ====================


def test_user_profile_valid() -> None:
    """Test valid user profile instantiation and helper methods."""
    profile = UserProfile(
        age=28,
        gender=Gender.FEMALE,
        state=IndianState.MAHARASHTRA,
        annual_income=250000.0,
        social_category=SocialCategory.OBC,
        occupation=Occupation.ARTISAN,
        education_level=EducationLevel.GRADUATE,
        residence_type=ResidenceType.RURAL,
        marital_status=MaritalStatus.SINGLE,
        disability_status=DisabilityStatus.NONE,
        is_student=False,
    )
    assert profile.age == 28
    assert profile.gender == Gender.FEMALE
    assert not profile.is_field_unknown("age")
    assert not profile.is_field_unknown("gender")
    assert profile.get_effective_value("state") == "maharashtra"


def test_user_profile_prefer_not_to_say_means_unknown() -> None:
    """Test that prefer_not_to_say or omitted fields evaluate to unknown (None)."""
    profile = UserProfile(
        age=None,
        gender=Gender.PREFER_NOT_TO_SAY,
        social_category=SocialCategory.PREFER_NOT_TO_SAY,
        disability_status=DisabilityStatus.PREFER_NOT_TO_SAY,
    )
    assert profile.is_field_unknown("age")
    assert profile.is_field_unknown("gender")
    assert profile.is_field_unknown("social_category")
    assert profile.is_field_unknown("disability_status")
    assert profile.get_effective_value("gender") is None
    assert profile.get_effective_value("social_category") is None


def test_user_profile_forbids_extra_fields() -> None:
    """Zero-PII invariant: forbidden extra fields raise ValidationError."""
    with pytest.raises(ValidationError):
        UserProfile.model_validate({"age": 25, "aadhaar": "123456789012"})

    with pytest.raises(ValidationError):
        UserProfile.model_validate(
            {"annual_income": 100000.0, "phone": "+919876543210"}
        )

    with pytest.raises(ValidationError):
        UserProfile.model_validate({"gender": "female", "bank_account": "SBIN0001234"})


def test_user_profile_bounds_validation() -> None:
    """Test bounds on age and income."""
    with pytest.raises(ValidationError):
        UserProfile(age=-1)

    with pytest.raises(ValidationError):
        UserProfile(age=150)

    with pytest.raises(ValidationError):
        UserProfile(annual_income=-500.0)


# ==================== EligibilityCriteria Tests ====================


def test_criteria_valid_operators() -> None:
    """Test valid criteria configurations across all supported operators."""
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
            Criterion(
                field=CriterionField.GENDER,
                op=CriterionOperator.EQ,
                value="female",
            ),
        ],
        any_of=[
            Criterion(
                field=CriterionField.OCCUPATION,
                op=CriterionOperator.IN,
                value=["farmer", "artisan"],
            ),
            Criterion(
                field=CriterionField.DISABILITY_STATUS,
                op=CriterionOperator.NOT_IN,
                value=["none", "prefer_not_to_say"],
            ),
        ],
    )
    assert len(crit.all_of) == 3
    assert len(crit.any_of) == 2


def test_criteria_invalid_between_operator() -> None:
    """Test that between operator enforces 2 numeric elements with min <= max."""
    # Only 1 element
    with pytest.raises(ValidationError):
        Criterion(
            field=CriterionField.AGE,
            op=CriterionOperator.BETWEEN,
            value=[18],
        )

    # Inverted bounds (min > max)
    with pytest.raises(ValidationError):
        Criterion(
            field=CriterionField.AGE,
            op=CriterionOperator.BETWEEN,
            value=[35, 18],
        )

    # Non-numeric
    with pytest.raises(ValidationError):
        Criterion(
            field=CriterionField.AGE,
            op=CriterionOperator.BETWEEN,
            value=["18", "30"],
        )


def test_criteria_invalid_in_and_gte_operators() -> None:
    """Test validation on in and numeric operators."""
    # Empty list for in
    with pytest.raises(ValidationError):
        Criterion(
            field=CriterionField.OCCUPATION,
            op=CriterionOperator.IN,
            value=[],
        )

    # Non-numeric value for gte
    with pytest.raises(ValidationError):
        Criterion(
            field=CriterionField.AGE,
            op=CriterionOperator.GTE,
            value="twenty",
        )

    # Composite value for eq
    with pytest.raises(ValidationError):
        Criterion(
            field=CriterionField.GENDER,
            op=CriterionOperator.EQ,
            value=["female"],
        )


# ==================== Scheme Schema Tests ====================


def test_scheme_schema_valid_central() -> None:
    """Test valid central scheme (state must be None)."""
    now = datetime.now(UTC)
    scheme = SchemeCreate(
        slug="pm-kisan-central-sample",
        name="PM Kisan Samman Nidhi",
        name_hi="पीएम किसान सम्मान निधि",
        level=SchemeLevel.CENTRAL,
        state=None,
        category_tags=["agriculture", "financial_aid"],
        benefit_summary="Rs 6,000 annual direct income support in installments.",
        benefit_summary_hi="तीन समान किस्तों में ₹6,000 की वार्षिक प्रत्यक्ष आय सहायता।",
        eligibility_criteria=EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.OCCUPATION,
                    op=CriterionOperator.EQ,
                    value="farmer",
                )
            ]
        ),
        required_documents=["Land ownership document"],
        application_steps=["Apply via PM-Kisan portal"],
        apply_url="https://pmkisan.gov.in",
        source_url="https://pmkisan.gov.in/guidelines.pdf",
        source_hash="abcdef0123456789abcdef0123456789abcdef01",
        status=SchemeStatus.VERIFIED,
        verified_by="admin@test.internal",
        verified_at=now,
        last_verified=now,
        is_sample=False,
    )
    assert scheme.slug == "pm-kisan-central-sample"
    assert scheme.state is None


def test_scheme_schema_central_cannot_have_state() -> None:
    """Test that level=central with a state raises ValidationError."""
    now = datetime.now(UTC)
    with pytest.raises(ValidationError):
        SchemeCreate(
            slug="invalid-central",
            name="Test Central",
            name_hi="टेस्ट सेंट्रल",
            level=SchemeLevel.CENTRAL,
            state="maharashtra",  # Must be None for central
            benefit_summary="Some benefit summary of sufficient length.",
            benefit_summary_hi="कुछ पर्याप्त लंबाई का लाभ सारांश।",
            apply_url="https://example.gov.in",
            source_url="https://example.gov.in",
            source_hash="0123456789abcdef0123456789abcdef",
            last_verified=now,
        )


def test_scheme_schema_state_level_requires_state() -> None:
    """Test that level=state requires non-null state."""
    now = datetime.now(UTC)
    with pytest.raises(ValidationError):
        SchemeCreate(
            slug="invalid-state",
            name="Test State Scheme",
            name_hi="टेस्ट राज्य योजना",
            level=SchemeLevel.STATE,
            state=None,  # Required for state schemes
            benefit_summary="Some benefit summary of sufficient length.",
            benefit_summary_hi="कुछ पर्याप्त लंबाई का लाभ सारांश।",
            apply_url="https://example.gov.in",
            source_url="https://example.gov.in",
            source_hash="0123456789abcdef0123456789abcdef",
            last_verified=now,
        )


def test_scheme_slug_format() -> None:
    """Test slug validation requires lowercase alphanumeric with hyphens."""
    now = datetime.now(UTC)
    with pytest.raises(ValidationError):
        SchemeCreate(
            slug="Invalid Slug With Spaces",
            name="Title",
            name_hi="शीर्षक",
            level=SchemeLevel.CENTRAL,
            state=None,
            benefit_summary="Valid summary text describing benefits.",
            benefit_summary_hi="लाभों का विवरण देने वाला सारांश।",
            apply_url="https://example.gov.in",
            source_url="https://example.gov.in",
            source_hash="0123456789abcdef0123456789abcdef",
            last_verified=now,
        )


# ==================== AdminUser & Chunk & Feedback Tests ====================


def test_admin_user_validation() -> None:
    """Test admin user schema validation and extra field rejection."""
    admin = AdminUserCreate(
        email="reviewer@yojanasetu.gov.in",
        password_hash="$2b$12$e80yV9u5ZlP4aP.sXQZ2Eep0uK7B5b8pXq...",
        role=AdminRole.REVIEWER,
    )
    assert admin.email == "reviewer@yojanasetu.gov.in"
    assert admin.failed_logins == 0
    assert admin.locked_until is None

    # Invalid email rejected
    with pytest.raises(ValidationError):
        AdminUserCreate(
            email="not-an-email",
            password_hash="some_long_hash_string_of_length_20+",
        )

    # Extra field rejected
    with pytest.raises(ValidationError):
        AdminUserCreate(
            email="admin@test.internal",
            password_hash="some_long_hash_string_of_length_20+",
            is_superadmin=True,
        )


def test_feedback_schema() -> None:
    """Test anonymous feedback schema and comment length constraint."""
    fb = FeedbackCreate(
        scheme_id="fictional-pm-yuva",
        vote=FeedbackVote.HELPFUL,
        comment="Very helpful guide on application steps.",
    )
    assert fb.vote == FeedbackVote.HELPFUL
    assert fb.scheme_id == "fictional-pm-yuva"

    # Comment exceeding 500 characters rejected
    with pytest.raises(ValidationError):
        FeedbackCreate(
            scheme_id="fictional-pm-yuva",
            vote=FeedbackVote.NOT_HELPFUL,
            comment="A" * 501,
        )

    # Extra fields rejected (e.g. attempting to send user identifiers)
    with pytest.raises(ValidationError):
        FeedbackCreate(
            scheme_id="fictional-pm-yuva",
            vote=FeedbackVote.HELPFUL,
            user_id="user-12345",
        )


def test_scheme_chunk_schema() -> None:
    """Test SchemeChunk validation and embedding vector requirements."""
    chunk = SchemeChunkCreate(
        scheme_id="sample-slug-123",
        section=ChunkSection.ELIGIBILITY,
        text="The applicant must be a resident of Maharashtra and a farmer.",
        embedding=[0.012, -0.045, 0.123, 0.456],
        source_url="https://sample.gov.in/guidelines.pdf",
        page=3,
    )
    assert chunk.section == ChunkSection.ELIGIBILITY
    assert chunk.page == 3

    # Extra field rejected
    with pytest.raises(ValidationError):
        SchemeChunkCreate(
            scheme_id="sample-slug-123",
            section=ChunkSection.DOCUMENTS,
            text="Valid length document text.",
            embedding=[0.1, 0.2],
            source_url="https://sample.gov.in",
            extra_field="unauthorized",
        )


def test_all_request_models_enforce_extra_forbid() -> None:
    """Verify every API request and input model enforces extra='forbid'."""
    from app.schemas.admin import AdminUserBase, AdminUserCreate
    from app.schemas.api import (
        FeedbackResponse,
        IntakeExtractRequest,
        IntakeExtractResponse,
        MatchRequest,
        MatchResponse,
        PaginatedSchemesResponse,
        SchemeAskRequest,
        SchemeAskResponse,
        SchemeMatchItem,
    )
    from app.schemas.audit import AuditLogBase, AuditLogCreate
    from app.schemas.chunk import SchemeChunkBase, SchemeChunkCreate
    from app.schemas.feedback import FeedbackBase, FeedbackCreate
    from app.schemas.scheme import SchemeBase, SchemeCreate, SchemeUpdate
    from app.schemas.user_profile import UserProfile

    request_models = [
        IntakeExtractRequest,
        MatchRequest,
        SchemeAskRequest,
        FeedbackCreate,
        FeedbackBase,
        UserProfile,
        SchemeCreate,
        SchemeBase,
        SchemeUpdate,
        AdminUserCreate,
        AdminUserBase,
        AuditLogCreate,
        AuditLogBase,
        SchemeChunkCreate,
        SchemeChunkBase,
        IntakeExtractResponse,
        MatchResponse,
        SchemeMatchItem,
        PaginatedSchemesResponse,
        SchemeAskResponse,
        FeedbackResponse,
    ]

    for model in request_models:
        extra_setting = model.model_config.get("extra")
        assert (
            extra_setting == "forbid"
        ), f"Model {model.__name__} has extra='{extra_setting}', expected 'forbid'"
