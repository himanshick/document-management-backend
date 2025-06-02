from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_db() -> None:
    """
    Initialize the MongoDB client and database connection.
    Should be called once at application startup.
    """
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URL)
        _db = _client[settings.DB_NAME]


async def close_db() -> None:
    """
    Close the MongoDB client connection.
    Should be called on application shutdown.
    """
    global _client, _db
    if _client:
        _client.close()
    _client = None
    _db = None


async def get_db() -> AsyncIOMotorDatabase:
    """
    Get the current database instance.
    Raises RuntimeError if the DB is not connected.
    """
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_db first.")
    return _db


def get_client() -> AsyncIOMotorClient:
    """
    Get the current MongoDB client instance.
    Raises RuntimeError if the client is not connected.
    """
    if _client is None:
        raise RuntimeError("MongoDB client not connected. Call connect_db first.")
    return _client
