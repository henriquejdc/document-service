import re
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from .utils import normalize_search_phrase


def build_text_query_from_phrase(phrase: str) -> dict:
    normalized_phrase = normalize_search_phrase(phrase)
    search = normalized_phrase

    if " " in normalized_phrase:
        search = f'"{normalized_phrase}"'

    return {"$text": {"$search": search}}


def build_regex_query(palavra: str) -> dict:
    regex = re.compile(re.escape(palavra), re.IGNORECASE)
    return {"$or": [{"titulo": regex}, {"conteudo": regex}, {"autor": regex}]}


async def create_document(
    collection: AsyncIOMotorCollection, doc: dict
) -> dict:
    result = await collection.insert_one(doc)
    created = await collection.find_one({"_id": result.inserted_id})
    return created


async def find_documents(
    collection: AsyncIOMotorCollection,
    query: dict,
    limit: int = 100,
    skip: int = 0,
) -> List[dict]:
    cursor = collection.find(query).skip(skip).limit(limit)
    return [document async for document in cursor]


async def search_with_geo(
    collection: AsyncIOMotorCollection,
    text_query: Optional[dict],
    latitude: float,
    longitude: float,
    limit: int = 100,
    skip: int = 0,
) -> List[dict]:
    near = {
        "type": "Point",
        "coordinates": [float(longitude), float(latitude)],
    }
    pipeline = []
    query = text_query if text_query is not None else {}
    pipeline.append(
        {
            "$geoNear": {
                "near": near,
                "distanceField": "distance_m",
                "spherical": True,
                "query": query,
                "limit": limit + skip,
            }
        }
    )

    if skip:
        pipeline.append({"$skip": skip})

    if limit:
        pipeline.append({"$limit": limit})

    cursor = collection.aggregate(pipeline)
    return [document async for document in cursor]
