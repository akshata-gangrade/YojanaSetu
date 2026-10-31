"""Repositories package exporting database handlers, protocols, and test fakes."""

from app.repositories.admin_repo import AdminRepository
from app.repositories.audit_repo import AuditRepository
from app.repositories.base import (
    IAdminRepository,
    IAuditRepository,
    IChunkRepository,
    IFeedbackRepository,
    ISchemeRepository,
)
from app.repositories.chunk_repo import ChunkRepository
from app.repositories.fakes import (
    FakeAdminRepository,
    FakeAuditRepository,
    FakeChunkRepository,
    FakeFeedbackRepository,
    FakeSchemeRepository,
)
from app.repositories.feedback_repo import FeedbackRepository
from app.repositories.scheme_repo import SchemeRepository

__all__ = [
    "AdminRepository",
    "AuditRepository",
    "ChunkRepository",
    "FakeAdminRepository",
    "FakeAuditRepository",
    "FakeChunkRepository",
    "FakeFeedbackRepository",
    "FakeSchemeRepository",
    "FeedbackRepository",
    "IAdminRepository",
    "IAuditRepository",
    "IChunkRepository",
    "IFeedbackRepository",
    "ISchemeRepository",
    "SchemeRepository",
]
