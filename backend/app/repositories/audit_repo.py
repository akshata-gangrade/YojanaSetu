"""Repository for administrative audit trails and operational logging."""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class AuditRepository:
    """Stores scheme modification history and admin verification events."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["audit_logs"]

    async def log_event(
        self, event_type: str, actor: str, details: dict[str, Any]
    ) -> None:
        """Record an administrative audit log entry without sensitive personal data."""
        await self.collection.insert_one(
            {
                "event_type": event_type,
                "actor": actor,
                "details": details,
            }
        )
