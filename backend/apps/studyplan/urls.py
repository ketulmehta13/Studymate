"""
URL routing for studyplan app.
"""
from django.urls import path
from apps.studyplan.views import StudyPlanView, StudyPlanGenerateView

urlpatterns = [
    path("", StudyPlanView.as_view(), name="studyplan-latest"),
    path("generate/", StudyPlanGenerateView.as_view(), name="studyplan-generate"),
]
