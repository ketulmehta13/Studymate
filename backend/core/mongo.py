"""
MongoDB connection layer using PyMongo for StudyMate AI.
Provides singleton client, collection accessors, and error handling.
"""
import os
import threading
from typing import Any, Dict, List, Optional
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, PyMongoError

from core.logging_config import get_logger

logger = get_logger("mongo")

_client_instance: Optional[MongoClient] = None
_client_lock = threading.Lock()

# Collections used across StudyMate AI
COLLECTIONS = {
    "users": "users",
    "documents": "documents",
    "chunks": "chunks",
    "chat_history": "chat_history",
    "quizzes": "quizzes",
    "quiz_results": "quiz_results",
    "study_plans": "study_plans",
}


def get_mongo_uri() -> str:
    """Fetches MongoDB URI from environment with default."""
    return os.getenv("MONGODB_URI", "mongodb://localhost:27017")


def get_mongo_db_name() -> str:
    """Fetches MongoDB database name from environment with default."""
    return os.getenv("MONGODB_DATABASE", "studymate")


def get_mongo_client() -> MongoClient:
    """
    Returns a thread-safe singleton MongoClient instance.
    Reuses connection across requests to prevent socket exhaustion.
    """
    global _client_instance
    if _client_instance is None:
        with _client_lock:
            if _client_instance is None:
                uri = get_mongo_uri()
                logger.info(f"Connecting to MongoDB at {uri}...")
                try:
                    _client_instance = MongoClient(
                        uri,
                        serverSelectionTimeoutMS=2000,
                        connectTimeoutMS=2000,
                        maxPoolSize=50,
                        retryWrites=True,
                    )
                except Exception as e:
                    logger.error(f"Failed to initialize MongoClient: {e}")
                    raise
    return _client_instance


def get_db(db_name: Optional[str] = None) -> Database:
    """Returns database instance."""
    client = get_mongo_client()
    name = db_name or get_mongo_db_name()
    return client[name]


def get_collection(collection_name: str) -> Collection:
    """Returns specific collection from configured database."""
    if collection_name not in COLLECTIONS and collection_name not in COLLECTIONS.values():
        logger.warning(f"Accessing unregistered collection: {collection_name}")
    db = get_db()
    return db[collection_name]


def check_mongo_connection() -> bool:
    """
    Pings the MongoDB server to verify active connection.
    Returns True if connected, False otherwise.
    """
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        return True
    except (ConnectionFailure, PyMongoError, Exception) as e:
        logger.warning(f"MongoDB ping check failed: {e}")
        return False


def setup_indexes() -> None:
    """Creates recommended indexes for collections."""
    try:
        db = get_db()
        # Users collection
        db.users.create_index([("email", ASCENDING)], unique=True)
        db.users.create_index([("username", ASCENDING)], unique=True)
        
        # Documents collection
        db.documents.create_index([("user_id", ASCENDING), ("document_id", ASCENDING)])
        
        # Chunks collection
        db.chunks.create_index([("user_id", ASCENDING), ("document_id", ASCENDING)])
        db.chunks.create_index([("chunk_id", ASCENDING)])
        
        # Chat history
        db.chat_history.create_index([("user_id", ASCENDING), ("conversation_id", ASCENDING)])
        
        # Quizzes and Results
        db.quizzes.create_index([("user_id", ASCENDING), ("quiz_id", ASCENDING)])
        db.quiz_results.create_index([("user_id", ASCENDING), ("quiz_id", ASCENDING)])
        
        # Study plans
        db.study_plans.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)])
        logger.info("MongoDB indexes verified.")
    except Exception as e:
        logger.warning(f"Could not initialize MongoDB indexes (DB may be offline): {e}")


def close_mongo_connection() -> None:
    """Closes MongoDB connection if active."""
    global _client_instance
    with _client_lock:
        if _client_instance is not None:
            _client_instance.close()
            _client_instance = None
            logger.info("MongoDB client connection closed.")
