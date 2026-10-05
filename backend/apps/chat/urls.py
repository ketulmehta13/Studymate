"""
URL routing for chat app.
"""
from django.urls import path
from apps.chat.views import ChatView, ChatHistoryView

urlpatterns = [
    path("", ChatView.as_view(), name="chat-message"),
    path("<str:conversation_id>/", ChatHistoryView.as_view(), name="chat-history"),
]
