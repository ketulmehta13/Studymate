"""
Chat service layer orchestrating the LangGraph agent and chat history persistence.
"""
import uuid
import datetime
from typing import Dict, Any, Optional

from core.mongo import get_collection
from core.logging_config import get_logger
from ai.agent.graph import agent_app

logger = get_logger("chat.services")


def process_chat_message(message: str, user_id: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Processes a chat query through the LangGraph agent and records history in MongoDB.
    """
    conv_id = conversation_id.strip() if conversation_id and conversation_id.strip() else str(uuid.uuid4())
    logger.info(f"Processing chat message for user {user_id} (conversation: {conv_id}): '{message[:50]}'")

    # Initial state for the agent workflow
    initial_state = {
        "question": message.strip(),
        "user_id": str(user_id),
        "conversation_id": conv_id,
        "query_type": "Q&A",
        "retrieved_documents": [],
        "grade": "GOOD",
        "retry_count": 0,
        "rewritten_query": "",
        "web_results": [],
        "answer": "",
        "sources": [],
        "source_type": "notes",
        "self_check_result": "PASS",
        "self_check_retries": 0,
    }

    try:
        final_state = agent_app.invoke(initial_state)
        answer = final_state.get("answer", "I could not generate an answer at this time.")
        source_type = final_state.get("source_type", "notes")
        sources = final_state.get("sources", [])
    except Exception as e:
        logger.error(f"Error during agent graph invocation: {e}", exc_info=True)
        answer = "I encountered an issue processing your question. Please try asking again."
        source_type = "system"
        sources = []

    # Store in MongoDB chat_history
    history_col = get_collection("chat_history")
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record = {
        "user_id": str(user_id),
        "conversation_id": conv_id,
        "message": message,
        "answer": answer,
        "source_type": source_type,
        "sources": sources,
        "timestamp": timestamp,
    }
    history_col.insert_one(record)

    return {
        "answer": answer,
        "source_type": source_type,
        "sources": sources,
        "conversation_id": conv_id,
    }


def get_conversation_history(user_id: str, conversation_id: str):
    """Retrieves chat history for a specific conversation."""
    history_col = get_collection("chat_history")
    cursor = history_col.find({
        "user_id": str(user_id),
        "conversation_id": str(conversation_id)
    }).sort("timestamp", 1)

    turns = []
    for doc in cursor:
        doc.pop("_id", None)
        turns.append(doc)
    return turns
