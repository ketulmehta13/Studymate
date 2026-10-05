"""
Serializers for accounts app.
"""
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50, min_length=3, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128, min_length=6, write_only=True, required=True)

    def validate_username(self, value: str) -> str:
        value = value.strip()
        if not value.isalnum() and not "_" in value:
            raise serializers.ValidationError("Username can only contain alphanumeric characters and underscores.")
        return value.lower()

    def validate_email(self, value: str) -> str:
        return value.strip().lower()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if not attrs.get("username") and not attrs.get("email"):
            raise serializers.ValidationError("Either username or email is required.")
        return attrs


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class UserSerializer(serializers.Serializer):
    id = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
