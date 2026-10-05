"""
Authentication views for StudyMate AI.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from apps.accounts.serializers import (
    RegisterSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    UserSerializer,
)
from apps.accounts.services import (
    register_user,
    authenticate_user,
    refresh_access_token,
    get_user_profile,
)


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Registers a new user.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        register_user(
            username=serializer.validated_data["username"],
            email=serializer.validated_data["email"],
            raw_password=serializer.validated_data["password"],
        )

        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """
    POST /api/auth/login/
    Logs in a user and returns JWT tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        identifier = serializer.validated_data.get("username") or serializer.validated_data.get("email")
        password = serializer.validated_data["password"]

        result = authenticate_user(identifier=identifier, raw_password=password)
        return Response(result, status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    """
    POST /api/auth/refresh/
    Exchanges refresh token for a new access token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_access = refresh_access_token(serializer.validated_data["refresh"])
        return Response({"access": new_access}, status=status.HTTP_200_OK)


class MeView(APIView):
    """
    GET /api/auth/me/
    Returns authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_user_profile(request.user.id)
        return Response(profile, status=status.HTTP_200_OK)
