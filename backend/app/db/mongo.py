"""MongoDB client management and database lifecycle using AsyncMongoClient."""

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import get_settings


class MongoDBManager:
    """Manages asynchronous MongoDB connection lifecycle with timeouts."""

    client: AsyncMongoClient | None = None

    @classmethod
    def get_client(cls) -> AsyncMongoClient:
        """Obtain or initialize the shared PyMongo AsyncMongoClient."""
        if cls.client is None:
            settings = get_settings()
            cls.client = AsyncMongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=10000,
                maxPoolSize=50,
                minPoolSize=5,
            )
        return cls.client

    @classmethod
    def get_database(cls) -> AsyncDatabase:
        """Get application database handle from shared async client."""
        settings = get_settings()
        return cls.get_client()[settings.MONGODB_DB]

    @classmethod
    async def close_client(cls) -> None:
        """Close active client connection pool asynchronously."""
        if cls.client is not None:
            await cls.client.aclose()
            cls.client = None


async def get_db() -> AsyncDatabase:
    """FastAPI dependency yielding the shared asynchronous database handle."""
    return MongoDBManager.get_database()
