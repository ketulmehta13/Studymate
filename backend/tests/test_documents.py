"""
Tests for document upload, processing pipeline, and CRUD operations.
"""
import os
import sys
from pathlib import Path
from io import BytesIO

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.documents.views import DocumentUploadView, DocumentListView, DocumentDetailView
from apps.accounts.views import RegisterView, LoginView
from core.security import MongoUser
from core.mongo import get_collection


TEST_USER_ID = "test_doc_user_001"
TEST_USER = MongoUser({"_id": TEST_USER_ID, "username": "doctest", "email": "doctest@test.com"})


@pytest.fixture(autouse=True)
def clean_test_data():
    """Remove test document data before/after each test."""
    docs_col = get_collection("documents")
    chunks_col = get_collection("chunks")
    docs_col.delete_many({"user_id": TEST_USER_ID})
    chunks_col.delete_many({"user_id": TEST_USER_ID})
    yield
    docs_col.delete_many({"user_id": TEST_USER_ID})
    chunks_col.delete_many({"user_id": TEST_USER_ID})


class TestDocumentUpload:
    def test_upload_txt_file(self):
        factory = APIRequestFactory()
        content = b"Machine learning is the study of algorithms that improve through data. Supervised learning uses labeled examples."
        uploaded = SimpleUploadedFile("test_notes.txt", content, content_type="text/plain")

        request = factory.post("/api/documents/upload/", {"file": uploaded}, format="multipart")
        force_authenticate(request, user=TEST_USER)
        response = DocumentUploadView.as_view()(request)

        assert response.status_code == 201
        assert response.data["filename"] == "test_notes.txt"
        assert response.data["status"] == "completed"
        assert response.data["user_id"] == TEST_USER_ID
        assert response.data.get("topic") is not None

    def test_upload_empty_file_rejected(self):
        factory = APIRequestFactory()
        uploaded = SimpleUploadedFile("empty.txt", b"", content_type="text/plain")

        request = factory.post("/api/documents/upload/", {"file": uploaded}, format="multipart")
        force_authenticate(request, user=TEST_USER)
        response = DocumentUploadView.as_view()(request)
        assert response.status_code == 400

    def test_upload_unsupported_format_rejected(self):
        factory = APIRequestFactory()
        uploaded = SimpleUploadedFile("test.docx", b"data", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        request = factory.post("/api/documents/upload/", {"file": uploaded}, format="multipart")
        force_authenticate(request, user=TEST_USER)
        response = DocumentUploadView.as_view()(request)
        assert response.status_code == 400


class TestDocumentList:
    def test_list_user_documents(self):
        factory = APIRequestFactory()
        # Upload a doc first
        content = b"Some study content for listing test."
        uploaded = SimpleUploadedFile("list_test.txt", content, content_type="text/plain")
        upload_req = factory.post("/api/documents/upload/", {"file": uploaded}, format="multipart")
        force_authenticate(upload_req, user=TEST_USER)
        DocumentUploadView.as_view()(upload_req)

        # List
        list_req = factory.get("/api/documents/")
        force_authenticate(list_req, user=TEST_USER)
        response = DocumentListView.as_view()(list_req)
        assert response.status_code == 200
        assert isinstance(response.data, list)
        assert len(response.data) >= 1

    def test_documents_are_user_isolated(self):
        """Another user should not see the first user's documents."""
        factory = APIRequestFactory()
        other_user = MongoUser({"_id": "other_user_999", "username": "other", "email": "other@test.com"})
        list_req = factory.get("/api/documents/")
        force_authenticate(list_req, user=other_user)
        response = DocumentListView.as_view()(list_req)
        assert response.status_code == 200
        # Should not contain TEST_USER_ID docs
        for doc in response.data:
            assert doc.get("user_id") != TEST_USER_ID


class TestDocumentDetail:
    def test_get_and_delete_document(self):
        factory = APIRequestFactory()
        # Upload
        content = b"Content for detail retrieval and deletion test."
        uploaded = SimpleUploadedFile("detail_test.txt", content, content_type="text/plain")
        upload_req = factory.post("/api/documents/upload/", {"file": uploaded}, format="multipart")
        force_authenticate(upload_req, user=TEST_USER)
        upload_resp = DocumentUploadView.as_view()(upload_req)
        doc_id = upload_resp.data["document_id"]

        # Get detail
        get_req = factory.get(f"/api/documents/{doc_id}/")
        force_authenticate(get_req, user=TEST_USER)
        get_resp = DocumentDetailView.as_view()(get_req, document_id=doc_id)
        assert get_resp.status_code == 200
        assert get_resp.data["document_id"] == doc_id

        # Delete
        del_req = factory.delete(f"/api/documents/{doc_id}/")
        force_authenticate(del_req, user=TEST_USER)
        del_resp = DocumentDetailView.as_view()(del_req, document_id=doc_id)
        assert del_resp.status_code == 200
