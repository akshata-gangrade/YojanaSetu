"""In-memory fake repositories for high-speed, isolated unit testing."""

import math
import uuid
from datetime import UTC, datetime
from typing import Any

from app.schemas.admin import AdminUserCreate, AdminUserInDB
from app.schemas.audit import AuditLog
from app.schemas.chunk import SchemeChunk, SchemeChunkCreate
from app.schemas.enums import SchemeStatus
from app.schemas.feedback import Feedback, FeedbackCreate
from app.schemas.scheme import Scheme, SchemeCreate, SchemeUpdate


class FakeSchemeRepository:
    """In-memory fake scheme repository replicating MongoDB query semantics."""

    def __init__(
        self,
        include_sample_schemes: bool = False,
        include_unverified_schemes: bool | None = None,
    ) -> None:
        self._schemes: dict[str, dict[str, Any]] = {}
        self._include_sample_schemes = include_sample_schemes
        if include_unverified_schemes is None:
            from app.core.config import get_settings

            self._include_unverified_schemes = get_settings().PUBLISH_UNREVIEWED_SCHEMES
        else:
            self._include_unverified_schemes = include_unverified_schemes

    @staticmethod
    def _doc_to_scheme(doc: dict[str, Any]) -> Scheme:
        data = dict(doc)
        if "_id" in data:
            data["id"] = str(data.pop("_id"))
        return Scheme.model_validate(data)

    async def get_by_slug(self, slug: str) -> Scheme | None:
        data = self._schemes.get(slug.strip())
        if not data:
            return None
        return self._doc_to_scheme(data)

    async def get_by_id_or_slug(self, identifier: str) -> Scheme | None:
        clean = identifier.strip()
        for s in self._schemes.values():
            if s.get("id") == clean or s.get("slug") == clean:
                return self._doc_to_scheme(s)
        return None

    async def get_admin_schemes(
        self,
        status: SchemeStatus | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Scheme]:
        results: list[dict[str, Any]] = []
        for s in self._schemes.values():
            if status is not None:
                stat_val = (
                    status.value if isinstance(status, SchemeStatus) else str(status)
                )
                if s.get("status") != stat_val:
                    continue
            if search:
                term = search.strip().lower()
                name = s.get("name", "").lower()
                name_hi = s.get("name_hi", "").lower()
                slug = s.get("slug", "").lower()
                if term not in name and term not in name_hi and term not in slug:
                    continue
            results.append(s)
        results.sort(key=lambda x: str(x.get("updated_at", "")), reverse=True)
        return [self._doc_to_scheme(r) for r in results[skip : skip + limit]]

    async def count_admin_schemes(
        self,
        status: SchemeStatus | None = None,
        search: str | None = None,
    ) -> int:
        count = 0
        for s in self._schemes.values():
            if status is not None:
                stat_val = (
                    status.value if isinstance(status, SchemeStatus) else str(status)
                )
                if s.get("status") != stat_val:
                    continue
            if search:
                term = search.strip().lower()
                name = s.get("name", "").lower()
                name_hi = s.get("name_hi", "").lower()
                slug = s.get("slug", "").lower()
                if term not in name and term not in name_hi and term not in slug:
                    continue
            count += 1
        return count

    async def get_verified_schemes(
        self,
        skip: int = 0,
        limit: int = 50,
        state: str | None = None,
        level: str | None = None,
        include_samples: bool | None = None,
        include_unverified: bool | None = None,
    ) -> list[Scheme]:
        effective_include_samples = (
            self._include_sample_schemes if include_samples is None else include_samples
        )
        effective_include_unverified = (
            self._include_unverified_schemes
            if include_unverified is None
            else include_unverified
        )
        allowed_statuses = {SchemeStatus.VERIFIED.value}
        if effective_include_unverified:
            allowed_statuses.add(SchemeStatus.NEEDS_REVIEW.value)

        results: list[dict[str, Any]] = []
        for s in self._schemes.values():
            if s.get("status") not in allowed_statuses:
                continue
            if not effective_include_samples and s.get("is_sample", False):
                continue
            if state and s.get("state") != state.strip().lower():
                continue
            if level and s.get("level") != level.strip().lower():
                continue
            results.append(s)

        paged = results[skip : skip + limit]
        return [self._doc_to_scheme(r) for r in paged]

    async def count_verified(
        self,
        state: str | None = None,
        level: str | None = None,
        include_samples: bool | None = None,
        include_unverified: bool | None = None,
    ) -> int:
        effective_include_samples = (
            self._include_sample_schemes if include_samples is None else include_samples
        )
        effective_include_unverified = (
            self._include_unverified_schemes
            if include_unverified is None
            else include_unverified
        )
        allowed_statuses = {SchemeStatus.VERIFIED.value}
        if effective_include_unverified:
            allowed_statuses.add(SchemeStatus.NEEDS_REVIEW.value)

        count = 0
        for s in self._schemes.values():
            if s.get("status") not in allowed_statuses:
                continue
            if not effective_include_samples and s.get("is_sample", False):
                continue
            if state and s.get("state") != state.strip().lower():
                continue
            if level and s.get("level") != level.strip().lower():
                continue
            count += 1
        return count

    async def create_scheme(self, scheme: SchemeCreate) -> Scheme:
        if scheme.slug in self._schemes:
            raise ValueError(f"Scheme with slug '{scheme.slug}' already exists.")
        doc = scheme.model_dump()
        doc["id"] = str(uuid.uuid4())
        self._schemes[scheme.slug] = doc
        return self._doc_to_scheme(doc)

    async def update_scheme(
        self, slug: str, update_data: SchemeUpdate
    ) -> Scheme | None:
        clean_slug = slug.strip()
        if clean_slug not in self._schemes:
            return None
        existing = dict(self._schemes[clean_slug])
        updates = update_data.model_dump(exclude_unset=True)
        updates["updated_at"] = datetime.now(UTC)
        existing.update(updates)
        self._schemes[clean_slug] = existing
        return self._doc_to_scheme(existing)

    async def delete_sample_schemes(self) -> int:
        to_delete = [
            slug for slug, s in self._schemes.items() if s.get("is_sample", False)
        ]
        for slug in to_delete:
            del self._schemes[slug]
        return len(to_delete)


class FakeChunkRepository:
    """In-memory fake chunk repository with mock vector cosine similarity."""

    def __init__(self) -> None:
        self._chunks: list[dict[str, Any]] = []

    async def create_chunks(self, chunks: list[SchemeChunkCreate]) -> list[str]:
        ids: list[str] = []
        for c in chunks:
            doc = c.model_dump()
            cid = str(uuid.uuid4())
            doc["id"] = cid
            self._chunks.append(doc)
            ids.append(cid)
        return ids

    async def get_chunks_by_scheme_id(self, scheme_id: str) -> list[SchemeChunk]:
        clean_id = scheme_id.strip()
        matched = [c for c in self._chunks if c.get("scheme_id") == clean_id]
        return [SchemeChunk.model_validate(c) for c in matched]

    async def delete_chunks_by_scheme_id(self, scheme_id: str) -> int:
        clean_id = scheme_id.strip()
        before_count = len(self._chunks)
        self._chunks = [c for c in self._chunks if c.get("scheme_id") != clean_id]
        return before_count - len(self._chunks)

    @staticmethod
    def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
        """Compute cosine similarity between two float vectors."""
        if len(v1) != len(v2) or not v1:
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2, strict=False))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    async def vector_search(
        self,
        query_vector: list[float],
        limit: int = 5,
        section: str | None = None,
        scheme_id: str | None = None,
    ) -> list[SchemeChunk]:
        scored: list[tuple[float, dict[str, Any]]] = []
        for c in self._chunks:
            if section and c.get("section") != section:
                continue
            if scheme_id and c.get("scheme_id") != scheme_id:
                continue
            emb = c.get("embedding", [])
            score = self._cosine_similarity(query_vector, emb)
            scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:limit]
        results: list[SchemeChunk] = []
        for sc, c in top:
            doc = dict(c)
            doc["score"] = sc
            results.append(SchemeChunk.model_validate(doc))
        return results


class FakeAdminRepository:
    """In-memory fake admin repository for authentication unit tests."""

    def __init__(self) -> None:
        self._admins: dict[str, dict[str, Any]] = {}

    async def get_by_email(self, email: str) -> AdminUserInDB | None:
        clean = email.strip().lower()
        data = self._admins.get(clean)
        if not data:
            return None
        return AdminUserInDB.model_validate(data)

    async def create_admin(self, user: AdminUserCreate) -> AdminUserInDB:
        clean = user.email.strip().lower()
        if clean in self._admins:
            raise ValueError(f"Admin with email '{clean}' already exists.")
        doc = user.model_dump()
        doc["email"] = clean
        doc["id"] = str(uuid.uuid4())
        self._admins[clean] = doc
        return AdminUserInDB.model_validate(doc)

    async def update_login_attempts(
        self, email: str, failed_logins: int, locked_until: datetime | None
    ) -> bool:
        clean = email.strip().lower()
        if clean not in self._admins:
            return False
        self._admins[clean]["failed_logins"] = failed_logins
        self._admins[clean]["locked_until"] = locked_until
        return True

    async def reset_failed_logins(self, email: str) -> bool:
        clean = email.strip().lower()
        if clean not in self._admins:
            return False
        self._admins[clean]["failed_logins"] = 0
        self._admins[clean]["locked_until"] = None
        return True

    async def count_admins(self) -> int:
        return len(self._admins)


class FakeAuditRepository:
    """In-memory fake append-only audit repository."""

    def __init__(self) -> None:
        self._logs: list[dict[str, Any]] = []

    async def log_event(
        self,
        actor: str,
        action: str,
        target: str,
        diff: dict[str, Any] | None = None,
    ) -> AuditLog:
        doc = {
            "id": str(uuid.uuid4()),
            "actor": actor.strip(),
            "action": action.strip(),
            "target": target.strip(),
            "timestamp": datetime.now(UTC),
            "diff": diff,
        }
        self._logs.append(doc)
        return AuditLog.model_validate(doc)

    async def get_by_target(self, target: str, limit: int = 50) -> list[AuditLog]:
        clean_target = target.strip()
        matched = [entry for entry in self._logs if entry["target"] == clean_target]
        matched.sort(key=lambda x: x["timestamp"], reverse=True)
        return [AuditLog.model_validate(entry) for entry in matched[:limit]]

    async def get_logs(
        self, skip: int = 0, limit: int = 50, target: str | None = None
    ) -> list[AuditLog]:
        matched = self._logs
        if target:
            clean_target = target.strip()
            matched = [entry for entry in matched if entry["target"] == clean_target]
        sorted_logs = sorted(matched, key=lambda x: x["timestamp"], reverse=True)
        return [
            AuditLog.model_validate(entry)
            for entry in sorted_logs[skip : skip + limit]
        ]

    async def count_logs(self, target: str | None = None) -> int:
        if target:
            clean_target = target.strip()
            return sum(1 for entry in self._logs if entry["target"] == clean_target)
        return len(self._logs)


class FakeFeedbackRepository:
    """In-memory fake anonymous feedback repository."""

    def __init__(self) -> None:
        self._feedback: list[dict[str, Any]] = []

    async def create_feedback(self, feedback: FeedbackCreate) -> Feedback:
        doc = feedback.model_dump()
        doc["id"] = str(uuid.uuid4())
        self._feedback.append(doc)
        return Feedback.model_validate(doc)

    async def get_feedback_by_scheme(
        self, scheme_id: str, limit: int = 100
    ) -> list[Feedback]:
        clean_id = scheme_id.strip()
        matched = [f for f in self._feedback if f["scheme_id"] == clean_id]
        matched.sort(key=lambda x: x["created_at"], reverse=True)
        return [Feedback.model_validate(f) for f in matched[:limit]]
