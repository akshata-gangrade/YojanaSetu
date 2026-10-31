"""Repository for querying and managing verified government schemes."""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class SchemeRepository:
    """Handles persistence and retrieval of schemes.

    Product rule: Only schemes with status 'verified' are
    returned to user-facing queries.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["schemes"]

    async def get_verified_schemes(self) -> list[dict[str, Any]]:
        """Fetch all schemes verified by an administrator against official sources."""
        cursor = self.collection.find({"status": "verified"})
        return await cursor.to_list(length=100)
