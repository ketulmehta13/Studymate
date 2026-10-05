"""
Classifier views exposing classical ML topic prediction to the API.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from ai.classifier.predictor import predict_topic, _ensure_models_loaded, CONFIDENCE_THRESHOLD, CLF_PATH, VEC_PATH


class PredictTopicView(APIView):
    """
    POST /api/classifier/predict/
    Body: {"text": "convolutional neural networks and backpropagation"}
    Returns predicted topic and confidence score.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        text = request.data.get("text", "")
        if not text or not str(text).strip():
            return Response(
                {"error": True, "message": "Text parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = predict_topic(str(text))
        return Response(
            {
                "success": True,
                "data": result,
                "text_snippet": str(text)[:100] + ("..." if len(str(text)) > 100 else "")
            },
            status=status.HTTP_200_OK
        )


class ClassifierStatusView(APIView):
    """
    GET /api/classifier/status/
    Returns classifier status, available classes, and model health.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            _ensure_models_loaded()
            from ai.classifier.predictor import _classifier, _vectorizer
            classes = list(_classifier.classes_) if _classifier else []
            vocab_size = len(_vectorizer.vocabulary_) if _vectorizer else 0
            model_exists = CLF_PATH.exists() and VEC_PATH.exists()

            return Response({
                "status": "ready" if model_exists else "untrained",
                "model_type": "LogisticRegression + TF-IDF",
                "classes": classes,
                "features_count": vocab_size,
                "confidence_threshold": CONFIDENCE_THRESHOLD,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
