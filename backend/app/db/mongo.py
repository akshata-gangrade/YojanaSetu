"""MongoDB client management and database session lifecycle."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


class MongoDBManager:
    """Manages asynchronous MongoDB connection lifecycle."""

    client: AsyncIOMotorClient | None = None

    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        """Obtain or initialize motor client."""
        if cls.client is None:
            settings = get_settings()
            cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
        return cls.client

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get application database handle."""
        settings = get_settings()
        return cls.get_client()[settings.MONGODB_DB]

    @classmethod
    def close_client(cls) -> None:
        """Close active client connection pool."""
        if cls.client is not None:
            cls.client.close()
            cls.client = None


async def get_db() -> AsyncIOMotorDatabase:
    """FastAPI dependency yielding database handle."""
    return MongoDBManager.get_database()
