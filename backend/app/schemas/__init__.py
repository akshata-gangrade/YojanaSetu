"""Pydantic schemas and data contracts across YojanaSetu."""

from app.schemas.admin import (
    AdminUser,
    AdminUserBase,
    AdminUserCreate,
    AdminUserInDB,
)
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
from app.schemas.audit import (
    AuditLog,
    AuditLogBase,
    AuditLogCreate,
)
from app.schemas.chunk import (
    SchemeChunk,
    SchemeChunkBase,
    SchemeChunkCreate,
)
from app.schemas.criteria import (
    Criterion,
    EligibilityCriteria,
)
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
from app.schemas.feedback import (
    Feedback,
    FeedbackBase,
    FeedbackCreate,
)
from app.schemas.health import HealthResponse
from app.schemas.scheme import (
    Scheme,
    SchemeBase,
    SchemeCreate,
    SchemeUpdate,
)
from app.schemas.user_profile import UserProfile

__all__ = [
    "AdminRole",
    "AdminUser",
    "AdminUserBase",
    "AdminUserCreate",
    "AdminUserInDB",
    "AuditLog",
    "AuditLogBase",
    "AuditLogCreate",
    "ChunkSection",
    "Criterion",
    "CriterionField",
    "CriterionOperator",
    "DisabilityStatus",
    "EducationLevel",
    "EligibilityCriteria",
    "Feedback",
    "FeedbackBase",
    "FeedbackCreate",
    "FeedbackResponse",
    "FeedbackVote",
    "Gender",
    "HealthResponse",
    "IndianState",
    "IntakeExtractRequest",
    "IntakeExtractResponse",
    "MaritalStatus",
    "MatchRequest",
    "MatchResponse",
    "Occupation",
    "PaginatedSchemesResponse",
    "ResidenceType",
    "Scheme",
    "SchemeAskRequest",
    "SchemeAskResponse",
    "SchemeBase",
    "SchemeCreate",
    "SchemeLevel",
    "SchemeMatchItem",
    "SchemeStatus",
    "SchemeUpdate",
    "SchemeChunk",
    "SchemeChunkBase",
    "SchemeChunkCreate",
    "SocialCategory",
    "UserProfile",
]
