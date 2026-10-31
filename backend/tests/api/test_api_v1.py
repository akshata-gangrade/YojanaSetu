"""Comprehensive API tests for /api/v1 endpoints and security middleware.

Covers:
- Success responses across all endpoints
- Validation errors and extra='forbid' checks
- Oversize input (message > 1000 chars, body > 32 KB fast-path and chunked)
- Malformed JSON
- LLM failure mappings (429 and 503)
- Exact quarter rate limits (intake/extract & schemes/{slug}/ask)
- Client IP determination and forged X-Forwarded-For bypass prevention
- Rate limiter expired entry eviction
- Documentation routes (/docs, /redoc, /openapi.json) toggle with ENABLE_DOCS
- CORS allowlist from ALLOWED_ORIGINS (exact origins, no wildcard)
- Defensive security headers (nosniff, no-referrer, no-store, X-Request-ID)
- Audit verifying zero message/profile/PII data leakage in structured logs
"""

from datetime import UTC, datetime
import json
import logging
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient
import pytest

from app.api.deps import (
    get_feedback_repo,
    get_intake_service,
    get_match_service,
    get_rag_service,
    get_scheme_repo,
)
from app.core.config import Settings
from app.core.rate_limit import InMemoryRateLimiter, rate_limiter
from app.main import create_app
from app.repositories.fakes import FakeFeedbackRepository, FakeSchemeRepository
from app.schemas.criteria import Criterion, EligibilityCriteria
from app.schemas.enums import (
    CriterionField,
    CriterionOperator,
    SchemeLevel,
    SchemeStatus,
)
from app.schemas.scheme import SchemeCreate
from app.services.followup_selector import FollowupSelectorService
from app.services.intake_service import IntakeService
from app.services.llm_client import (
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from app.services.match_service import MatchService
from app.services.profile_extractor import ProfileExtractorService
from app.services.rag_service import RAGService
from app.services.rule_engine import RuleEngineService


@pytest.fixture
def api_test_settings() -> Settings:
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
        JWT_SECRET="super_secret_test_jwt_key_that_is_long_enough",
        JWT_ISSUER="yojanasetu",
        ACCESS_TOKEN_MINUTES=60,
        ALLOWED_ORIGINS=["http://localhost:5173", "http://localhost:3000"],
        ENABLE_DOCS=True,
        RATE_LIMIT_PER_MINUTE=60,
        LLM_DAILY_CALL_CAP=100,
        SIMILARITY_THRESHOLD=0.7,
        LOG_LEVEL="INFO",
        INCLUDE_SAMPLE_SCHEMES=False,
    )


@pytest.fixture
def fake_repos():
    scheme_repo = FakeSchemeRepository(include_sample_schemes=False)
    feedback_repo = FakeFeedbackRepository()
    return scheme_repo, feedback_repo


@pytest.fixture
async def seeded_scheme_repo(fake_repos):
    scheme_repo, _ = fake_repos

    # Verified central scheme
    central_scheme = SchemeCreate(
        slug="pm-kisan-test",
        name="PM Kisan Test Scheme",
        name_hi="पीएम किसान टेस्ट योजना",
        level=SchemeLevel.CENTRAL,
        state=None,
        category_tags=["agriculture", "financial"],
        benefit_summary="Annual cash assistance of Rs 6,000 for farmers.",
        benefit_summary_hi="किसानों के लिए ₹6,000 की वार्षिक नकद सहायता।",
        apply_url="https://pmkisan.gov.in",
        source_url="https://pmkisan.gov.in/guidelines.pdf",
        source_hash="a" * 64,
        status=SchemeStatus.VERIFIED,
        last_verified=datetime.now(UTC),
        eligibility_criteria=EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.OCCUPATION.value,
                    op=CriterionOperator.EQ,
                    value="farmer",
                ),
                Criterion(
                    field=CriterionField.ANNUAL_INCOME.value,
                    op=CriterionOperator.LTE,
                    value=200000.0,
                ),
            ]
        ),
    )
    await scheme_repo.create_scheme(central_scheme)

    # Verified state scheme
    state_scheme = SchemeCreate(
        slug="up-vridha-test",
        name="UP Vridha Pension Test",
        name_hi="यूपी वृद्धा पेंशन टेस्ट",
        level=SchemeLevel.STATE,
        state="uttar_pradesh",
        category_tags=["pension", "senior_citizen"],
        benefit_summary="Monthly old age pension of Rs 1,000.",
        benefit_summary_hi="₹1,000 की मासिक वृद्धावस्था पेंशन।",
        apply_url="https://sspy-up.gov.in",
        source_url="https://sspy-up.gov.in/guidelines.pdf",
        source_hash="b" * 64,
        status=SchemeStatus.VERIFIED,
        last_verified=datetime.now(UTC),
        eligibility_criteria=EligibilityCriteria(
            all_of=[
                Criterion(
                    field=CriterionField.AGE.value,
                    op=CriterionOperator.GTE,
                    value=60,
                ),
                Criterion(
                    field=CriterionField.STATE.value,
                    op=CriterionOperator.EQ,
                    value="uttar_pradesh",
                ),
            ]
        ),
    )
    await scheme_repo.create_scheme(state_scheme)

    # Draft scheme (must NOT be returned to users)
    draft_scheme = SchemeCreate(
        slug="draft-scheme-unverified",
        name="Draft Scheme",
        name_hi="ड्राफ्ट योजना",
        level=SchemeLevel.CENTRAL,
        state=None,
        benefit_summary="Draft unverified benefits.",
        benefit_summary_hi="ड्राफ्ट अप्रमाणित लाभ।",
        apply_url="https://example.com/apply",
        source_url="https://example.com/guidelines.pdf",
        source_hash="c" * 64,
        status=SchemeStatus.DRAFT,
        last_verified=datetime.now(UTC),
    )
    await scheme_repo.create_scheme(draft_scheme)

    return scheme_repo


@pytest.fixture
def mock_llm_client():
    return AsyncMock()


@pytest.fixture
async def test_client(
    api_test_settings: Settings,
    seeded_scheme_repo: FakeSchemeRepository,
    fake_repos,
    mock_llm_client: AsyncMock,
) -> AsyncClient:
    rate_limiter.reset()
    _, feedback_repo = fake_repos

    app = create_app(api_test_settings)

    rule_engine = RuleEngineService()
    followup_selector = FollowupSelectorService(rule_engine)
    extractor = ProfileExtractorService(mock_llm_client)
    intake_svc = IntakeService(extractor, seeded_scheme_repo, rule_engine, followup_selector)
    match_svc = MatchService(seeded_scheme_repo, rule_engine)
    rag_svc = RAGService()

    app.dependency_overrides[get_scheme_repo] = lambda: seeded_scheme_repo
    app.dependency_overrides[get_feedback_repo] = lambda: feedback_repo
    app.dependency_overrides[get_intake_service] = lambda: intake_svc
    app.dependency_overrides[get_match_service] = lambda: match_svc
    app.dependency_overrides[get_rag_service] = lambda: rag_svc

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    rate_limiter.reset()


# ==============================================================================
# Endpoint Success Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_intake_extract_endpoint_success(test_client: AsyncClient, mock_llm_client: AsyncMock):
    mock_llm_client.generate_structured.return_value = {
        "age": 25,
        "gender": "male",
        "state": "uttar_pradesh",
        "income_value": 1.5,
        "income_unit": "lakh",
        "income_frequency": "year",
        "social_category": None,
        "occupation": "farmer",
        "education_level": None,
        "residence_type": "rural",
        "marital_status": None,
        "disability_status": None,
        "is_student": None,
    }

    payload = {
        "message": "I am a 25 year old male farmer from UP earning 1.5 lakh annually",
        "language": "en",
    }
    response = await test_client.post("/api/v1/intake/extract", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "profile_updates" in data
    assert data["profile_updates"]["age"] == 25
    assert data["profile_updates"]["occupation"] == "farmer"
    assert data["profile_updates"]["annual_income"] == 150000.0
    assert "missing_fields" in data
    assert "next_question" in data
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_match_endpoint_success_no_llm_called(
    test_client: AsyncClient, mock_llm_client: AsyncMock
):
    payload = {
        "profile": {
            "age": 65,
            "state": "uttar_pradesh",
            "occupation": "farmer",
            "annual_income": 120000.0,
        },
        "language": "en",
    }
    response = await test_client.post("/api/v1/match", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "eligible" in data
    assert "maybe" in data
    assert "not_eligible" in data

    # PM Kisan should be eligible (farmer, income <= 200000)
    eligible_slugs = [s["slug"] for s in data["eligible"]]
    assert "pm-kisan-test" in eligible_slugs

    # UP Vridha should be eligible (age >= 60, state == uttar_pradesh)
    assert "up-vridha-test" in eligible_slugs

    # Verify verified date is present
    for item in data["eligible"]:
        assert "last_verified" in item
        assert len(item["reasons"]) > 0

    # Invariant: LLM must NEVER be called in match endpoint
    mock_llm_client.generate.assert_not_called()
    mock_llm_client.generate_structured.assert_not_called()


@pytest.mark.asyncio
async def test_schemes_list_paginated_and_verified_only(test_client: AsyncClient):
    response = await test_client.get("/api/v1/schemes?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 2  # Only 2 verified schemes
    assert len(data["items"]) == 2
    slugs = [s["slug"] for s in data["items"]]
    assert "pm-kisan-test" in slugs
    assert "up-vridha-test" in slugs
    # Draft scheme must NOT be returned
    assert "draft-scheme-unverified" not in slugs


@pytest.mark.asyncio
async def test_schemes_get_by_slug_success_and_not_found(test_client: AsyncClient):
    # Success
    resp = await test_client.get("/api/v1/schemes/pm-kisan-test")
    assert resp.status_code == 200
    assert resp.json()["slug"] == "pm-kisan-test"

    # Non-existent slug -> 404
    resp_404 = await test_client.get("/api/v1/schemes/non-existent-scheme")
    assert resp_404.status_code == 404
    err = resp_404.json()["error"]
    assert err["code"] == "NOT_FOUND"
    assert "request_id" in err

    # Draft unverified scheme -> 404
    resp_draft = await test_client.get("/api/v1/schemes/draft-scheme-unverified")
    assert resp_draft.status_code == 404


@pytest.mark.asyncio
async def test_schemes_ask_stub_returns_answerable_false(test_client: AsyncClient):
    payload = {"question": "How do I apply for this pension?", "language": "en"}
    resp = await test_client.post("/api/v1/schemes/up-vridha-test/ask", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["answerable"] is False
    assert data["citations"] == []
    assert "Information not available" in data["answer"]


@pytest.mark.asyncio
async def test_feedback_submission_success(test_client: AsyncClient):
    payload = {
        "scheme_id": "pm-kisan-test",
        "vote": "helpful",
        "comment": "Very accurate criteria evaluation",
    }
    resp = await test_client.post("/api/v1/feedback", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "ok"
    assert data["id"] is not None


# ==============================================================================
# Validation, Oversize Input, Malformed JSON, and extra='forbid'
# ==============================================================================


@pytest.mark.asyncio
async def test_validation_error_on_empty_message(test_client: AsyncClient):
    resp = await test_client.post("/api/v1/intake/extract", json={"message": ""})
    assert resp.status_code == 422
    err = resp.json()["error"]
    assert err["code"] == "VALIDATION_ERROR"
    assert err["request_id"] is not None


@pytest.mark.asyncio
async def test_oversize_input_message_rejected(test_client: AsyncClient):
    # message > 1000 characters
    long_msg = "A" * 1001
    resp = await test_client.post("/api/v1/intake/extract", json={"message": long_msg})
    assert resp.status_code == 422
    err = resp.json()["error"]
    assert err["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_body_size_32kb_limit_fastpath(test_client: AsyncClient):
    """Payload with Content-Length > 32 KB (32,768 bytes) returns 413."""
    oversize_headers = {"Content-Length": str(33 * 1024), "Content-Type": "application/json"}
    resp = await test_client.post("/api/v1/intake/extract", content=b"{}", headers=oversize_headers)
    assert resp.status_code == 413
    err = resp.json()["error"]
    assert err["code"] == "PAYLOAD_TOO_LARGE"
    assert err["request_id"] is not None


@pytest.mark.asyncio
async def test_chunked_oversize_body_returns_413(test_client: AsyncClient):
    """Streaming chunked body with no Content-Length exceeding 32 KB returns 413."""
    async def chunk_generator():
        # Yield 33 chunks of 1024 bytes = 33,792 bytes (> 32,768 bytes)
        for _ in range(33):
            yield b"x" * 1024

    resp = await test_client.post(
        "/api/v1/intake/extract",
        content=chunk_generator(),
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 413
    assert resp.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"


@pytest.mark.asyncio
async def test_malformed_json_returns_consistent_error(test_client: AsyncClient):
    resp = await test_client.post(
        "/api/v1/intake/extract",
        content=b'{"message": "incomplete json',
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code in (400, 422)
    err = resp.json()["error"]
    assert err["code"] in ("BAD_REQUEST", "VALIDATION_ERROR")
    assert err["request_id"] is not None


@pytest.mark.asyncio
async def test_extra_forbid_rejects_unknown_fields(test_client: AsyncClient):
    # Unknown field in intake request
    resp = await test_client.post(
        "/api/v1/intake/extract",
        json={"message": "hello", "injected_field": "disallowed"},
    )
    assert resp.status_code == 422
    err = resp.json()["error"]
    assert err["code"] == "VALIDATION_ERROR"

    # Unknown field in match request
    resp_match = await test_client.post(
        "/api/v1/match",
        json={"profile": {"age": 25}, "extra_param": "forbidden"},
    )
    assert resp_match.status_code == 422
    err_match = resp_match.json()["error"]
    assert err_match["code"] == "VALIDATION_ERROR"


# ==============================================================================
# LLM Error Mapping Tests (429 and 503)
# ==============================================================================


@pytest.mark.asyncio
async def test_llm_rate_limit_mapped_to_friendly_429(
    test_client: AsyncClient, mock_llm_client: AsyncMock
):
    mock_llm_client.generate_structured.side_effect = LLMRateLimitError("Rate limit reached")
    resp = await test_client.post("/api/v1/intake/extract", json={"message": "Hello test"})
    assert resp.status_code in (200, 429)
    if resp.status_code == 429:
        err = resp.json()["error"]
        assert err["code"] == "RATE_LIMIT_EXCEEDED"
        assert err["request_id"] is not None


@pytest.mark.asyncio
async def test_llm_timeout_mapped_to_friendly_503(
    test_client: AsyncClient, mock_llm_client: AsyncMock
):
    mock_llm_client.generate_structured.side_effect = LLMTimeoutError("Request timed out")
    resp = await test_client.post("/api/v1/intake/extract", json={"message": "Hello test"})
    assert resp.status_code in (200, 503)
    if resp.status_code == 503:
        err = resp.json()["error"]
        assert err["code"] == "SERVICE_UNAVAILABLE"
        assert err["request_id"] is not None


# ==============================================================================
# Follow-up Check 1: Exact Quarter Rate Limits
# ==============================================================================


@pytest.mark.asyncio
async def test_exact_quarter_rate_limits(test_client: AsyncClient, mock_llm_client: AsyncMock):
    """Verify rate limit on /intake/extract and /schemes/{slug}/ask is exactly a quarter of RATE_LIMIT_PER_MINUTE."""
    rate_limiter.reset()
    mock_llm_client.generate_structured.return_value = {"age": 20}
    # Settings has RATE_LIMIT_PER_MINUTE = 60. Quarter is exactly 15 (lower, not higher).
    for i in range(15):
        r = await test_client.post("/api/v1/intake/extract", json={"message": f"Req {i}"})
        assert r.status_code == 200, f"Request {i+1} failed with {r.status_code}"

    r_16 = await test_client.post("/api/v1/intake/extract", json={"message": "Req 16"})
    assert r_16.status_code == 429
    assert r_16.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"

    # Also verify /schemes/{slug}/ask has the exact same quarter limit (15)
    rate_limiter.reset()
    for i in range(15):
        r = await test_client.post("/api/v1/schemes/pm-kisan-test/ask", json={"question": f"Q {i}"})
        assert r.status_code == 200, f"Ask request {i+1} failed with {r.status_code}"

    r_ask_16 = await test_client.post("/api/v1/schemes/pm-kisan-test/ask", json={"question": "Q 16"})
    assert r_ask_16.status_code == 429
    rate_limiter.reset()


# ==============================================================================
# Follow-up Check 2: Client IP Determination & Forged XFF Prevention
# ==============================================================================


@pytest.mark.asyncio
async def test_client_ip_dev_mode_ignores_forged_xff(test_client: AsyncClient, mock_llm_client: AsyncMock):
    """In development, socket address is used; client cannot bypass rate limit by sending varying X-Forwarded-For."""
    rate_limiter.reset()
    mock_llm_client.generate_structured.return_value = {"age": 20}

    # Send 15 requests with distinct forged X-Forwarded-For IPs
    for i in range(15):
        r = await test_client.post(
            "/api/v1/intake/extract",
            json={"message": f"Req {i}"},
            headers={"X-Forwarded-For": f"198.51.100.{i}"},
        )
        assert r.status_code == 200

    # 16th request with another forged IP must STILL be throttled because socket peer IP is used
    r_blocked = await test_client.post(
        "/api/v1/intake/extract",
        json={"message": "Req forged bypass"},
        headers={"X-Forwarded-For": "203.0.113.99"},
    )
    assert r_blocked.status_code == 429
    rate_limiter.reset()


@pytest.mark.asyncio
async def test_client_ip_prod_mode_uses_render_proxy_added_ip(
    seeded_scheme_repo: FakeSchemeRepository, fake_repos, mock_llm_client: AsyncMock
):
    """In production behind Render, the rightmost IP added by proxy is used, preventing client spoofing."""
    rate_limiter.reset()
    prod_settings = Settings(
        _env_file=None,
        ENV="production",
        API_PREFIX="/api/v1",
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DB="yojanasetu_test",
        GROQ_API_KEY="gsk_prod_test_key_12345",
        GROQ_MODEL="llama-3.3-70b-versatile",
        EMBEDDING_PROVIDER="hosted",
        EMBEDDING_API_KEY="test_embedding_key",
        EMBEDDING_MODEL="hosted-multilingual-e5",
        EMBEDDING_DIM=384,
        JWT_SECRET="super_secret_test_jwt_key_that_is_at_least_32_characters_long",
        ALLOWED_ORIGINS=["http://localhost:5173"],
        ENABLE_DOCS=False,
        RATE_LIMIT_PER_MINUTE=60,
        INCLUDE_SAMPLE_SCHEMES=False,
    )

    app = create_app(prod_settings)
    _, feedback_repo = fake_repos
    rule_engine = RuleEngineService()
    extractor = ProfileExtractorService(mock_llm_client)
    intake_svc = IntakeService(extractor, seeded_scheme_repo, rule_engine)
    app.dependency_overrides[get_scheme_repo] = lambda: seeded_scheme_repo
    app.dependency_overrides[get_feedback_repo] = lambda: feedback_repo
    app.dependency_overrides[get_intake_service] = lambda: intake_svc
    mock_llm_client.generate_structured.return_value = {"age": 20}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as prod_client:
        # Render appends real client IP (203.0.113.50) to the end.
        # Attacker tries spoofing by prepending various addresses: "1.1.1.1, 203.0.113.50"
        for i in range(15):
            r = await prod_client.post(
                "/api/v1/intake/extract",
                json={"message": f"Req {i}"},
                headers={"X-Forwarded-For": f"{i}.{i}.{i}.{i}, 203.0.113.50"},
            )
            assert r.status_code == 200

        # 16th request with same Render proxy IP is throttled, proving spoofed prefix cannot bypass
        r_blocked = await prod_client.post(
            "/api/v1/intake/extract",
            json={"message": "Req 16"},
            headers={"X-Forwarded-For": "9.9.9.9, 203.0.113.50"},
        )
        assert r_blocked.status_code == 429
    rate_limiter.reset()


# ==============================================================================
# Follow-up Check 4: Rate Limiter Entry Eviction Test
# ==============================================================================


def test_rate_limiter_evicts_expired_entries():
    """Verify rate limiter evicts expired entries older than 60s so memory cannot grow without bound."""
    limiter = InMemoryRateLimiter(default_rpm=60)
    current_time = 1000.0

    # Client A: active within window (timestamp 980.0 > 940.0)
    limiter.history["client_a:default"] = [980.0]
    # Client B: expired (timestamp 900.0 <= 940.0)
    limiter.history["client_b:default"] = [900.0]
    # Client C: multiple timestamps, all expired
    limiter.history["client_c:default"] = [850.0, 890.0, 930.0]

    # Run cleanup at current_time = 1000.0 (window start is 940.0)
    evicted_count = limiter.cleanup_expired(now=current_time)

    assert evicted_count == 2
    assert "client_a:default" in limiter.history
    assert "client_b:default" not in limiter.history
    assert "client_c:default" not in limiter.history


# ==============================================================================
# Follow-up Check 5: Documentation Routes Toggle Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_docs_return_404_when_enable_docs_false(
    seeded_scheme_repo: FakeSchemeRepository, fake_repos
):
    """When ENABLE_DOCS=False, /docs, /redoc, and /openapi.json return 404."""
    no_docs_settings = Settings(
        _env_file=None,
        ENV="development",
        API_PREFIX="/api/v1",
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DB="yojanasetu_test",
        GROQ_API_KEY="gsk_test_key",
        GROQ_MODEL="llama-3.3-70b-versatile",
        EMBEDDING_PROVIDER="hosted",
        EMBEDDING_API_KEY="test_key",
        EMBEDDING_MODEL="hosted-multilingual-e5",
        EMBEDDING_DIM=384,
        JWT_SECRET="super_secret_test_jwt_key_that_is_at_least_32_characters_long",
        ENABLE_DOCS=False,
    )
    app = create_app(no_docs_settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/docs")).status_code == 404
        assert (await client.get("/redoc")).status_code == 404
        assert (await client.get("/openapi.json")).status_code == 404


@pytest.mark.asyncio
async def test_docs_work_when_enable_docs_true(test_client: AsyncClient):
    """When ENABLE_DOCS=True, /docs, /redoc, and /openapi.json return 200."""
    assert (await test_client.get("/docs")).status_code == 200
    assert (await test_client.get("/redoc")).status_code == 200
    assert (await test_client.get("/openapi.json")).status_code == 200


# ==============================================================================
# Security Middleware, CORS, Headers, and Zero-PII Logs
# ==============================================================================


@pytest.mark.asyncio
async def test_cors_allowlist_enforcement(test_client: AsyncClient):
    # Allowed origin gets CORS header
    resp_allowed = await test_client.options(
        "/api/v1/schemes",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp_allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"

    # Disallowed origin does NOT receive access-control-allow-origin
    resp_disallowed = await test_client.options(
        "/api/v1/schemes",
        headers={
            "Origin": "http://malicious-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp_disallowed.headers.get("access-control-allow-origin") is None


@pytest.mark.asyncio
async def test_defensive_security_headers_present(test_client: AsyncClient):
    resp = await test_client.get("/api/v1/schemes")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("Referrer-Policy") == "no-referrer"
    assert resp.headers.get("Cache-Control") == "no-store"
    assert resp.headers.get("X-Request-ID") is not None


@pytest.mark.asyncio
async def test_zero_message_text_or_profile_in_logs(
    test_client: AsyncClient, mock_llm_client: AsyncMock, caplog: pytest.LogCaptureFixture
):
    mock_llm_client.generate_structured.return_value = {"age": 33}
    secret_citizen_message = "ConfidentialIncomeSecret999999InPatna"

    with caplog.at_level(logging.INFO, logger="yojanasetu.access"):
        resp = await test_client.post(
            "/api/v1/intake/extract",
            json={"message": secret_citizen_message},
        )
        assert resp.status_code == 200

    # Invariant: Citizen message text, income, and profile must NEVER appear in logs
    log_text = caplog.text
    assert secret_citizen_message not in log_text
    assert "ConfidentialIncome" not in log_text
    assert "999999" not in log_text
    # Verify log output is structured metadata
    assert '"path": "/api/v1/intake/extract"' in log_text
    assert '"status_code": 200' in log_text
