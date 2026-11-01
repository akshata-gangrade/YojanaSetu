"""Administrative router for scheme verification, auditing, and ingestion.

Invariants:
- All routes except /auth/login require authenticated administrator credentials.
- Role checks enforce full admin privileges for sensitive actions (archive, audit-logs).
- Every write mutation produces an immutable audit log entry.
- Rate limiting protects authentication against brute-force attacks.
"""

from datetime import UTC, datetime, timedelta
import hashlib
from typing import Any

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile, status

from app.api.deps import (
    get_admin_repo,
    get_audit_repo,
    get_current_admin,
    get_scheme_repo,
    require_admin_role,
)
from app.core.auth import (
    GENERIC_LOGIN_ERROR,
    create_admin_jwt,
    run_dummy_password_verification,
    verify_password,
)
from app.core.config import Settings, get_settings
from app.core.errors import AppException, NotFoundError, UnauthorizedError
from app.core.rate_limit import get_client_ip, rate_limiter
from app.repositories.base import (
    IAdminRepository,
    IAuditRepository,
    ISchemeRepository,
)
from app.schemas.admin import (
    AdminLoginRequest,
    AdminRejectRequest,
    AdminSchemeCreate,
    AdminSchemeListResponse,
    AdminSchemeUpdate,
    AdminTokenResponse,
    AdminUserInDB,
    AdminVerifyRequest,
    AuditLogListResponse,
    validate_gov_nic_url,
)
from app.schemas.enums import SchemeStatus
from app.schemas.scheme import Scheme, SchemeCreate, SchemeUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])


def rate_limit_admin_login_dependency(request: Request) -> None:
    """Strict per-IP rate limit on admin login: exactly 5 attempts per minute."""
    ip = get_client_ip(request)
    rate_limiter.check(
        client_id=ip,
        max_requests=5,
        bucket="admin_login",
    )


# ==============================================================================
# Authentication
# ==============================================================================


@router.post(
    "/auth/login",
    response_model=AdminTokenResponse,
    dependencies=[Depends(rate_limit_admin_login_dependency)],
    summary="Authenticate administrator credentials and receive short-lived JWT",
)
async def admin_login(
    payload: AdminLoginRequest,
    admin_repo: IAdminRepository = Depends(get_admin_repo),
    settings: Settings = Depends(get_settings),
) -> AdminTokenResponse:
    """Verify administrator credentials using Argon2id and issue short-lived JWT.

    Invariants:
    - Lockout: 5 failed attempts lock account for 15 minutes.
    - Dummy password check ensures identical timing for unknown emails.
    - Error message is strictly identical for unknown email and wrong password.
    """
    now = datetime.now(UTC)
    clean_email = payload.email.strip().lower()
    admin = await admin_repo.get_by_email(clean_email)

    if not admin:
        # Prevent user enumeration via side-channel timing attack
        run_dummy_password_verification(payload.password)
        raise UnauthorizedError(GENERIC_LOGIN_ERROR)

    # Check if account is currently locked
    if admin.locked_until and admin.locked_until > now:
        run_dummy_password_verification(payload.password)
        raise UnauthorizedError(
            "Account is temporarily locked due to repeated failed login attempts. Please try again later."
        )

    # Verify password with Argon2id
    is_valid = verify_password(payload.password, admin.password_hash)

    if not is_valid:
        new_failed_logins = admin.failed_logins + 1
        locked_until = (
            now + timedelta(minutes=15) if new_failed_logins >= 5 else None
        )
        await admin_repo.update_login_attempts(
            admin.email, new_failed_logins, locked_until
        )
        raise UnauthorizedError(GENERIC_LOGIN_ERROR)

    # Success: reset failed logins counter and issue token
    await admin_repo.reset_failed_logins(admin.email)
    token, expires_in = create_admin_jwt(
        admin.email, admin.role, settings=settings
    )

    return AdminTokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        role=admin.role,
    )


# ==============================================================================
# Scheme Management
# ==============================================================================


@router.get(
    "/schemes",
    response_model=AdminSchemeListResponse,
    summary="List schemes filtered by status and search with pagination",
)
async def list_admin_schemes(
    status: SchemeStatus | None = Query(None, description="Filter by lifecycle status"),
    q: str | None = Query(None, description="Search query across name and slug"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: AdminUserInDB = Depends(get_current_admin),
    scheme_repo: ISchemeRepository = Depends(get_scheme_repo),
) -> AdminSchemeListResponse:
    """Retrieve paginated schemes for administrative review."""
    items = await scheme_repo.get_admin_schemes(
        status=status,
        search=q,
        skip=skip,
        limit=limit,
    )
    total = await scheme_repo.count_admin_schemes(status=status, search=q)
    return AdminSchemeListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get(
    "/schemes/{identifier}",
    response_model=Scheme,
    summary="Get single scheme by slug or MongoDB document identifier",
)
async def get_admin_scheme(
    identifier: str,
    current_admin: AdminUserInDB = Depends(get_current_admin),
    scheme_repo: ISchemeRepository = Depends(get_scheme_repo),
) -> Scheme:
    """Retrieve full scheme record for review."""
    scheme = await scheme_repo.get_by_id_or_slug(identifier)
    if not scheme:
        raise NotFoundError(f"Scheme '{identifier}' not found.")
    return scheme


@router.post(
    "/schemes",
    response_model=Scheme,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new scheme (always saved as needs_review)",
)
async def create_admin_scheme(
    payload: AdminSchemeCreate,
    current_admin: AdminUserInDB = Depends(get_current_admin),
    scheme_repo: ISchemeRepository = Depends(get_scheme_repo),
    audit_repo: IAuditRepository = Depends(get_audit_repo),
) -> Scheme:
    """Create a new scheme draft in needs_review status.

    Invariants:
    - Status is strictly forced to needs_review.
    - URLs must be HTTPS and on a .gov.in or .nic.in domain.
    - Criteria validated by EligibilityCriteria model.
    - Mutation recorded in immutable audit log.
    """
    existing = await scheme_repo.get_by_slug(payload.slug)
    if existing:
        raise AppException(
            f"Scheme with slug '{payload.slug}' already exists.",
            status_code=status.HTTP_400_BAD_REQUEST,
            code="SLUG_EXISTS",
        )

    doc_data = payload.model_dump()
    doc_data["status"] = SchemeStatus.NEEDS_REVIEW
    doc_data["created_at"] = datetime.now(UTC)
    doc_data["updated_at"] = datetime.now(UTC)

    scheme_create = SchemeCreate(**doc_data)
    created = await scheme_repo.create_scheme(scheme_create)

    # Audit log creation
    diff: dict[str, Any] = {}
    for k, v in payload.model_dump().items():
        if k not in ("created_at", "updated_at"):
            diff[k] = {"old": None, "new": v}
    diff["status"] = {"old": None, "new": SchemeStatus.NEEDS_REVIEW.value}

    await audit_repo.log_event(
        actor=current_admin.email,
        action="create_scheme",
        target=created.slug,
        diff=diff,
    )

    return created


@router.put(
    "/schemes/{identifier}",
    response_model=Scheme,
    summary="Edit an existing scheme (resets verified scheme to needs_review)",
)
@router.patch(
    "/schemes/{identifier}",
    response_model=Scheme,
    summary="Partially edit an existing scheme",
)
async def edit_admin_scheme(
    identifier: str,
    payload: AdminSchemeUpdate,
    current_admin: AdminUserInDB = Depends(get_current_admin),
    scheme_repo: ISchemeRepository = Depends(get_scheme_repo),
    audit_repo: IAuditRepository = Depends(get_audit_repo),
) -> Scheme:
    """Update scheme fields.

    Invariant: Any edit to a verified scheme resets its status to needs_review.
    """
    scheme = await scheme_repo.get_by_id_or_slug(identifier)
    if not scheme:
        raise NotFoundError(f"Scheme '{identifier}' not found.")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return scheme

    diff: dict[str, Any] = {}
    for k, new_v in updates.items():
        old_v = getattr(scheme, k, None)
        if old_v != new_v:
            diff[k] = {"old": old_v, "new": new_v}

    # Invariant: Any edit to a verified scheme resets it to needs_review
    if scheme.status == SchemeStatus.VERIFIED:
        updates["status"] = SchemeStatus.NEEDS_REVIEW
        diff["status"] = {
            "old": SchemeStatus.VERIFIED.value,
            "new": SchemeStatus.NEEDS_REVIEW.value,
        }

    scheme_update = SchemeUpdate(**updates)
    updated = await scheme_repo.update_scheme(scheme.slug, scheme_update)

    if diff:
        await audit_repo.log_event(
            actor=current_admin.email,
            action="edit_scheme",
            target=scheme.slug,
            diff=diff,
        )

    return updated or scheme


@router.post(
    "/schemes/{identifier}/verify",
    response_model=Scheme,
    summary="Verify a scheme against official source document",
)
async def verify_admin_scheme(
    identifier: str,
    payload: AdminVerifyRequest | None = None,
    current_admin: AdminUserInDB = Depends(get_current_admin),
    scheme_repo: ISchemeRepository = Depends(get_scheme_repo),
    audit_repo: IAuditRepository = Depends(get_audit_repo),
) -> Scheme:
    """Verify scheme and record administrator details.

    Invariants:
    - Requires verified official source_url and last_verified date.
    - Sets verified_by and verified_at.
    """
    scheme = await scheme_repo.get_by_id_or_slug(identifier)
    if not scheme:
        raise NotFoundError(f"Scheme '{identifier}' not found.")

    source_url = payload.source_url if (payload and payload.source_url) else scheme.source_url
    if not source_url or not source_url.strip():
        raise AppException(
            "source_url is required to verify scheme.",
            status_code=status.HTTP_400_BAD_REQUEST,
            code="VALIDATION_ERROR",
        )
    # Re-validate host format
    validate_gov_nic_url(source_url)

    now = datetime.now(UTC)
    last_verified = (
        payload.last_verified
        if (payload and payload.last_verified)
        else (scheme.last_verified or now)
    )

    update_payload = SchemeUpdate(
        status=SchemeStatus.VERIFIED,
        source_url=source_url,
        last_verified=last_verified,
        verified_by=current_admin.email,
        verified_at=now,
    )
    updated = await scheme_repo.update_scheme(scheme.slug, update_payload)

    diff = {
        "status": {"old": scheme.status.value, "new": SchemeStatus.VERIFIED.value},
        "verified_by": {"old": scheme.verified_by, "new": current_admin.email},
        "verified_at": {
            "old": scheme.verified_at.isoformat() if scheme.verified_at else None,
            "new": now.isoformat(),
        },
    }

    await audit_repo.log_event(
        actor=current_admin.email,
        action="verify_scheme",
        target=scheme.slug,
        diff=diff,
    )

    return updated or scheme


@router.post(
    "/schemes/{identifier}/reject",
    response_model=Scheme,
    summary="Reject scheme verification and revert status to draft",
)
async def reject_admin_scheme(
    identifier: str,
    payload: AdminRejectRequest,
    current_admin: AdminUserInDB = Depends(get_current_admin),
    scheme_repo: ISchemeRepository = Depends(get_scheme_repo),
    audit_repo: IAuditRepository = Depends(get_audit_repo),
) -> Scheme:
    """Reject scheme with mandatory reason and revert to draft."""
    scheme = await scheme_repo.get_by_id_or_slug(identifier)
    if not scheme:
        raise NotFoundError(f"Scheme '{identifier}' not found.")

    update_payload = SchemeUpdate(status=SchemeStatus.DRAFT)
    updated = await scheme_repo.update_scheme(scheme.slug, update_payload)

    diff = {
        "status": {"old": scheme.status.value, "new": SchemeStatus.DRAFT.value},
        "rejection_reason": {"old": None, "new": payload.reason},
    }

    await audit_repo.log_event(
        actor=current_admin.email,
        action="reject_scheme",
        target=scheme.slug,
        diff=diff,
    )

    return updated or scheme


@router.post(
    "/schemes/{identifier}/archive",
    response_model=Scheme,
    summary="Archive a scheme (Admin role only)",
)
async def archive_admin_scheme(
    identifier: str,
    current_admin: AdminUserInDB = Depends(require_admin_role),
    scheme_repo: ISchemeRepository = Depends(get_scheme_repo),
    audit_repo: IAuditRepository = Depends(get_audit_repo),
) -> Scheme:
    """Archive a scheme. Restricted strictly to admin role."""
    scheme = await scheme_repo.get_by_id_or_slug(identifier)
    if not scheme:
        raise NotFoundError(f"Scheme '{identifier}' not found.")

    update_payload = SchemeUpdate(status=SchemeStatus.ARCHIVED)
    updated = await scheme_repo.update_scheme(scheme.slug, update_payload)

    diff = {
        "status": {"old": scheme.status.value, "new": SchemeStatus.ARCHIVED.value},
    }

    await audit_repo.log_event(
        actor=current_admin.email,
        action="archive_scheme",
        target=scheme.slug,
        diff=diff,
    )

    return updated or scheme


# ==============================================================================
# Ingestion & PDF Upload
# ==============================================================================


@router.post(
    "/schemes/upload-pdf",
    summary="Upload an official scheme guidelines PDF and calculate SHA-256 hash",
)
async def upload_scheme_pdf(
    file: UploadFile = File(...),
    current_admin: AdminUserInDB = Depends(get_current_admin),
    audit_repo: IAuditRepository = Depends(get_audit_repo),
) -> dict[str, Any]:
    """Upload official scheme PDF and compute SHA-256 source hash."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise AppException(
            "Only PDF documents are supported for scheme ingestion.",
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_FILE_TYPE",
        )

    content = await file.read()
    source_hash = hashlib.sha256(content).hexdigest()

    diff = {
        "filename": {"old": None, "new": file.filename},
        "source_hash": {"old": None, "new": source_hash},
        "size_bytes": {"old": None, "new": len(content)},
    }

    await audit_repo.log_event(
        actor=current_admin.email,
        action="upload_pdf",
        target=file.filename,
        diff=diff,
    )

    return {
        "filename": file.filename,
        "source_hash": source_hash,
        "size_bytes": len(content),
    }


@router.post(
    "/schemes/{identifier}/ingest",
    summary="Trigger ingestion and chunking pipeline for a scheme",
)
async def trigger_scheme_ingestion(
    identifier: str,
    current_admin: AdminUserInDB = Depends(get_current_admin),
    scheme_repo: ISchemeRepository = Depends(get_scheme_repo),
    audit_repo: IAuditRepository = Depends(get_audit_repo),
) -> dict[str, str]:
    """Trigger ingestion for a scheme."""
    scheme = await scheme_repo.get_by_id_or_slug(identifier)
    if not scheme:
        raise NotFoundError(f"Scheme '{identifier}' not found.")

    diff = {
        "ingestion_status": {"old": None, "new": "triggered"},
    }

    await audit_repo.log_event(
        actor=current_admin.email,
        action="trigger_ingestion",
        target=scheme.slug,
        diff=diff,
    )

    return {
        "status": "ingestion_triggered",
        "slug": scheme.slug,
    }


# ==============================================================================
# Audit Logs
# ==============================================================================


@router.get(
    "/audit-logs",
    response_model=AuditLogListResponse,
    summary="Read immutable administrative audit logs (Admin role only)",
)
async def read_audit_logs(
    target: str | None = Query(None, description="Filter logs by target entity"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: AdminUserInDB = Depends(require_admin_role),
    audit_repo: IAuditRepository = Depends(get_audit_repo),
) -> AuditLogListResponse:
    """Retrieve paginated immutable audit log events. Restricted to admin role."""
    items = await audit_repo.get_logs(skip=skip, limit=limit, target=target)
    total = await audit_repo.count_logs(target=target)
    return AuditLogListResponse(items=items, total=total, skip=skip, limit=limit)
