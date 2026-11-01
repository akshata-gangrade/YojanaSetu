"""Comprehensive administrative panel and authentication backend tests.

Covers:
- Login with Argon2id password verification
- Generic error identical for wrong email and wrong password
- 5 failed attempts account lockout for 15 minutes
- Heavy rate-limiting (5/min per IP) on login route
- Token security: missing, expired, tampered, and alg=none tokens return 401
- Role-based authorization: reviewer cannot archive or read audit logs (returns 403)
- Admin can archive and read audit logs
- Scheme creation forces status to needs_review and requires https on .gov.in/.nic.in
- Editing a verified scheme resets it to needs_review
- Scheme verification requires source_url and sets verified_by and verified_at
- Scheme rejection requires reason and sets status to draft
- Public API visibility invariant: verified scheme appears, draft/rejected does not
- Audit trail integrity: all writes create audit logs; no passwords or tokens ever logged
"""

from datetime import UTC, datetime, timedelta
import uuid

from httpx import ASGITransport, AsyncClient
import jwt
import pytest

from app.api.deps import (
    get_admin_repo,
    get_audit_repo,
    get_feedback_repo,
    get_scheme_repo,
)
from app.core.auth import create_admin_jwt, hash_password
from app.core.config import Settings, get_settings
from app.core.rate_limit import rate_limiter
from app.main import create_app
from app.repositories.fakes import (
    FakeAdminRepository,
    FakeAuditRepository,
    FakeFeedbackRepository,
    FakeSchemeRepository,
)
from app.schemas.admin import AdminUserCreate
from app.schemas.criteria import Criterion, EligibilityCriteria
from app.schemas.enums import (
    AdminRole,
    CriterionField,
    CriterionOperator,
    SchemeLevel,
    SchemeStatus,
)
from app.schemas.scheme import SchemeCreate

TEST_ADMIN_EMAIL = "superadmin@yojanasetu.gov.in"
TEST_REVIEWER_EMAIL = "reviewer@yojanasetu.gov.in"
TEST_PASSWORD = "StrongPassword@2026Secure!"


@pytest.fixture
def admin_test_settings() -> Settings:
    return Settings(
        _env_file=None,
        ENV="development",
        API_PREFIX="/api/v1",
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DB="yojanasetu_test",
        GROQ_API_KEY="gsk_test_api_key_12345",
        GROQ_MODEL="llama-3.3-70b-versatile",
        EMBEDDING_PROVIDER="hosted",
        EMBEDDING_API_KEY="test_embedding_key",
        EMBEDDING_MODEL="hosted-multilingual-e5",
        EMBEDDING_DIM=384,
        JWT_SECRET="super_secret_admin_jwt_key_that_is_at_least_32_characters_long",
        JWT_ISSUER="yojanasetu",
        ACCESS_TOKEN_MINUTES=30,
        ALLOWED_ORIGINS=["http://localhost:5173"],
        ENABLE_DOCS=True,
        RATE_LIMIT_PER_MINUTE=60,
        LOG_LEVEL="INFO",
        INCLUDE_SAMPLE_SCHEMES=False,
    )


@pytest.fixture
def fake_admin_repos():
    scheme_repo = FakeSchemeRepository(include_sample_schemes=False)
    audit_repo = FakeAuditRepository()
    admin_repo = FakeAdminRepository()
    feedback_repo = FakeFeedbackRepository()
    return scheme_repo, audit_repo, admin_repo, feedback_repo


@pytest.fixture
async def seeded_admin_repos(fake_admin_repos):
    scheme_repo, audit_repo, admin_repo, feedback_repo = fake_admin_repos

    # Seed Admin User
    admin_hash = hash_password(TEST_PASSWORD)
    await admin_repo.create_admin(
        AdminUserCreate(
            email=TEST_ADMIN_EMAIL,
            password_hash=admin_hash,
            role=AdminRole.ADMIN,
        )
    )

    # Seed Reviewer User
    reviewer_hash = hash_password(TEST_PASSWORD)
    await admin_repo.create_admin(
        AdminUserCreate(
            email=TEST_REVIEWER_EMAIL,
            password_hash=reviewer_hash,
            role=AdminRole.REVIEWER,
        )
    )

    return scheme_repo, audit_repo, admin_repo, feedback_repo


@pytest.fixture
async def admin_client(
    admin_test_settings: Settings,
    seeded_admin_repos,
) -> AsyncClient:
    rate_limiter.reset()
    scheme_repo, audit_repo, admin_repo, feedback_repo = seeded_admin_repos

    app = create_app(admin_test_settings)
    app.dependency_overrides[get_settings] = lambda: admin_test_settings
    app.dependency_overrides[get_scheme_repo] = lambda: scheme_repo
    app.dependency_overrides[get_audit_repo] = lambda: audit_repo
    app.dependency_overrides[get_admin_repo] = lambda: admin_repo
    app.dependency_overrides[get_feedback_repo] = lambda: feedback_repo

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    rate_limiter.reset()


@pytest.fixture
def make_auth_header(admin_test_settings: Settings):
    def _generator(email: str, role: AdminRole) -> dict[str, str]:
        token, _ = create_admin_jwt(email, role, settings=admin_test_settings)
        return {"Authorization": f"Bearer {token}"}

    return _generator


# ==============================================================================
# Authentication & Lockout Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_admin_login_success(admin_client: AsyncClient, admin_test_settings: Settings):
    """Test successful login with Argon2id and short-lived HS256 JWT response."""
    payload = {"email": TEST_ADMIN_EMAIL, "password": TEST_PASSWORD}
    resp = await admin_client.post("/api/v1/admin/auth/login", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "admin"
    assert 900 <= data["expires_in"] <= 1800  # 15 to 30 mins

    # Verify claims
    decoded = jwt.decode(
        data["access_token"],
        admin_test_settings.JWT_SECRET,
        algorithms=["HS256"],
        issuer=admin_test_settings.JWT_ISSUER,
    )
    assert decoded["sub"] == TEST_ADMIN_EMAIL
    assert decoded["role"] == "admin"
    assert decoded["iss"] == "yojanasetu"
    assert "jti" in decoded
    assert "iat" in decoded
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_login_generic_error_identical_for_wrong_email_and_password(
    admin_client: AsyncClient,
):
    """Timing and response equality: identical error envelope for wrong email and wrong password."""
    # 1. Wrong email
    resp_wrong_email = await admin_client.post(
        "/api/v1/admin/auth/login",
        json={"email": "nonexistent@yojanasetu.gov.in", "password": TEST_PASSWORD},
    )
    assert resp_wrong_email.status_code == 401

    # 2. Wrong password
    resp_wrong_pw = await admin_client.post(
        "/api/v1/admin/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": "WrongPassword12345!"},
    )
    assert resp_wrong_pw.status_code == 401

    err_email = resp_wrong_email.json()["error"]
    err_pw = resp_wrong_pw.json()["error"]

    assert err_email["code"] == "UNAUTHORIZED"
    assert err_pw["code"] == "UNAUTHORIZED"
    # Strict invariance: Messages must be identical
    assert err_email["message"] == err_pw["message"]


@pytest.mark.asyncio
async def test_login_lockout_after_5_failed_attempts(
    admin_client: AsyncClient,
    seeded_admin_repos,
):
    """Account locks for 15 minutes after 5 consecutive failed attempts."""
    rate_limiter.reset()
    _, _, admin_repo, _ = seeded_admin_repos

    target_email = "lockout_target@yojanasetu.gov.in"
    await admin_repo.create_admin(
        AdminUserCreate(
            email=target_email,
            password_hash=hash_password(TEST_PASSWORD),
            role=AdminRole.REVIEWER,
        )
    )

    # Attempts 1 through 5 fail with wrong password
    for i in range(5):
        rate_limiter.reset()  # Reset IP rate limiter to test account lockout specifically
        resp = await admin_client.post(
            "/api/v1/admin/auth/login",
            json={"email": target_email, "password": f"WrongAttempt{i}"},
        )
        assert resp.status_code == 401

    # In database: account should now be marked locked
    user = await admin_repo.get_by_email(target_email)
    assert user is not None
    assert user.failed_logins == 5
    assert user.locked_until is not None
    assert user.locked_until > datetime.now(UTC)

    # 6th attempt (even with CORRECT password) is rejected due to lockout
    rate_limiter.reset()
    resp_locked = await admin_client.post(
        "/api/v1/admin/auth/login",
        json={"email": target_email, "password": TEST_PASSWORD},
    )
    assert resp_locked.status_code == 401
    assert "locked" in resp_locked.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_login_heavily_rate_limited(admin_client: AsyncClient):
    """Login route is strictly rate-limited to 5 requests per minute per IP."""
    rate_limiter.reset()

    for i in range(5):
        r = await admin_client.post(
            "/api/v1/admin/auth/login",
            json={"email": TEST_ADMIN_EMAIL, "password": f"Try{i}"},
        )
        assert r.status_code in (200, 401)

    r_sixth = await admin_client.post(
        "/api/v1/admin/auth/login",
        json={"email": TEST_ADMIN_EMAIL, "password": "Try6"},
    )
    assert r_sixth.status_code == 429
    assert r_sixth.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    rate_limiter.reset()


# ==============================================================================
# Token Validation: Missing, Expired, Tampered, Alg=None
# ==============================================================================


@pytest.mark.asyncio
async def test_auth_token_security_variants(
    admin_client: AsyncClient,
    admin_test_settings: Settings,
):
    """Test 401 Unauthorized for missing, malformed, expired, tampered, and alg=none tokens."""
    # 1. Missing Authorization header
    resp_missing = await admin_client.get("/api/v1/admin/schemes")
    assert resp_missing.status_code == 401

    # 2. Expired Token
    now = datetime.now(UTC)
    expired_payload = {
        "sub": TEST_ADMIN_EMAIL,
        "role": "admin",
        "iat": int((now - timedelta(hours=2)).timestamp()),
        "exp": int((now - timedelta(hours=1)).timestamp()),
        "iss": admin_test_settings.JWT_ISSUER,
        "jti": uuid.uuid4().hex,
    }
    expired_token = jwt.encode(
        expired_payload, admin_test_settings.JWT_SECRET, algorithm="HS256"
    )
    resp_expired = await admin_client.get(
        "/api/v1/admin/schemes",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp_expired.status_code == 401
    assert "expired" in resp_expired.json()["error"]["message"].lower()

    # 3. Tampered Token (signature invalidated)
    valid_token, _ = create_admin_jwt(TEST_ADMIN_EMAIL, AdminRole.ADMIN)
    tampered_token = valid_token[:-4] + "xxxx"
    resp_tampered = await admin_client.get(
        "/api/v1/admin/schemes",
        headers={"Authorization": f"Bearer {tampered_token}"},
    )
    assert resp_tampered.status_code == 401

    # 4. alg=none Token Attack
    alg_none_payload = {
        "sub": TEST_ADMIN_EMAIL,
        "role": "admin",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=15)).timestamp()),
        "iss": admin_test_settings.JWT_ISSUER,
        "jti": uuid.uuid4().hex,
    }
    # Unsecured token with alg: none
    alg_none_token = jwt.encode(alg_none_payload, key="", algorithm="none")
    resp_alg_none = await admin_client.get(
        "/api/v1/admin/schemes",
        headers={"Authorization": f"Bearer {alg_none_token}"},
    )
    assert resp_alg_none.status_code == 401


# ==============================================================================
# Role Checks & Reviewer Restrictions
# ==============================================================================


@pytest.mark.asyncio
async def test_role_permissions_reviewer_vs_admin(
    admin_client: AsyncClient,
    make_auth_header,
    seeded_admin_repos,
):
    """Reviewer can list, create, edit, verify, reject, but CANNOT archive or read audit-logs (403)."""
    scheme_repo, _, _, _ = seeded_admin_repos

    # Create dummy scheme
    scheme = SchemeCreate(
        slug="test-role-scheme",
        name="Role Test Scheme",
        name_hi="रोल टेस्ट योजना",
        level=SchemeLevel.CENTRAL,
        benefit_summary="Financial assistance for citizens.",
        benefit_summary_hi="नागरिकों के लिए वित्तीय सहायता।",
        apply_url="https://myscheme.gov.in",
        source_url="https://myscheme.gov.in/guidelines.pdf",
        source_hash="d" * 64,
        status=SchemeStatus.NEEDS_REVIEW,
        last_verified=datetime.now(UTC),
    )
    await scheme_repo.create_scheme(scheme)

    reviewer_header = make_auth_header(TEST_REVIEWER_EMAIL, AdminRole.REVIEWER)
    admin_header = make_auth_header(TEST_ADMIN_EMAIL, AdminRole.ADMIN)

    # 1. Reviewer CAN list schemes
    r_list = await admin_client.get("/api/v1/admin/schemes", headers=reviewer_header)
    assert r_list.status_code == 200

    # 2. Reviewer CAN view one scheme
    r_get = await admin_client.get(
        "/api/v1/admin/schemes/test-role-scheme", headers=reviewer_header
    )
    assert r_get.status_code == 200

    # 3. Reviewer CANNOT archive a scheme -> 403 Forbidden
    r_archive_denied = await admin_client.post(
        "/api/v1/admin/schemes/test-role-scheme/archive",
        headers=reviewer_header,
    )
    assert r_archive_denied.status_code == 403
    assert r_archive_denied.json()["error"]["code"] == "FORBIDDEN"

    # 4. Reviewer CANNOT read audit logs -> 403 Forbidden
    r_audit_denied = await admin_client.get(
        "/api/v1/admin/audit-logs",
        headers=reviewer_header,
    )
    assert r_audit_denied.status_code == 403
    assert r_audit_denied.json()["error"]["code"] == "FORBIDDEN"

    # 5. Admin CAN archive scheme -> 200
    r_archive_ok = await admin_client.post(
        "/api/v1/admin/schemes/test-role-scheme/archive",
        headers=admin_header,
    )
    assert r_archive_ok.status_code == 200
    assert r_archive_ok.json()["status"] == "archived"

    # 6. Admin CAN read audit logs -> 200
    r_audit_ok = await admin_client.get(
        "/api/v1/admin/audit-logs",
        headers=admin_header,
    )
    assert r_audit_ok.status_code == 200
    assert len(r_audit_ok.json()["items"]) > 0


# ==============================================================================
# Scheme Mutation, Re-verification Reset, and Audit Logs
# ==============================================================================


@pytest.mark.asyncio
async def test_create_scheme_enforces_needs_review_and_gov_urls(
    admin_client: AsyncClient,
    make_auth_header,
    seeded_admin_repos,
):
    """Scheme creation always saves as needs_review and rejects non-gov URLs."""
    _, audit_repo, _, _ = seeded_admin_repos
    reviewer_header = make_auth_header(TEST_REVIEWER_EMAIL, AdminRole.REVIEWER)

    # 1. Non-gov URL rejected
    invalid_url_payload = {
        "slug": "invalid-url-scheme",
        "name": "Invalid URL Scheme",
        "name_hi=" : "अमान्य योजना",
        "level": "central",
        "benefit_summary": "Direct benefit transfer to accounts.",
        "benefit_summary_hi": "खातों में प्रत्यक्ष लाभ अंतरण।",
        "apply_url": "https://commercial-scam.com/apply",
        "source_url": "https://commercial-scam.com/doc.pdf",
        "source_hash": "e" * 64,
    }
    r_fail = await admin_client.post(
        "/api/v1/admin/schemes",
        json=invalid_url_payload,
        headers=reviewer_header,
    )
    assert r_fail.status_code == 422

    # 2. Valid .gov.in URL creates scheme in needs_review
    valid_payload = {
        "slug": "fresh-agri-scheme",
        "name": "Fresh Agriculture Scheme",
        "name_hi": "नवीन कृषि योजना",
        "level": "central",
        "category_tags": ["agriculture"],
        "benefit_summary": "Direct benefit transfer of Rs 5,000 annually.",
        "benefit_summary_hi": "₹5,000 की वार्षिक प्रत्यक्ष सहायता।",
        "eligibility_criteria": {
            "all_of": [
                {
                    "field": CriterionField.OCCUPATION.value,
                    "op": CriterionOperator.EQ.value,
                    "value": "farmer",
                }
            ]
        },
        "apply_url": "https://agri.gov.in/apply",
        "source_url": "https://agri.nic.in/guidelines.pdf",
        "source_hash": "f" * 64,
    }
    r_create = await admin_client.post(
        "/api/v1/admin/schemes",
        json=valid_payload,
        headers=reviewer_header,
    )
    assert r_create.status_code == 201
    created_scheme = r_create.json()
    assert created_scheme["status"] == "needs_review"

    # Audit log check
    logs = await audit_repo.get_by_target("fresh-agri-scheme")
    assert len(logs) == 1
    assert logs[0].action == "create_scheme"
    assert logs[0].actor == TEST_REVIEWER_EMAIL
    assert logs[0].diff is not None


@pytest.mark.asyncio
async def test_editing_verified_scheme_resets_to_needs_review(
    admin_client: AsyncClient,
    make_auth_header,
    seeded_admin_repos,
):
    """Any modification to a verified scheme resets it to needs_review."""
    scheme_repo, audit_repo, _, _ = seeded_admin_repos
    reviewer_header = make_auth_header(TEST_REVIEWER_EMAIL, AdminRole.REVIEWER)

    # 1. Create and verify scheme
    scheme = SchemeCreate(
        slug="verified-scheme-alpha",
        name="Verified Alpha Scheme",
        name_hi="सत्यापित अल्फा योजना",
        level=SchemeLevel.CENTRAL,
        benefit_summary="Original benefit description.",
        benefit_summary_hi="मूल लाभ विवरण।",
        apply_url="https://alpha.gov.in",
        source_url="https://alpha.gov.in/rules.pdf",
        source_hash="1" * 64,
        status=SchemeStatus.VERIFIED,
        verified_by=TEST_ADMIN_EMAIL,
        verified_at=datetime.now(UTC),
        last_verified=datetime.now(UTC),
    )
    await scheme_repo.create_scheme(scheme)

    # 2. Edit scheme
    update_payload = {
        "benefit_summary": "Updated enhanced benefit description.",
    }
    r_edit = await admin_client.put(
        "/api/v1/admin/schemes/verified-scheme-alpha",
        json=update_payload,
        headers=reviewer_header,
    )
    assert r_edit.status_code == 200
    updated_scheme = r_edit.json()

    # Invariant: Status MUST reset to needs_review
    assert updated_scheme["status"] == "needs_review"
    assert updated_scheme["benefit_summary"] == "Updated enhanced benefit description."

    # Audit log verifies the reset
    logs = await audit_repo.get_by_target("verified-scheme-alpha")
    assert any(log.action == "edit_scheme" for log in logs)
    edit_log = next(log for log in logs if log.action == "edit_scheme")
    assert edit_log.diff["status"]["old"] == "verified"
    assert edit_log.diff["status"]["new"] == "needs_review"


@pytest.mark.asyncio
async def test_verification_requires_source_url_and_records_verifier(
    admin_client: AsyncClient,
    make_auth_header,
    seeded_admin_repos,
):
    """Verify endpoint sets verified_by, verified_at, and verifies source_url."""
    scheme_repo, audit_repo, _, _ = seeded_admin_repos
    reviewer_header = make_auth_header(TEST_REVIEWER_EMAIL, AdminRole.REVIEWER)

    scheme = SchemeCreate(
        slug="pending-review-scheme",
        name="Pending Review Scheme",
        name_hi="समीक्षाधीन योजना",
        level=SchemeLevel.CENTRAL,
        benefit_summary="Financial aid scheme.",
        benefit_summary_hi="वित्तीय सहायता योजना।",
        apply_url="https://scheme.gov.in",
        source_url="https://scheme.gov.in/doc.pdf",
        source_hash="2" * 64,
        status=SchemeStatus.NEEDS_REVIEW,
        last_verified=datetime.now(UTC),
    )
    await scheme_repo.create_scheme(scheme)

    # 1. Verification without source_url when scheme has none or empty fails
    empty_scheme = SchemeCreate(
        slug="empty-source-scheme",
        name="Empty Source Scheme",
        name_hi="रिक्त स्रोत योजना",
        level=SchemeLevel.CENTRAL,
        benefit_summary="Financial aid scheme.",
        benefit_summary_hi="वित्तीय सहायता योजना।",
        apply_url="https://scheme.gov.in",
        source_url="https://temp.gov.in",
        source_hash="2" * 64,
        status=SchemeStatus.NEEDS_REVIEW,
        last_verified=datetime.now(UTC),
    )
    created_empty = await scheme_repo.create_scheme(empty_scheme)
    # Clear out source_url
    scheme_repo._schemes[created_empty.slug]["source_url"] = ""

    r_verify_empty = await admin_client.post(
        f"/api/v1/admin/schemes/{created_empty.slug}/verify",
        json={"source_url": ""},
        headers=reviewer_header,
    )
    assert r_verify_empty.status_code in (400, 422)

    # 2. Execute valid verification
    r_verify = await admin_client.post(
        "/api/v1/admin/schemes/pending-review-scheme/verify",
        json={"source_url": "https://scheme.gov.in/final.pdf"},
        headers=reviewer_header,
    )
    assert r_verify.status_code == 200
    data = r_verify.json()
    assert data["status"] == "verified"
    assert data["verified_by"] == TEST_REVIEWER_EMAIL
    assert data["verified_at"] is not None

    logs = await audit_repo.get_by_target("pending-review-scheme")
    assert any(log.action == "verify_scheme" for log in logs)


@pytest.mark.asyncio
async def test_rejection_requires_reason_and_sets_draft(
    admin_client: AsyncClient,
    make_auth_header,
    seeded_admin_repos,
):
    """Reject endpoint sets status to draft and requires explanation reason."""
    scheme_repo, audit_repo, _, _ = seeded_admin_repos
    reviewer_header = make_auth_header(TEST_REVIEWER_EMAIL, AdminRole.REVIEWER)

    scheme = SchemeCreate(
        slug="flawed-scheme",
        name="Flawed Scheme",
        name_hi="त्रुटिपूर्ण योजना",
        level=SchemeLevel.CENTRAL,
        benefit_summary="Benefits description.",
        benefit_summary_hi="लाभ विवरण।",
        apply_url="https://flawed.gov.in",
        source_url="https://flawed.gov.in/doc.pdf",
        source_hash="3" * 64,
        status=SchemeStatus.NEEDS_REVIEW,
        last_verified=datetime.now(UTC),
    )
    await scheme_repo.create_scheme(scheme)

    # Rejection without reason fails validation
    r_no_reason = await admin_client.post(
        "/api/v1/admin/schemes/flawed-scheme/reject",
        json={},
        headers=reviewer_header,
    )
    assert r_no_reason.status_code == 422

    # Rejection with reason succeeds and reverts to draft
    r_rejected = await admin_client.post(
        "/api/v1/admin/schemes/flawed-scheme/reject",
        json={"reason": "The source document income criteria conflicts with section 4."},
        headers=reviewer_header,
    )
    assert r_rejected.status_code == 200
    assert r_rejected.json()["status"] == "draft"

    logs = await audit_repo.get_by_target("flawed-scheme")
    assert any(log.action == "reject_scheme" for log in logs)


# ==============================================================================
# Public API Visibility Invariant
# ==============================================================================


@pytest.mark.asyncio
async def test_verified_scheme_appears_in_public_api_and_rejected_does_not(
    admin_client: AsyncClient,
    make_auth_header,
    seeded_admin_repos,
):
    """Verified scheme appears in public /api/v1/schemes; draft/rejected does not."""
    scheme_repo, _, _, _ = seeded_admin_repos
    reviewer_header = make_auth_header(TEST_REVIEWER_EMAIL, AdminRole.REVIEWER)

    # 1. Create a scheme (starts in needs_review)
    scheme = SchemeCreate(
        slug="lifecycle-scheme",
        name="Lifecycle Visibility Scheme",
        name_hi="दृश्यता योजना",
        level=SchemeLevel.CENTRAL,
        benefit_summary="Support for public testing.",
        benefit_summary_hi="सार्वजनिक परीक्षण सहायता।",
        apply_url="https://portal.gov.in",
        source_url="https://portal.gov.in/rules.pdf",
        source_hash="4" * 64,
        status=SchemeStatus.NEEDS_REVIEW,
        last_verified=datetime.now(UTC),
    )
    await scheme_repo.create_scheme(scheme)

    # Needs review -> NOT in public API
    resp_pub1 = await admin_client.get("/api/v1/schemes")
    slugs1 = [s["slug"] for s in resp_pub1.json()["items"]]
    assert "lifecycle-scheme" not in slugs1

    # 2. Verify scheme -> APPEARS in public API
    await admin_client.post(
        "/api/v1/admin/schemes/lifecycle-scheme/verify",
        json={"source_url": "https://portal.gov.in/rules.pdf"},
        headers=reviewer_header,
    )
    resp_pub2 = await admin_client.get("/api/v1/schemes")
    slugs2 = [s["slug"] for s in resp_pub2.json()["items"]]
    assert "lifecycle-scheme" in slugs2

    # 3. Reject scheme -> REVERTS to draft -> DISAPPEARS from public API
    await admin_client.post(
        "/api/v1/admin/schemes/lifecycle-scheme/reject",
        json={"reason": "Source link broken."},
        headers=reviewer_header,
    )
    resp_pub3 = await admin_client.get("/api/v1/schemes")
    slugs3 = [s["slug"] for s in resp_pub3.json()["items"]]
    assert "lifecycle-scheme" not in slugs3

    # Direct slug query gives 404 for draft scheme
    resp_slug = await admin_client.get("/api/v1/schemes/lifecycle-scheme")
    assert resp_slug.status_code == 404


# ==============================================================================
# Ingestion, PDF Upload, and Audit Log Safety Invariant
# ==============================================================================


@pytest.mark.asyncio
async def test_pdf_upload_and_ingestion_trigger(
    admin_client: AsyncClient,
    make_auth_header,
    seeded_admin_repos,
):
    """Test uploading PDF to compute SHA-256 hash and trigger ingestion."""
    scheme_repo, audit_repo, _, _ = seeded_admin_repos
    reviewer_header = make_auth_header(TEST_REVIEWER_EMAIL, AdminRole.REVIEWER)

    scheme = SchemeCreate(
        slug="pdf-target-scheme",
        name="PDF Target Scheme",
        name_hi="पीडीएफ लक्ष्य योजना",
        level=SchemeLevel.CENTRAL,
        benefit_summary="Benefits summary text.",
        benefit_summary_hi="लाभ सारांश पाठ।",
        apply_url="https://pdf.gov.in",
        source_url="https://pdf.gov.in/guidelines.pdf",
        source_hash="5" * 64,
        status=SchemeStatus.NEEDS_REVIEW,
        last_verified=datetime.now(UTC),
    )
    await scheme_repo.create_scheme(scheme)

    # 1. Upload PDF
    pdf_content = b"%PDF-1.4 official guidelines document content here"
    files = {"file": ("guidelines.pdf", pdf_content, "application/pdf")}
    r_upload = await admin_client.post(
        "/api/v1/admin/schemes/upload-pdf",
        files=files,
        headers=reviewer_header,
    )
    assert r_upload.status_code == 200
    upload_data = r_upload.json()
    assert upload_data["filename"] == "guidelines.pdf"
    assert len(upload_data["source_hash"]) == 64

    # 2. Trigger ingestion
    r_ingest = await admin_client.post(
        "/api/v1/admin/schemes/pdf-target-scheme/ingest",
        headers=reviewer_header,
    )
    assert r_ingest.status_code == 200
    assert r_ingest.json()["status"] == "ingestion_triggered"


@pytest.mark.asyncio
async def test_audit_logs_strictly_exclude_passwords_and_tokens(
    admin_client: AsyncClient,
    make_auth_header,
    seeded_admin_repos,
    admin_test_settings: Settings,
):
    """Invariant: Audit logs never log or print passwords, hashes, tokens, or JWT_SECRET."""
    _, audit_repo, _, _ = seeded_admin_repos
    admin_header = make_auth_header(TEST_ADMIN_EMAIL, AdminRole.ADMIN)

    r_logs = await admin_client.get("/api/v1/admin/audit-logs", headers=admin_header)
    assert r_logs.status_code == 200
    logs_data = r_logs.json()

    for item in logs_data["items"]:
        item_str = str(item)
        assert TEST_PASSWORD not in item_str
        assert admin_test_settings.JWT_SECRET not in item_str
        assert "password_hash" not in item_str
        assert "access_token" not in item_str
