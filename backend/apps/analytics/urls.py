"""
URL routing for analytics app.
"""
from django.urls import path
from apps.analytics.views import ProgressSummaryView

urlpatterns = [
    path("", ProgressSummaryView.as_view(), name="analytics-summary"),
]
