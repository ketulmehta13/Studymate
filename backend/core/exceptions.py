"""
Centralized error handling and exceptions for StudyMate AI.
Standardizes error responses and prevents leakage of internal stack traces.
"""
from typing import Any, Dict, Optional
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException

from core.logging_config import get_logger

logger = get_logger("exceptions")


class StudyMateException(Exception):
    """Base exception for all domain-specific StudyMate errors."""
    def __init__(self, message: str, status_code: int = 400, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class AuthenticationError(StudyMateException):
    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED, details=details)


class TokenExpiredError(StudyMateException):
    def __init__(self, message: str = "Token has expired", details: Optional[Any] = None):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED, details=details)


class InvalidTokenError(StudyMateException):
    def __init__(self, message: str = "Invalid token provided", details: Optional[Any] = None):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED, details=details)


class PermissionDeniedError(StudyMateException):
    def __init__(self, message: str = "Permission denied", details: Optional[Any] = None):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN, details=details)


class ValidationError(StudyMateException):
    def __init__(self, message: str = "Invalid request data", details: Optional[Any] = None):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST, details=details)


class DocumentError(StudyMateException):
    def __init__(self, message: str = "Document processing error", status_code: int = 400, details: Optional[Any] = None):
        super().__init__(message=message, status_code=status_code, details=details)


class DocumentNotFoundError(StudyMateException):
    def __init__(self, message: str = "Document not found", details: Optional[Any] = None):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND, details=details)


class RAGError(StudyMateException):
    def __init__(self, message: str = "RAG retrieval/generation failed", details: Optional[Any] = None):
        super().__init__(message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=details)


class VectorStoreError(StudyMateException):
    def __init__(self, message: str = "Vector database error", details: Optional[Any] = None):
        super().__init__(message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=details)


class QuizError(StudyMateException):
    def __init__(self, message: str = "Quiz generation or evaluation failed", details: Optional[Any] = None):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST, details=details)


class StudyPlanError(StudyMateException):
    def __init__(self, message: str = "Study plan generation failed", details: Optional[Any] = None):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST, details=details)


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """
    DRF custom exception handler ensuring uniform error structure:
    {
        "error": true,
        "message": "Human readable message",
        "details": {...} (optional)
    }
    """
    view = context.get("view")
    view_name = view.__class__.__name__ if view else "UnknownView"
    logger.error(f"Exception in view {view_name}: {str(exc)}", exc_info=False)

    # Check for domain-specific StudyMateException
    if isinstance(exc, StudyMateException):
        response_data = {
            "error": True,
            "message": exc.message,
        }
        if exc.details:
            response_data["details"] = exc.details
        return Response(response_data, status=exc.status_code)

    # Let DRF handle built-in DRF exceptions (ValidationError, AuthenticationFailed, etc.)
    from rest_framework.views import exception_handler
    response = exception_handler(exc, context)

    if response is not None:
        message = "An error occurred."
        details = None

        if isinstance(response.data, dict):
            if "detail" in response.data:
                message = str(response.data["detail"])
            else:
                details = response.data
                message = "Validation error occurred."
        elif isinstance(response.data, list):
            message = str(response.data[0]) if response.data else "Validation error."
            details = response.data

        response_data = {
            "error": True,
            "message": message,
        }
        if details:
            response_data["details"] = details
        response.data = response_data
        return response

    # Catch-all unhandled exceptions: do NOT expose raw stack trace to user
    logger.critical(f"Unhandled server error: {exc}", exc_info=True)
    return Response(
        {
            "error": True,
            "message": "An internal server error occurred. Please try again later.",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
