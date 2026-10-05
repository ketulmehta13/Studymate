"""
URL configuration for StudyMate AI project.
"""
from django.urls import path, include

urlpatterns = [
    path("api/auth/", include("apps.accounts.urls")),
    path("api/documents/", include("apps.documents.urls")),
    path("api/chat/", include("apps.chat.urls")),
    path("api/quiz/", include("apps.quiz.urls")),
    path("api/study-plan/", include("apps.studyplan.urls")),
]
