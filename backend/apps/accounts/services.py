"""
Authentication service layer interacting with MongoDB.
"""
import datetime
from bson import ObjectId
from typing import Dict, Any, Optional

from core.mongo import get_collection
from core.security import hash_password, verify_password, generate_tokens, decode_token
from core.exceptions import ValidationError, AuthenticationError
from core.logging_config import get_logger

logger = get_logger("accounts.services")


def register_user(username: str, email: str, raw_password: str) -> Dict[str, Any]:
    """
    Registers a new user in MongoDB with a hashed password.
    Raises ValidationError if user already exists.
    """
    users_col = get_collection("users")
    username_clean = username.strip().lower()
    email_clean = email.strip().lower()

    # Check for existing user
    existing_user = users_col.find_one({
        "$or": [
            {"username": username_clean},
            {"email": email_clean}
        ]
    })

    if existing_user:
        if existing_user.get("username") == username_clean:
            raise ValidationError("A user with this username already exists.")
        if existing_user.get("email") == email_clean:
            raise ValidationError("A user with this email already exists.")

    password_hash = hash_password(raw_password)
    user_doc = {
        "username": username_clean,
        "email": email_clean,
        "password": password_hash,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "is_active": True,
    }

    result = users_col.insert_one(user_doc)
    user_id = str(result.inserted_id)
    logger.info(f"User registered successfully: {username_clean} ({user_id})")

    return {
        "id": user_id,
        "username": username_clean,
        "email": email_clean,
    }


def authenticate_user(identifier: str, raw_password: str) -> Dict[str, Any]:
    """
    Authenticates user with username or email and password.
    Returns access & refresh tokens and user info.
    """
    users_col = get_collection("users")
    clean_id = identifier.strip().lower()

    user_doc = users_col.find_one({
        "$or": [
            {"username": clean_id},
            {"email": clean_id}
        ]
    })

    if not user_doc:
        raise AuthenticationError("Invalid username/email or password.")

    stored_hash = user_doc.get("password", "")
    if not verify_password(raw_password, stored_hash):
        raise AuthenticationError("Invalid username/email or password.")

    user_id = str(user_doc["_id"])
    username = user_doc.get("username", "")
    email = user_doc.get("email", "")

    tokens = generate_tokens(user_id=user_id, username=username, email=email)
    logger.info(f"User logged in: {username} ({user_id})")

    return {
        "access": tokens["access"],
        "refresh": tokens["refresh"],
        "user": {
            "id": user_id,
            "username": username,
            "email": email,
        }
    }


def refresh_access_token(refresh_token: str) -> str:
    """
    Validates refresh token and issues a new access token.
    """
    payload = decode_token(refresh_token, expected_type="refresh")
    user_id = payload.get("user_id")
    username = payload.get("username", "")
    email = payload.get("email", "")

    tokens = generate_tokens(user_id=user_id, username=username, email=email)
    return tokens["access"]


def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Fetches user profile by ID."""
    users_col = get_collection("users")
    query = {}
    if ObjectId.is_valid(user_id):
        query["$or"] = [{"_id": ObjectId(user_id)}, {"_id": user_id}, {"user_id": user_id}]
    else:
        query["$or"] = [{"_id": user_id}, {"user_id": user_id}]

    user_doc = users_col.find_one(query)
    if not user_doc:
        raise AuthenticationError("User not found.")

    return {
        "id": str(user_doc["_id"]),
        "username": user_doc.get("username", ""),
        "email": user_doc.get("email", ""),
        "created_at": user_doc.get("created_at"),
    }
