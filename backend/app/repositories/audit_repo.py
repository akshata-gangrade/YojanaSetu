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
        doc["id"] = str(result.inserted_id)
        return AuditLog.model_validate(doc)

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
