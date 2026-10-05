"""
State schema for the StudyMate LangGraph agent workflow.
"""
from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    """
    Typed state representation flowing through LangGraph nodes.
    """
    question: str
    user_id: str
    conversation_id: str
    query_type: str                  # "Q&A", "QUIZ", "STUDY_PLAN", "OFF_TOPIC"
    retrieved_documents: List[Dict[str, Any]]
    grade: str                       # "GOOD", "POOR"
    retry_count: int                 # Max 2 retries
    rewritten_query: str
    web_results: List[Dict[str, Any]]
    answer: str
    sources: List[Dict[str, Any]]
    source_type: str                 # "notes", "web", "quiz", "study_plan", "system"
    self_check_result: str           # "PASS", "FAIL"
    self_check_retries: int          # Max 1 retry
