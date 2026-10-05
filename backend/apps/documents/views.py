"""
Document views for StudyMate AI.
Handles upload, listing, retrieval, and deletion of study materials.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from apps.documents.serializers import DocumentUploadSerializer, DocumentResponseSerializer
from apps.documents.services import (
    process_uploaded_document,
    list_user_documents,
    get_document_by_id,
    delete_user_document,
)


class DocumentUploadView(APIView):
    """
    POST /api/documents/upload/
    Uploads and processes a PDF or TXT file into the RAG vectorstore.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["file"]
        result = process_uploaded_document(
            uploaded_file=uploaded_file,
            user_id=request.user.id
        )

        return Response(result, status=status.HTTP_201_CREATED)


class DocumentListView(APIView):
    """
    GET /api/documents/
    Returns all uploaded documents belonging to the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        docs = list_user_documents(user_id=request.user.id)
        return Response(docs, status=status.HTTP_200_OK)


class DocumentDetailView(APIView):
    """
    GET /api/documents/<id>/
    DELETE /api/documents/<id>/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, document_id):
        doc = get_document_by_id(document_id=document_id, user_id=request.user.id)
        return Response(doc, status=status.HTTP_200_OK)

    def delete(self, request, document_id):
        delete_user_document(document_id=document_id, user_id=request.user.id)
        return Response({"message": "Document deleted successfully."}, status=status.HTTP_200_OK)
