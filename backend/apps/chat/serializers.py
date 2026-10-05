"""
Serializers for chat app.
"""
from rest_framework import serializers


class ChatMessageRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True, min_length=1)
    conversation_id = serializers.CharField(required=False, allow_blank=True, default=None)

    def validate_message(self, value):
        val = value.strip()
        if not val:
            raise serializers.ValidationError("Message cannot be blank.")
        return val


class ChatSourceSerializer(serializers.Serializer):
    filename = serializers.CharField(required=False)
    page = serializers.IntegerField(required=False)
    title = serializers.CharField(required=False)
    url = serializers.CharField(required=False)


class ChatMessageResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    source_type = serializers.CharField()
    sources = serializers.ListField(child=serializers.DictField())
    conversation_id = serializers.CharField()
