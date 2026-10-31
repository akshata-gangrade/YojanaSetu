"""Repository for anonymous scheme feedback collection."""

from typing import Any

from pymongo import DESCENDING
from pymongo.asynchronous.database import AsyncDatabase

from app.schemas.feedback import Feedback, FeedbackCreate


class FeedbackRepository:
    """Manages anonymous scheme helpfulness feedback entries.

    Invariants:
    - No citizen personal identifiers (name, IP, user ID, email) are recorded.
    - Documents expire automatically after 90 days via MongoDB TTL index.
    """

    def __init__(self, db: AsyncDatabase):
        self.collection = db["feedback"]

    @staticmethod
    def _doc_to_feedback(doc: dict[str, Any]) -> Feedback:
        """Convert BSON document to validated Pydantic Feedback model."""
        data = dict(doc)
        if "_id" in data:
            data["id"] = str(data.pop("_id"))
        return Feedback.model_validate(data)

    async def create_feedback(self, feedback: FeedbackCreate) -> Feedback:
        """Insert an anonymous feedback record."""
        doc = feedback.model_dump()
        result = await self.collection.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        return Feedback.model_validate(doc)

    async def get_feedback_by_scheme(
        self, scheme_id: str, limit: int = 100
    ) -> list[Feedback]:
        """Fetch anonymous feedback for a scheme in reverse chronological order."""
        clean_scheme_id = str(scheme_id).strip()
        bounded_limit = max(1, min(limit, 500))
        cursor = (
            self.collection.find({"scheme_id": clean_scheme_id})
            .sort("created_at", DESCENDING)
            .limit(bounded_limit)
        )
        docs = await cursor.to_list(length=bounded_limit)
        return [self._doc_to_feedback(d) for d in docs]
