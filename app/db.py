import os

from motor.motor_asyncio import AsyncIOMotorClient

_client: AsyncIOMotorClient = None  # type: ignore


def get_mongo_uri() -> str:  # pragma: no cover
    return os.getenv("MONGO_URI", "mongodb://localhost:27017")


def get_db_name() -> str:  # pragma: no cover
    return os.getenv("MONGO_DB", "document_service")


async def connect():  # pragma: no cover
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(get_mongo_uri())
    return _client


def client():  # pragma: no cover
    global _client
    return _client


def get_collection(name: str):  # pragma: no cover
    if _client is None:
        raise RuntimeError(
            "Mongo client is not initialized. Call connect() first."
        )
    return _client[get_db_name()][name]  # type: ignore
