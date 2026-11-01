"""FastAPI dependency injection providers for repositories, clients, and services."""

from datetime import UTC, datetime

from fastapi import Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.core.auth import decode_admin_jwt
from app.core.config import Settings, get_settings
from app.core.errors import ForbiddenError, UnauthorizedError
from app.db.mongo import get_db
from app.repositories.admin_repo import AdminRepository
from app.repositories.audit_repo import AuditRepository
from app.repositories.base import (
    IAdminRepository,
    IAuditRepository,
    IFeedbackRepository,
    ISchemeRepository,
)
from app.repositories.feedback_repo import FeedbackRepository
from app.repositories.scheme_repo import SchemeRepository
from app.schemas.admin import AdminUserInDB
from app.schemas.enums import AdminRole
from app.services.followup_selector import FollowupSelectorService
from app.services.intake_service import IntakeService
from app.services.llm_client import GroqClient, LLMClient
from app.services.match_service import MatchService
from app.services.profile_extractor import ProfileExtractorService
from app.services.rag_service import RAGService
from app.services.rule_engine import RuleEngineService


async def get_scheme_repo(db: AsyncDatabase = Depends(get_db)) -> ISchemeRepository:
    """Provide scheme repository instance."""
    return SchemeRepository(db)


async def get_feedback_repo(db: AsyncDatabase = Depends(get_db)) -> IFeedbackRepository:
    """Provide feedback repository instance."""
    return FeedbackRepository(db)


async def get_admin_repo(db: AsyncDatabase = Depends(get_db)) -> IAdminRepository:
    """Provide administrator repository instance."""
    return AdminRepository(db)


async def get_audit_repo(db: AsyncDatabase = Depends(get_db)) -> IAuditRepository:
    """Provide immutable audit log repository instance."""
    return AuditRepository(db)


async def get_current_admin(
    request: Request,
    admin_repo: IAdminRepository = Depends(get_admin_repo),
    settings: Settings = Depends(get_settings),
) -> AdminUserInDB:
    """Validate bearer token from Authorization header and authenticate administrator.

    Invariants:
    - Never uses cookies; strictly parses Authorization: Bearer <token>.
    - Validates fixed HS256 algorithm and all mandatory claims.
    - Rejects expired or tampered tokens with 401.
    - Rejects locked accounts with 401.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Missing or invalid Authorization header.")

    token = auth_header[7:].strip()
    if not token:
        raise UnauthorizedError("Authorization token cannot be empty.")

    payload = decode_admin_jwt(token, settings=settings)
    email = payload.get("sub")
    if not email:
        raise UnauthorizedError("Token missing valid subject identifier.")

    admin = await admin_repo.get_by_email(email)
    if not admin:
        raise UnauthorizedError("Administrator account not found.")

    if admin.locked_until and admin.locked_until > datetime.now(UTC):
        raise UnauthorizedError("Account is temporarily locked. Please try again later.")

    return admin


def require_admin_role(
    current_admin: AdminUserInDB = Depends(get_current_admin),
) -> AdminUserInDB:
    """Enforce full administrator authorization (rejects reviewers with 403 Forbidden)."""
    if current_admin.role != AdminRole.ADMIN:
        raise ForbiddenError("Admin privilege required for this administrative operation.")
    return current_admin


def get_llm_client() -> LLMClient:
    """Provide configured Groq LLM client instance."""
    return GroqClient()


def get_profile_extractor(
    llm_client: LLMClient = Depends(get_llm_client),
) -> ProfileExtractorService:
    """Provide citizen profile extractor service."""
    return ProfileExtractorService(llm_client)


def get_rule_engine() -> RuleEngineService:
    """Provide deterministic rule engine service."""
    return RuleEngineService()


def get_followup_selector(
    rule_engine: RuleEngineService = Depends(get_rule_engine),
) -> FollowupSelectorService:
    """Provide follow-up question selector service."""
    return FollowupSelectorService(rule_engine)


def get_intake_service(
    extractor: ProfileExtractorService = Depends(get_profile_extractor),
    scheme_repo: ISchemeRepository = Depends(get_scheme_repo),
    rule_engine: RuleEngineService = Depends(get_rule_engine),
    followup_selector: FollowupSelectorService = Depends(get_followup_selector),
) -> IntakeService:
    """Provide citizen intake orchestration service."""
    return IntakeService(
        extractor=extractor,
        scheme_repo=scheme_repo,
        rule_engine=rule_engine,
        followup_selector=followup_selector,
    )


def get_match_service(
    scheme_repo: ISchemeRepository = Depends(get_scheme_repo),
    rule_engine: RuleEngineService = Depends(get_rule_engine),
) -> MatchService:
    """Provide deterministic scheme matching service."""
    return MatchService(
        scheme_repo=scheme_repo,
        rule_engine=rule_engine,
    )


def get_rag_service() -> RAGService:
    """Provide scheme question answering RAG service."""
    return RAGService()

