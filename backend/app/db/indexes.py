"""Index definitions and setup procedures for MongoDB and Atlas Vector Search."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.logging import logger


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create essential unique and query indexes across collections."""
    logger.info("Ensuring database indexes...")

    # Unique index for schemes slug
    await db["schemes"].create_index("slug", unique=True)
    # Filter index for verified status
    await db["schemes"].create_index("status")

    # Admin username index
    await db["admins"].create_index("username", unique=True)

    # Chunk scheme reference index
    await db["chunks"].create_index("scheme_id")

    logger.info("Indexes verified successfully.")
