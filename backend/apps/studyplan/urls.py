"""
URL routing for studyplan app.
"""
from django.urls import path
from apps.studyplan.views import (
    StudyPlanView,
    StudyPlanGenerateView,
    StudyPlanHistoryView,
    StudyPlanDetailView,
    StudyPlanToggleTaskView,
)

urlpatterns = [
    path("", StudyPlanView.as_view(), name="studyplan-latest"),
    path("generate/", StudyPlanGenerateView.as_view(), name="studyplan-generate"),
    path("history/", StudyPlanHistoryView.as_view(), name="studyplan-history"),
    path("<str:plan_id>/", StudyPlanDetailView.as_view(), name="studyplan-detail"),
    path("<str:plan_id>/toggle-task/", StudyPlanToggleTaskView.as_view(), name="studyplan-toggle-task"),
]
