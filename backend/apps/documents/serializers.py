"""
Serializers for documents app.
"""
from rest_framework import serializers
from django.conf import settings

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)

    def validate_file(self, value):
        filename = value.name.lower()
        import os
        ext = os.path.splitext(filename)[1]

        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(f"Unsupported file format '{ext}'. Only PDF and TXT files are accepted.")

        if value.size == 0:
            raise serializers.ValidationError("The uploaded file is empty.")

        max_bytes = getattr(settings, "MAX_UPLOAD_SIZE", 25 * 1024 * 1024)
        if value.size > max_bytes:
            mb = max_bytes // (1024 * 1024)
            raise serializers.ValidationError(f"File size exceeds the {mb}MB limit.")

        return value


class DocumentResponseSerializer(serializers.Serializer):
    document_id = serializers.CharField()
    user_id = serializers.CharField()
    filename = serializers.CharField()
    file_type = serializers.CharField()
    status = serializers.CharField()
    topic = serializers.CharField(required=False, allow_null=True)
    page_count = serializers.IntegerField(required=False, default=1)
    chunks_count = serializers.IntegerField(required=False, default=0)
    created_at = serializers.CharField()
    error_message = serializers.CharField(required=False, allow_null=True)
