"""
Chat views for StudyMate AI.
Handles user messages, LangGraph routing, and conversation history.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.chat.serializers import ChatMessageRequestSerializer, ChatMessageResponseSerializer
from apps.chat.services import process_chat_message, get_conversation_history


class ChatView(APIView):
    """
    POST /api/chat/
    Sends a question or prompt to the adaptive study assistant.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatMessageRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data["message"]
        conversation_id = serializer.validated_data.get("conversation_id")

        result = process_chat_message(
            message=message,
            user_id=request.user.id,
            conversation_id=conversation_id
        )

        return Response(result, status=status.HTTP_200_OK)


class ChatHistoryView(APIView):
    """
    GET /api/chat/<conversation_id>/
    Returns conversation history for a specific session.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        history = get_conversation_history(
            user_id=request.user.id,
            conversation_id=conversation_id
        )
        return Response(history, status=status.HTTP_200_OK)
