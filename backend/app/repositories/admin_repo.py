"""Repository for administrator credentials and permission verification."""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class AdminRepository:
    """Handles administrator account lookups."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["admins"]

    async def get_by_username(self, username: str) -> dict[str, Any] | None:
        """Fetch administrator record by unique username."""
        return await self.collection.find_one({"username": username})
