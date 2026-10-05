"""
Tests for authentication (registration, login, JWT, profile).
"""
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

import pytest
from rest_framework.test import APIRequestFactory
from apps.accounts.views import RegisterView, LoginView, RefreshTokenView, MeView
from core.security import hash_password, verify_password, generate_tokens, decode_token, MongoUser
from core.mongo import get_collection


@pytest.fixture(autouse=True)
def clean_test_users():
    """Remove test user data before/after each test."""
    users_col = get_collection("users")
    users_col.delete_many({"username": {"$regex": "^testuser_auth"}})
    yield
    users_col.delete_many({"username": {"$regex": "^testuser_auth"}})


class TestPasswordHashing:
    def test_hash_and_verify_password(self):
        raw = "StrongP@ss123"
        hashed = hash_password(raw)
        assert hashed != raw
        assert verify_password(raw, hashed) is True

    def test_wrong_password_fails_verification(self):
        hashed = hash_password("correct_pass")
        assert verify_password("wrong_pass", hashed) is False


class TestJWTTokens:
    def test_generate_and_decode_tokens(self):
        tokens = generate_tokens("user123", "testuser", "test@test.com")
        assert "access" in tokens
        assert "refresh" in tokens

        payload = decode_token(tokens["access"], expected_type="access")
        assert payload["user_id"] == "user123"
        assert payload["username"] == "testuser"
        assert payload["token_type"] == "access"

    def test_refresh_token_decode(self):
        tokens = generate_tokens("user456", "refreshuser", "refresh@test.com")
        payload = decode_token(tokens["refresh"], expected_type="refresh")
        assert payload["token_type"] == "refresh"


class TestMongoUser:
    def test_mongo_user_wrapper(self):
        user = MongoUser({"_id": "abc123", "username": "testperson", "email": "tp@test.com"})
        assert user.id == "abc123"
        assert user.username == "testperson"
        assert user.is_authenticated is True
        d = user.to_dict()
        assert d["id"] == "abc123"


class TestRegisterAPI:
    def test_register_success(self):
        factory = APIRequestFactory()
        request = factory.post("/api/auth/register/", {
            "username": "testuser_auth_reg",
            "email": "testuser_auth_reg@example.com",
            "password": "TestPass123!"
        }, format="json")
        view = RegisterView.as_view()
        response = view(request)
        assert response.status_code == 201
        assert response.data["message"] == "User registered successfully"

    def test_register_duplicate_username(self):
        factory = APIRequestFactory()
        data = {
            "username": "testuser_auth_dup",
            "email": "testuser_auth_dup@example.com",
            "password": "TestPass123!"
        }
        request1 = factory.post("/api/auth/register/", data, format="json")
        RegisterView.as_view()(request1)

        data["email"] = "another@example.com"
        request2 = factory.post("/api/auth/register/", data, format="json")
        response2 = RegisterView.as_view()(request2)
        assert response2.status_code in (400, 409)


class TestLoginAPI:
    def test_login_success(self):
        factory = APIRequestFactory()
        # Register first
        reg_data = {
            "username": "testuser_auth_login",
            "email": "testuser_auth_login@example.com",
            "password": "SecurePass123"
        }
        RegisterView.as_view()(factory.post("/api/auth/register/", reg_data, format="json"))

        # Login
        login_data = {"username": "testuser_auth_login", "password": "SecurePass123"}
        request = factory.post("/api/auth/login/", login_data, format="json")
        response = LoginView.as_view()(request)
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["username"] == "testuser_auth_login"

    def test_login_wrong_password(self):
        factory = APIRequestFactory()
        reg_data = {
            "username": "testuser_auth_wrongpw",
            "email": "testuser_auth_wrongpw@example.com",
            "password": "CorrectPass"
        }
        RegisterView.as_view()(factory.post("/api/auth/register/", reg_data, format="json"))

        login_data = {"username": "testuser_auth_wrongpw", "password": "WrongPassword"}
        request = factory.post("/api/auth/login/", login_data, format="json")
        response = LoginView.as_view()(request)
        assert response.status_code in (400, 401)


class TestMeAPI:
    def test_me_authenticated(self):
        factory = APIRequestFactory()
        # Register & login
        reg_data = {
            "username": "testuser_auth_me",
            "email": "testuser_auth_me@example.com",
            "password": "MePass123"
        }
        RegisterView.as_view()(factory.post("/api/auth/register/", reg_data, format="json"))
        login_req = factory.post("/api/auth/login/", {"username": "testuser_auth_me", "password": "MePass123"}, format="json")
        login_resp = LoginView.as_view()(login_req)
        access_token = login_resp.data["access"]

        # Call /me/
        me_request = factory.get("/api/auth/me/", HTTP_AUTHORIZATION=f"Bearer {access_token}")
        me_response = MeView.as_view()(me_request)
        assert me_response.status_code == 200
        assert me_response.data["username"] == "testuser_auth_me"

    def test_me_unauthenticated(self):
        factory = APIRequestFactory()
        request = factory.get("/api/auth/me/")
        response = MeView.as_view()(request)
        assert response.status_code in (401, 403)
