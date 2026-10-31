"""Repository for managing scheme chunks and Atlas Vector Search queries."""

from typing import Any

from pymongo.asynchronous.database import AsyncDatabase

from app.schemas.chunk import SchemeChunk, SchemeChunkCreate


class ChunkRepository:
    """Manages knowledge chunk storage and Atlas Vector Search retrieval."""

    def __init__(self, db: AsyncDatabase):
        self.collection = db["scheme_chunks"]

    @staticmethod
    def _doc_to_chunk(doc: dict[str, Any]) -> SchemeChunk:
        """Convert BSON document to validated Pydantic SchemeChunk model."""
        data = dict(doc)
        if "_id" in data:
            data["id"] = str(data.pop("_id"))
        return SchemeChunk.model_validate(data)

    async def create_chunks(self, chunks: list[SchemeChunkCreate]) -> list[str]:
        """Insert multiple chunk records into scheme_chunks."""
        if not chunks:
            return []
        docs = [chunk.model_dump() for chunk in chunks]
        result = await self.collection.insert_many(docs)
        return [str(inserted_id) for inserted_id in result.inserted_ids]

    async def get_chunks_by_scheme_id(self, scheme_id: str) -> list[SchemeChunk]:
        """Fetch all chunks for a given scheme identifier."""
        clean_scheme_id = str(scheme_id).strip()
        cursor = self.collection.find({"scheme_id": clean_scheme_id})
        docs = await cursor.to_list(length=200)
        return [self._doc_to_chunk(d) for d in docs]

    async def delete_chunks_by_scheme_id(self, scheme_id: str) -> int:
        """Delete all chunks associated with a scheme identifier."""
        clean_scheme_id = str(scheme_id).strip()
        result = await self.collection.delete_many({"scheme_id": clean_scheme_id})
        return result.deleted_count

    async def vector_search(
        self,
        query_vector: list[float],
        limit: int = 5,
        section: str | None = None,
        scheme_id: str | None = None,
    ) -> list[SchemeChunk]:
        """Retrieve top matching chunks using MongoDB Atlas Vector Search."""
        bounded_limit = max(1, min(limit, 20))

        vector_search_stage: dict[str, Any] = {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": bounded_limit * 10,
                "limit": bounded_limit,
            }
        }

        # Whitelisted filters
        filter_doc: dict[str, Any] = {}
        if section:
            filter_doc["section"] = str(section).strip().lower()
        if scheme_id:
            filter_doc["scheme_id"] = str(scheme_id).strip()

        if filter_doc:
            vector_search_stage["$vectorSearch"]["filter"] = filter_doc

        pipeline = [
            vector_search_stage,
            {
                "$project": {
                    "_id": 1,
                    "scheme_id": 1,
                    "section": 1,
                    "text": 1,
                    "embedding": 1,
                    "source_url": 1,
                    "page": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        cursor = self.collection.aggregate(pipeline)
        docs = await cursor.to_list(length=bounded_limit)
        return [self._doc_to_chunk(d) for d in docs]
