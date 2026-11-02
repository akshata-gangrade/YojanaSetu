"""Repository for administrator accounts and authentication security tracking."""

from datetime import datetime
from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.schemas.admin import AdminUserCreate, AdminUserInDB


class AdminRepository:
    """Manages administrator credentials, roles, and lockout states."""

    def __init__(self, db: AsyncDatabase):
        self.collection = db["admin_users"]

    @staticmethod
    def _doc_to_admin(doc: dict[str, Any]) -> AdminUserInDB:
        """Convert BSON document to validated Pydantic AdminUserInDB model."""
        data = dict(doc)
        if "_id" in data:
            data["id"] = str(data.pop("_id"))
        return AdminUserInDB.model_validate(data)

    async def get_by_email(self, email: str) -> AdminUserInDB | None:
        """Fetch administrator record by unique email."""
        clean_email = str(email).strip().lower()
        doc = await self.collection.find_one({"email": clean_email})
        if not doc:
            return None
        return self._doc_to_admin(doc)

    async def create_admin(self, user: AdminUserCreate) -> AdminUserInDB:
        """Insert a newly provisioned administrator account."""
        doc = user.model_dump()
        doc["email"] = doc["email"].strip().lower()
        result = await self.collection.insert_one(doc)
        if "_id" not in doc and hasattr(result, "inserted_id"):
            doc["_id"] = result.inserted_id
        return self._doc_to_admin(doc)

    async def update_login_attempts(
        self, email: str, failed_logins: int, locked_until: datetime | None
    ) -> bool:
        """Record consecutive failed authentication attempts and optional lockout."""
        clean_email = str(email).strip().lower()
        result = await self.collection.update_one(
            {"email": clean_email},
            {"$set": {"failed_logins": failed_logins, "locked_until": locked_until}},
        )
        return result.modified_count > 0

    async def reset_failed_logins(self, email: str) -> bool:
        """Reset consecutive failed logins to zero upon successful authentication."""
        clean_email = str(email).strip().lower()
        result = await self.collection.update_one(
            {"email": clean_email},
            {"$set": {"failed_logins": 0, "locked_until": None}},
        )
        return result.modified_count > 0

    async def count_admins(self) -> int:
        """Count total registered administrator accounts."""
        return await self.collection.count_documents({})
