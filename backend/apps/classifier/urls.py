"""
URL routing for classifier app.
"""
from django.urls import path
from apps.classifier.views import PredictTopicView, ClassifierStatusView

urlpatterns = [
    path("predict/", PredictTopicView.as_view(), name="classifier-predict"),
    path("status/", ClassifierStatusView.as_view(), name="classifier-status"),
]
