"""Database indexes for MongoDB collections and Atlas Vector Search."""

import asyncio
from typing import Any

from pymongo import ASCENDING, DESCENDING, IndexModel
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.operations import SearchIndexModel

from app.core.config import get_settings
from app.core.logging import logger


async def ensure_indexes(
    db: AsyncDatabase, include_vector: bool = False
) -> dict[str, list[str]]:
    """Create essential unique, compound, and TTL indexes across collections.

    Vector search index on Atlas is excluded by default and only created when
    explicitly requested with include_vector=True.
    """
    logger.info("Ensuring standard database indexes...")
    created_indexes: dict[str, list[str]] = {}

    # 1. schemes collection indexes
    schemes_col = db["schemes"]
    scheme_models = [
        IndexModel([("slug", ASCENDING)], unique=True, name="uniq_scheme_slug"),
        IndexModel(
            [("status", ASCENDING), ("state", ASCENDING), ("level", ASCENDING)],
            name="idx_status_state_level",
        ),
        IndexModel([("is_sample", ASCENDING)], name="idx_is_sample"),
    ]
    created_indexes["schemes"] = await schemes_col.create_indexes(scheme_models)

    # 2. admin_users collection indexes
    admin_col = db["admin_users"]
    admin_models = [
        IndexModel([("email", ASCENDING)], unique=True, name="uniq_admin_email"),
    ]
    created_indexes["admin_users"] = await admin_col.create_indexes(admin_models)

    # 3. scheme_chunks collection indexes
    chunks_col = db["scheme_chunks"]
    chunk_models = [
        IndexModel([("scheme_id", ASCENDING)], name="idx_chunk_scheme_id"),
        IndexModel([("section", ASCENDING)], name="idx_chunk_section"),
    ]
    created_indexes["scheme_chunks"] = await chunks_col.create_indexes(chunk_models)

    # 4. feedback collection indexes (with 90-day TTL index on created_at)
    feedback_col = db["feedback"]
    ttl_seconds = 90 * 24 * 3600  # 90 days = 7,776,000 seconds
    feedback_models = [
        IndexModel(
            [("created_at", ASCENDING)],
            expireAfterSeconds=ttl_seconds,
            name="ttl_feedback_90_days",
        ),
        IndexModel([("scheme_id", ASCENDING)], name="idx_feedback_scheme_id"),
    ]
    created_indexes["feedback"] = await feedback_col.create_indexes(feedback_models)

    # 5. audit_logs collection indexes
    audit_col = db["audit_logs"]
    audit_models = [
        IndexModel(
            [("target", ASCENDING), ("timestamp", DESCENDING)],
            name="idx_audit_target_timestamp",
        ),
    ]
    created_indexes["audit_logs"] = await audit_col.create_indexes(audit_models)

    logger.info("Standard database indexes verified successfully.")

    if include_vector:
        settings = get_settings()
        await create_vector_index(db, embedding_dim=settings.EMBEDDING_DIM)

    return created_indexes


async def create_vector_index(
    db: AsyncDatabase,
    embedding_dim: int,
    index_name: str = "vector_index",
    wait: bool = True,
    timeout_seconds: int = 300,
) -> str:
    """Create MongoDB Atlas Vector Search index on scheme_chunks.embedding.

    Atlas builds search indexes asynchronously. If wait=True, this function polls
    until the index status is READY or queryable.
    """
    logger.info(
        "Creating Atlas Vector Search index '%s' (dim=%d)...",
        index_name,
        embedding_dim,
    )
    chunks_col = db["scheme_chunks"]

    definition: dict[str, Any] = {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": embedding_dim,
                "similarity": "cosine",
            },
            {"type": "filter", "path": "section"},
            {"type": "filter", "path": "scheme_id"},
        ]
    }

    search_index_model = SearchIndexModel(
        definition=definition,
        name=index_name,
        type="vectorSearch",
    )

    result_name = await chunks_col.create_search_index(model=search_index_model)
    logger.info("Search index creation requested: %s", result_name)

    if wait:
        logger.info("Waiting for Atlas Vector Search index to become queryable...")
        elapsed = 0
        interval = 5
        while elapsed < timeout_seconds:
            try:
                cursor = chunks_col.list_search_indexes(name=index_name)
                indexes = await cursor.to_list(length=10)
                for idx in indexes:
                    if idx.get("name") == index_name:
                        status = idx.get("status")
                        queryable = idx.get("queryable", False)
                        if status == "READY" or queryable is True:
                            logger.info("Vector index '%s' is ready.", index_name)
                            return result_name
            except Exception as e:
                logger.warning("Error polling vector index status: %s", e)

            await asyncio.sleep(interval)
            elapsed += interval

        logger.warning(
            "Vector index not confirmed ready within %ds; building in background.",
            timeout_seconds,
        )

    return result_name
