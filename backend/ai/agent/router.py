"""
Query router for StudyMate AI LangGraph agent.
Routes user inputs to Q&A, QUIZ, STUDY_PLAN, or OFF_TOPIC.
"""
import os
import re
from typing import Literal, Optional
from langchain_core.output_parsers import StrOutputParser

from ai.agent.prompts import ROUTER_PROMPT_TEMPLATE
from ai.rag.chain import get_chat_llm
from core.logging_config import get_logger

logger = get_logger("agent.router")

QueryType = Literal["Q&A", "QUIZ", "STUDY_PLAN", "OFF_TOPIC"]

QUIZ_KEYWORDS = [r"\bquiz\b", r"\bquestions?\b", r"\bmcq\b", r"\btest me\b", r"\bflashcards?\b", r"\bpractice problems?\b"]
STUDY_PLAN_KEYWORDS = [r"\bstudy plan\b", r"\bschedule\b", r"\btimetable\b", r"\broadmap\b", r"\bweekly plan\b", r"\bhow should i study\b"]
OFF_TOPIC_KEYWORDS = [r"\bweather\b", r"\bwho won\b", r"\bsports\b", r"\bcinema\b", r"\bjoke\b", r"\btell me a joke\b", r"\brecipe\b"]


def route_query_heuristics(text: str) -> Optional[QueryType]:
    """Fast regex-based intent classification."""
    lower = text.lower().strip()

    for pattern in QUIZ_KEYWORDS:
        if re.search(pattern, lower):
            return "QUIZ"

    for pattern in STUDY_PLAN_KEYWORDS:
        if re.search(pattern, lower):
            return "STUDY_PLAN"

    for pattern in OFF_TOPIC_KEYWORDS:
        if re.search(pattern, lower):
            return "OFF_TOPIC"

    return None


def route_query(question: str) -> QueryType:
    """
    Determines query type using fast heuristics first, falling back to LLM.
    """
    heuristic_match = route_query_heuristics(question)
    if heuristic_match:
        logger.info(f"Router matched '{question[:40]}...' to {heuristic_match} via heuristics.")
        return heuristic_match

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.info(f"OPENAI_API_KEY not set; defaulting '{question[:40]}...' to Q&A.")
        return "Q&A"

    try:
        llm = get_chat_llm(temperature=0.0)
        chain = ROUTER_PROMPT_TEMPLATE | llm | StrOutputParser()
        raw_output = chain.invoke({"question": question}).strip().upper()

        if "QUIZ" in raw_output:
            return "QUIZ"
        elif "STUDY" in raw_output or "PLAN" in raw_output:
            return "STUDY_PLAN"
        elif "OFF" in raw_output or "TOPIC" in raw_output:
            return "OFF_TOPIC"
        else:
            return "Q&A"

    except Exception as e:
        logger.warning(f"Router LLM execution failed: {e}; defaulting to Q&A.")
        return "Q&A"
