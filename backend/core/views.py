"""
Core general-purpose views for StudyMate AI (e.g. Health checks).
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from core.mongo import check_mongo_connection
from ai.rag.vectorstore import get_vectorstore
from ai.classifier.predictor import CLF_PATH, VEC_PATH


class HealthCheckView(APIView):
    """
    GET /api/health/
    Health check endpoint returning system status and connected services.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        db_healthy = check_mongo_connection()
        classifier_ready = CLF_PATH.exists() and VEC_PATH.exists()

        overall_healthy = db_healthy

        return Response({
            "status": "healthy" if overall_healthy else "degraded",
            "services": {
                "mongodb": "connected" if db_healthy else "disconnected",
                "classifier_models": "ready" if classifier_ready else "not_loaded",
                "vectorstore": "ready",
            },
            "environment": "development",
            "version": "1.0.0",
        }, status=status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE)
