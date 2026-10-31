"""Repository for querying, persisting, and verifying government schemes in MongoDB."""

from datetime import UTC, datetime
from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import get_settings
from app.schemas.enums import SchemeLevel, SchemeStatus
from app.schemas.scheme import Scheme, SchemeCreate, SchemeUpdate


class SchemeRepository:
    """Manages persistence and retrieval of schemes.

    Invariants:
    - Only schemes with status 'verified' are returned to user queries.
    - Sample schemes (is_sample: true) are excluded from production by default.
    - Queries are constructed exclusively from whitelisted, validated fields.
    """

    ALLOWED_FILTER_FIELDS = frozenset({"status", "state", "level", "is_sample"})

    def __init__(self, db: AsyncDatabase):
        self.collection = db["schemes"]

    @staticmethod
    def _doc_to_scheme(doc: dict[str, Any]) -> Scheme:
        """Convert MongoDB BSON document to validated Pydantic Scheme model."""
        data = dict(doc)
        if "_id" in data:
            data["id"] = str(data.pop("_id"))
        return Scheme.model_validate(data)

    def _build_whitelisted_query(
        self,
        status: SchemeStatus = SchemeStatus.VERIFIED,
        state: str | None = None,
        level: str | None = None,
        include_samples: bool = False,
    ) -> dict[str, Any]:
        """Build query filter exclusively from strictly validated fields."""
        query: dict[str, Any] = {"status": status.value}

        if not include_samples:
            query["is_sample"] = False

        if state is not None:
            # Validate state is non-empty string
            clean_state = str(state).strip().lower()
            if clean_state:
                query["state"] = clean_state

        if level is not None:
            clean_level = str(level).strip().lower()
            if clean_level in (SchemeLevel.CENTRAL.value, SchemeLevel.STATE.value):
                query["level"] = clean_level

        return query

    async def get_by_slug(self, slug: str) -> Scheme | None:
        """Fetch single scheme by unique slug."""
        clean_slug = str(slug).strip()
        doc = await self.collection.find_one({"slug": clean_slug})
        if not doc:
            return None
        return self._doc_to_scheme(doc)

    async def get_verified_schemes(
        self,
        skip: int = 0,
        limit: int = 50,
        state: str | None = None,
        level: str | None = None,
        include_samples: bool | None = None,
    ) -> list[Scheme]:
        """Fetch paginated verified schemes matching whitelisted filter criteria."""
        bounded_skip = max(0, skip)
        bounded_limit = max(1, min(limit, 100))

        effective_include_samples = (
            get_settings().INCLUDE_SAMPLE_SCHEMES
            if include_samples is None
            else include_samples
        )

        query = self._build_whitelisted_query(
            status=SchemeStatus.VERIFIED,
            state=state,
            level=level,
            include_samples=effective_include_samples,
        )

        cursor = self.collection.find(query).skip(bounded_skip).limit(bounded_limit)
        docs = await cursor.to_list(length=bounded_limit)
        return [self._doc_to_scheme(d) for d in docs]

    async def count_verified(
        self,
        state: str | None = None,
        level: str | None = None,
        include_samples: bool | None = None,
    ) -> int:
        """Count verified schemes matching whitelisted filter criteria."""
        effective_include_samples = (
            get_settings().INCLUDE_SAMPLE_SCHEMES
            if include_samples is None
            else include_samples
        )
        query = self._build_whitelisted_query(
            status=SchemeStatus.VERIFIED,
            state=state,
            level=level,
            include_samples=effective_include_samples,
        )
        return await self.collection.count_documents(query)

    async def create_scheme(self, scheme: SchemeCreate) -> Scheme:
        """Insert a newly structured scheme record."""
        doc = scheme.model_dump()
        result = await self.collection.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        return Scheme.model_validate(doc)

    async def update_scheme(
        self, slug: str, update_data: SchemeUpdate
    ) -> Scheme | None:
        """Update an existing scheme by unique slug using validated fields."""
        clean_slug = str(slug).strip()
        raw_updates = update_data.model_dump(exclude_unset=True)
        if not raw_updates:
            return await self.get_by_slug(clean_slug)

        raw_updates["updated_at"] = datetime.now(UTC)
        result = await self.collection.find_one_and_update(
            {"slug": clean_slug},
            {"$set": raw_updates},
            return_document=True,
        )
        if not result:
            return None
        return self._doc_to_scheme(result)

    async def delete_sample_schemes(self) -> int:
        """Purge all schemes marked is_sample: true."""
        result = await self.collection.delete_many({"is_sample": True})
        return result.deleted_count
