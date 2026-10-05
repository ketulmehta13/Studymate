"""
URL configuration for StudyMate AI project.
"""
from django.urls import path, include
from core.views import HealthCheckView

urlpatterns = [
    path("api/health/", HealthCheckView.as_view(), name="health-check"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/documents/", include("apps.documents.urls")),
    path("api/chat/", include("apps.chat.urls")),
    path("api/quiz/", include("apps.quiz.urls")),
    path("api/study-plan/", include("apps.studyplan.urls")),
    path("api/study-plans/", include("apps.studyplan.urls")),
    path("api/classifier/", include("apps.classifier.urls")),
    path("api/progress/", include("apps.analytics.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
]
