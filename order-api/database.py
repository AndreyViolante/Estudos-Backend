import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "orders_db")

_client: AsyncIOMotorClient | None = None


async def get_database():
    return _client[DATABASE_NAME]


async def connect():
    global _client
    _client = AsyncIOMotorClient(MONGODB_URL)


async def close():
    global _client
    if _client:
        _client.close()
        _client = None
