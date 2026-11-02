"""Repository for append-only administrative audit trail logging."""

from datetime import UTC, datetime
from typing import Any

from pymongo import DESCENDING
from pymongo.asynchronous.database import AsyncDatabase

from app.schemas.audit import AuditLog, AuditLogCreate


class AuditRepository:
    """Manages immutable audit logging for administrative mutations.

    Invariant: Audit logs are append-only. There are no delete or update methods.
    """

    def __init__(self, db: AsyncDatabase):
        self.collection = db["audit_logs"]

    @staticmethod
    def _doc_to_audit(doc: dict[str, Any]) -> AuditLog:
        """Convert BSON document to validated Pydantic AuditLog model."""
        data = dict(doc)
        if "_id" in data:
            data["id"] = str(data.pop("_id"))
        return AuditLog.model_validate(data)

    async def log_event(
        self,
        actor: str,
        action: str,
        target: str,
        diff: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Append an immutable audit entry."""
        clean_actor = str(actor).strip()
        clean_action = str(action).strip()
        clean_target = str(target).strip()

        entry = AuditLogCreate(
            actor=clean_actor,
            action=clean_action,
            target=clean_target,
            timestamp=datetime.now(UTC),
            diff=diff,
        )

        doc = entry.model_dump()
        result = await self.collection.insert_one(doc)
        if "_id" not in doc and hasattr(result, "inserted_id"):
            doc["_id"] = result.inserted_id
        return self._doc_to_audit(doc)

    async def get_by_target(self, target: str, limit: int = 50) -> list[AuditLog]:
        """Query audit log history for a specific target in reverse order."""
        clean_target = str(target).strip()
        bounded_limit = max(1, min(limit, 200))
        cursor = (
            self.collection.find({"target": clean_target})
            .sort("timestamp", DESCENDING)
            .limit(bounded_limit)
        )
        docs = await cursor.to_list(length=bounded_limit)
        return [self._doc_to_audit(d) for d in docs]

    async def get_logs(
        self, skip: int = 0, limit: int = 50, target: str | None = None
    ) -> list[AuditLog]:
        """Fetch paginated audit log entries in reverse chronological order."""
        bounded_skip = max(0, skip)
        bounded_limit = max(1, min(limit, 100))
        query = {"target": str(target).strip()} if target else {}
        cursor = (
            self.collection.find(query)
            .sort("timestamp", DESCENDING)
            .skip(bounded_skip)
            .limit(bounded_limit)
        )
        docs = await cursor.to_list(length=bounded_limit)
        return [self._doc_to_audit(d) for d in docs]

    async def count_logs(self, target: str | None = None) -> int:
        """Count total audit log events matching optional target filter."""
        query = {"target": str(target).strip()} if target else {}
        return await self.collection.count_documents(query)
