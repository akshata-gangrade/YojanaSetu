"""Repository interface contracts (protocols) for clean architecture and fakes."""

from datetime import datetime
from typing import Any, Protocol

from app.schemas.admin import AdminUserCreate, AdminUserInDB
from app.schemas.audit import AuditLog
from app.schemas.chunk import SchemeChunk, SchemeChunkCreate
from app.schemas.feedback import Feedback, FeedbackCreate
from app.schemas.scheme import Scheme, SchemeCreate, SchemeUpdate


class ISchemeRepository(Protocol):
    """Protocol for scheme persistence and verified retrieval."""

    async def get_by_slug(self, slug: str) -> Scheme | None:
        """Fetch single scheme by unique slug."""
        ...

    async def get_verified_schemes(
        self,
        skip: int = 0,
        limit: int = 50,
        state: str | None = None,
        level: str | None = None,
        include_samples: bool | None = None,
    ) -> list[Scheme]:
        """Fetch verified schemes with whitelisted filters."""
        ...

    async def count_verified(
        self,
        state: str | None = None,
        level: str | None = None,
        include_samples: bool | None = None,
    ) -> int:
        """Count verified schemes matching whitelisted filters."""
        ...

    async def create_scheme(self, scheme: SchemeCreate) -> Scheme:
        """Insert a new scheme record."""
        ...

    async def update_scheme(
        self, slug: str, update_data: SchemeUpdate
    ) -> Scheme | None:
        """Update an existing scheme by slug."""
        ...

    async def delete_sample_schemes(self) -> int:
        """Purge all schemes marked is_sample: true."""
        ...


class IChunkRepository(Protocol):
    """Protocol for vector chunk storage and semantic retrieval."""

    async def create_chunks(self, chunks: list[SchemeChunkCreate]) -> list[str]:
        """Store multiple knowledge chunks."""
        ...

    async def get_chunks_by_scheme_id(self, scheme_id: str) -> list[SchemeChunk]:
        """Retrieve chunks belonging to a specific scheme."""
        ...

    async def delete_chunks_by_scheme_id(self, scheme_id: str) -> int:
        """Delete all chunks belonging to a scheme."""
        ...

    async def vector_search(
        self,
        query_vector: list[float],
        limit: int = 5,
        section: str | None = None,
        scheme_id: str | None = None,
    ) -> list[SchemeChunk]:
        """Retrieve top-k chunks by vector similarity."""
        ...


class IAdminRepository(Protocol):
    """Protocol for admin user authentication and security tracking."""

    async def get_by_email(self, email: str) -> AdminUserInDB | None:
        """Fetch administrator by unique email."""
        ...

    async def create_admin(self, user: AdminUserCreate) -> AdminUserInDB:
        """Provision a new administrator account."""
        ...

    async def update_login_attempts(
        self, email: str, failed_logins: int, locked_until: datetime | None
    ) -> bool:
        """Update consecutive failed attempts and optional lockout."""
        ...

    async def reset_failed_logins(self, email: str) -> bool:
        """Reset consecutive failed logins to zero after successful authentication."""
        ...


class IAuditRepository(Protocol):
    """Protocol for append-only audit trail logging."""

    async def log_event(
        self,
        actor: str,
        action: str,
        target: str,
        diff: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Append an immutable audit entry."""
        ...

    async def get_by_target(self, target: str, limit: int = 50) -> list[AuditLog]:
        """Query audit log history by target identifier."""
        ...


class IFeedbackRepository(Protocol):
    """Protocol for anonymous feedback collection."""

    async def create_feedback(self, feedback: FeedbackCreate) -> Feedback:
        """Record an anonymous helpful or not-helpful feedback entry."""
        ...

    async def get_feedback_by_scheme(
        self, scheme_id: str, limit: int = 100
    ) -> list[Feedback]:
        """Fetch anonymous feedback entries for a specific scheme."""
        ...
