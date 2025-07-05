from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from typing import Generator

# Synchronous MongoDB client
client = MongoClient(settings.MONGODB_URL)
database = client[settings.MONGODB_DB_NAME]

# Asynchronous MongoDB client
async_client = AsyncIOMotorClient(settings.MONGODB_URL)
async_database = async_client[settings.MONGODB_DB_NAME]

def get_db():
    """
    Database dependency for FastAPI
    """
    try:
        yield database
    finally:
        pass  # MongoDB connection is managed by the client

def get_async_db():
    """
    Async database dependency for FastAPI
    """
    return async_database