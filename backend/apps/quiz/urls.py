"""
URL routing for quiz app.
"""
from django.urls import path
from apps.quiz.views import QuizGenerateView, QuizSubmitView

urlpatterns = [
    path("generate/", QuizGenerateView.as_view(), name="quiz-generate"),
    path("submit/", QuizSubmitView.as_view(), name="quiz-submit"),
]
