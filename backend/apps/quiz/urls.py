"""
URL routing for quiz app.
"""
from django.urls import path
from apps.quiz.views import (
    QuizGenerateView,
    QuizSubmitView,
    QuizHistoryView,
    QuizDetailView,
)

urlpatterns = [
    path("generate/", QuizGenerateView.as_view(), name="quiz-generate"),
    path("submit/", QuizSubmitView.as_view(), name="quiz-submit"),
    path("history/", QuizHistoryView.as_view(), name="quiz-history"),
    path("<str:quiz_id>/", QuizDetailView.as_view(), name="quiz-detail"),
]
