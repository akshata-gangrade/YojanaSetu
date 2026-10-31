"""FastAPI dependency injection providers for repositories, clients, and services."""

from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.db.mongo import get_db
from app.repositories.base import IFeedbackRepository, ISchemeRepository
from app.repositories.feedback_repo import FeedbackRepository
from app.repositories.scheme_repo import SchemeRepository
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

