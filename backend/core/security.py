"""
Security and JWT Authentication utilities for StudyMate AI.
Supports password hashing via PBKDF2 and token generation/verification.
"""
import os
import datetime
from typing import Dict, Any, Optional, Tuple
import jwt
from bson import ObjectId
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from core.mongo import get_collection
from core.logging_config import get_logger

logger = get_logger("security")

DEFAULT_SECRET_KEY = "studymate-dev-jwt-secret-key-32chars-min-prod"


def get_jwt_secret() -> str:
    """Retrieves the JWT secret key from environment."""
    return os.getenv("JWT_SECRET_KEY", DEFAULT_SECRET_KEY)


def hash_password(raw_password: str) -> str:
    """Hashes password using Django's PBKDF2 hasher with salt."""
    return make_password(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    """Verifies plain password against hashed value."""
    return check_password(raw_password, hashed_password)


def generate_tokens(user_id: str, username: str, email: str) -> Dict[str, str]:
    """Generates both JWT access token and refresh token."""
    secret = get_jwt_secret()
    now = datetime.datetime.now(datetime.timezone.utc)
    
    access_payload = {
        "user_id": str(user_id),
        "username": username,
        "email": email,
        "token_type": "access",
        "iat": now,
        "exp": now + datetime.timedelta(hours=24),  # 24h access for smooth study sessions
    }

    refresh_payload = {
        "user_id": str(user_id),
        "username": username,
        "email": email,
        "token_type": "refresh",
        "iat": now,
        "exp": now + datetime.timedelta(days=7),  # 7-day refresh window
    }

    access_token = jwt.encode(access_payload, secret, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, secret, algorithm="HS256")

    return {
        "access": access_token,
        "refresh": refresh_token,
    }


def decode_token(token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token.
    Raises AuthenticationFailed on invalid/expired tokens.
    """
    secret = get_jwt_secret()
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token has expired.")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token.")

    if expected_type and payload.get("token_type") != expected_type:
        raise AuthenticationFailed(f"Invalid token type: expected {expected_type}.")

    return payload


class MongoUser:
    """
    User model wrapper for MongoDB documents to integrate with DRF.
    Ensures views can access request.user.id, request.user.username, etc.
    """
    def __init__(self, user_dict: Dict[str, Any]):
        self._doc = user_dict
        self.id = str(user_dict.get("_id") or user_dict.get("id") or user_dict.get("user_id"))
        self.user_id = self.id
        self.username = user_dict.get("username", "")
        self.email = user_dict.get("email", "")
        self.is_authenticated = True

    def __str__(self) -> str:
        return f"MongoUser({self.username}, {self.id})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }


class JWTAuthentication(BaseAuthentication):
    """
    DRF custom authentication class that validates Bearer JWT tokens
    and loads user metadata from MongoDB.
    """
    def authenticate(self, request) -> Optional[Tuple[MongoUser, str]]:
        auth_header = get_authorization_header(request).split()

        if not auth_header:
            return None

        if auth_header[0].lower() != b"bearer":
            return None

        if len(auth_header) == 1:
            raise AuthenticationFailed("Invalid Authorization header: Token missing.")
        elif len(auth_header) > 2:
            raise AuthenticationFailed("Invalid Authorization header: Token string contains spaces.")

        token = auth_header[1].decode("utf-8")
        payload = decode_token(token, expected_type="access")
        user_id = payload.get("user_id")

        if not user_id:
            raise AuthenticationFailed("Token contains no user identifier.")

        # Lookup user in MongoDB
        try:
            users_col = get_collection("users")
            query = {}
            if ObjectId.is_valid(user_id):
                query["$or"] = [{"_id": ObjectId(user_id)}, {"_id": user_id}, {"user_id": user_id}]
            else:
                query["$or"] = [{"_id": user_id}, {"user_id": user_id}]
            
            user_doc = users_col.find_one(query)
            if not user_doc:
                # If offline mock mode or fallback
                user_doc = {
                    "_id": user_id,
                    "username": payload.get("username", "User"),
                    "email": payload.get("email", ""),
                }
        except Exception as e:
            logger.warning(f"Could not load user from DB ({e}), falling back to token payload.")
            user_doc = {
                "_id": user_id,
                "username": payload.get("username", "User"),
                "email": payload.get("email", ""),
            }

        user = MongoUser(user_doc)
        return (user, token)
