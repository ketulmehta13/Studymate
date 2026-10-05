"""
URL routing for documents app.
"""
from django.urls import path
from apps.documents.views import (
    DocumentUploadView,
    DocumentListView,
    DocumentDetailView,
)

urlpatterns = [
    path("upload/", DocumentUploadView.as_view(), name="documents-upload"),
    path("", DocumentListView.as_view(), name="documents-list"),
    path("<str:document_id>/", DocumentDetailView.as_view(), name="documents-detail"),
]
