"""
LangGraph workflow nodes for StudyMate AI.
Implements:
- route_query_node
- retrieve_node
- grade_node
- rewrite_query_node
- web_search_fallback_node
- generate_node
- self_check_node
- quiz_node
- study_plan_node
- off_topic_node
"""
import os
from typing import Dict, Any, List
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

from ai.agent.state import AgentState
from ai.agent.router import route_query
from ai.agent.prompts import (
    GRADER_PROMPT_TEMPLATE,
    REWRITER_PROMPT_TEMPLATE,
    SELF_CHECK_PROMPT_TEMPLATE,
)
from ai.rag.retriever import retrieve_documents
from ai.rag.prompts import RAG_PROMPT_TEMPLATE, WEB_FALLBACK_PROMPT_TEMPLATE
from ai.rag.chain import (
    get_chat_llm,
    format_context_with_citations,
    extract_unique_sources,
)
from ai.tools.web_search import perform_web_search, is_web_search_available
from ai.quiz.generator import generate_quiz
from ai.studyplan.generator import generate_study_plan
from core.logging_config import get_logger

logger = get_logger("agent.nodes")


def route_query_node(state: AgentState) -> Dict[str, Any]:
    """Node: Categorizes user question into Q&A, QUIZ, STUDY_PLAN, or OFF_TOPIC."""
    question = state.get("question", "")
    q_type = route_query(question)
    logger.info(f"[Node: route_query] Routed question to: {q_type}")
    return {"query_type": q_type}


def retrieve_node(state: AgentState) -> Dict[str, Any]:
    """Node: Retrieves top-k chunks from user notes in FAISS."""
    query = state.get("rewritten_query") or state.get("question", "")
    user_id = state.get("user_id", "default_user")

    logger.info(f"[Node: retrieve] Retrieving for query: '{query}' (user_id={user_id})")
    docs: List[Document] = retrieve_documents(query=query, user_id=user_id, k=4)

    serialized_docs = [
        {
            "page_content": d.page_content,
            "metadata": d.metadata,
        }
        for d in docs
    ]
    return {"retrieved_documents": serialized_docs}


def grade_node(state: AgentState) -> Dict[str, Any]:
    """Node: Evaluates relevance of retrieved chunks to the question."""
    retrieved = state.get("retrieved_documents", [])
    question = state.get("question", "")

    if not retrieved:
        logger.info("[Node: grade] No documents retrieved. Grade: POOR")
        return {"grade": "POOR"}

    # Extract text content for grading
    context_text = "\n---\n".join([d.get("page_content", "") for d in retrieved])

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        # Offline heuristic grading: check for word overlap
        q_words = set(w.lower() for w in question.split() if len(w) > 3)
        ctx_lower = context_text.lower()
        matches = [w for w in q_words if w in ctx_lower]
        grade = "GOOD" if matches else "POOR"
        logger.info(f"[Node: grade] Offline heuristic grade: {grade} (matches: {matches})")
        return {"grade": grade}

    try:
        llm = get_chat_llm(temperature=0.0)
        chain = GRADER_PROMPT_TEMPLATE | llm | StrOutputParser()
        raw = chain.invoke({"context": context_text[:2000], "question": question}).strip().upper()
        grade = "GOOD" if "GOOD" in raw else "POOR"
        logger.info(f"[Node: grade] LLM grade result: {grade}")
        return {"grade": grade}
    except Exception as e:
        logger.warning(f"[Node: grade] LLM grading failed: {e}; defaulting to GOOD.")
        return {"grade": "GOOD"}


def rewrite_query_node(state: AgentState) -> Dict[str, Any]:
    """Node: Rewrites question to improve retrieval accuracy and increments retry count."""
    current_retries = state.get("retry_count", 0)
    question = state.get("question", "")

    new_retries = current_retries + 1
    logger.info(f"[Node: rewrite_query] Rewriting query. Retry count: {new_retries}/2")

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        rewritten = f"{question} core definitions and characteristics"
        return {"rewritten_query": rewritten, "retry_count": new_retries}

    try:
        llm = get_chat_llm(temperature=0.3)
        chain = REWRITER_PROMPT_TEMPLATE | llm | StrOutputParser()
        rewritten = chain.invoke({"question": question}).strip()
        logger.info(f"[Node: rewrite_query] Rewritten query: '{rewritten}'")
        return {"rewritten_query": rewritten, "retry_count": new_retries}
    except Exception as e:
        logger.warning(f"[Node: rewrite_query] Rewrite failed: {e}")
        return {"rewritten_query": question, "retry_count": new_retries}


def web_search_fallback_node(state: AgentState) -> Dict[str, Any]:
    """Node: Triggers web search fallback when notes retrieval is insufficient."""
    query = state.get("rewritten_query") or state.get("question", "")
    logger.info(f"[Node: web_search_fallback] Executing web search for: '{query}'")

    search_result = perform_web_search(query=query, max_results=3)
    results = search_result.get("results", [])

    sources = [
        {"title": r.get("title"), "url": r.get("url")}
        for r in results if r.get("url")
    ]

    return {
        "web_results": results,
        "source_type": "web",
        "sources": sources,
    }


def generate_node(state: AgentState) -> Dict[str, Any]:
    """Node: Generates answer from either retrieved notes or external web search."""
    source_type = state.get("source_type", "notes")
    question = state.get("question", "")

    if source_type == "web":
        web_results = state.get("web_results", [])
        if not web_results:
            return {
                "answer": "I could not find this information in your notes, and web search is currently unavailable or returned no results.",
                "source_type": "system",
                "sources": [],
            }

        context_blocks = [
            f"[Source: {r.get('title')}] ({r.get('url')})\n{r.get('snippet')}"
            for r in web_results
        ]
        context_str = "\n\n".join(context_blocks)

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            return {
                "answer": f"Note: This answer is based on external web search results because it was not found in your uploaded study notes.\n\nSummary: {web_results[0].get('snippet', '')}",
                "source_type": "web",
                "sources": state.get("sources", []),
            }

        try:
            llm = get_chat_llm(temperature=0.2)
            chain = WEB_FALLBACK_PROMPT_TEMPLATE | llm | StrOutputParser()
            ans = chain.invoke({"context": context_str, "question": question}).strip()
            return {"answer": ans, "source_type": "web"}
        except Exception as e:
            return {"answer": f"Web generation error: {e}", "source_type": "web"}

    # Generating from notes
    raw_docs = state.get("retrieved_documents", [])
    doc_objs = [
        Document(page_content=d.get("page_content", ""), metadata=d.get("metadata", {}))
        for d in raw_docs
    ]
    sources = extract_unique_sources(doc_objs)

    if not doc_objs:
        return {
            "answer": "I could not find this information in your uploaded notes.",
            "source_type": "notes",
            "sources": [],
        }

    context_str = format_context_with_citations(doc_objs)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        first_doc = doc_objs[0]
        fname = first_doc.metadata.get("filename", "notes.pdf")
        page = first_doc.metadata.get("page", 1)
        return {
            "answer": f"Based on your notes: {first_doc.page_content[:300]} [Source: {fname}, Page {page}]",
            "source_type": "notes",
            "sources": sources,
        }

    try:
        llm = get_chat_llm(temperature=0.1)
        chain = RAG_PROMPT_TEMPLATE | llm | StrOutputParser()
        answer = chain.invoke({"context": context_str, "question": question}).strip()
        return {
            "answer": answer,
            "source_type": "notes",
            "sources": sources,
        }
    except Exception as e:
        return {
            "answer": f"Error generating answer: {str(e)}",
            "source_type": "notes",
            "sources": sources,
        }


def self_check_node(state: AgentState) -> Dict[str, Any]:
    """Node: Verifies groundedness of the generated answer against context."""
    answer = state.get("answer", "")
    source_type = state.get("source_type", "notes")
    self_check_retries = state.get("self_check_retries", 0)

    # If already a negative answer or system message, pass directly
    if "could not find this information" in answer.lower():
        return {"self_check_result": "PASS"}

    # Build context string
    if source_type == "web":
        web_results = state.get("web_results", [])
        context_str = "\n".join([r.get("snippet", "") for r in web_results])
    else:
        raw_docs = state.get("retrieved_documents", [])
        context_str = "\n".join([d.get("page_content", "") for d in raw_docs])

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        # Offline passes
        return {"self_check_result": "PASS"}

    try:
        llm = get_chat_llm(temperature=0.0)
        chain = SELF_CHECK_PROMPT_TEMPLATE | llm | StrOutputParser()
        result = chain.invoke({"context": context_str[:2500], "answer": answer}).strip().upper()
        check_pass = "PASS" if "PASS" in result else "FAIL"

        if check_pass == "FAIL" and self_check_retries < 1:
            logger.warning("[Node: self_check] Answer failed groundedness check! Regenerating strictly...")
            # Re-generate once strictly
            return {
                "self_check_result": "FAIL",
                "self_check_retries": self_check_retries + 1,
            }

        return {"self_check_result": "PASS"}

    except Exception as e:
        logger.warning(f"[Node: self_check] Self-check failed: {e}; accepting answer.")
        return {"self_check_result": "PASS"}


def quiz_node(state: AgentState) -> Dict[str, Any]:
    """Node: Handles quiz generation intent."""
    question = state.get("question", "")
    user_id = state.get("user_id", "default_user")
    logger.info(f"[Node: quiz_node] Handling quiz request: '{question}'")

    quiz_data = generate_quiz(topic=question, difficulty="medium", number_of_questions=5, user_id=user_id)
    return {
        "answer": f"I've generated a 5-question practice quiz for you on '{quiz_data.get('topic')}'.",
        "source_type": "quiz",
        "sources": [{"quiz_id": quiz_data.get("quiz_id"), "questions_count": len(quiz_data.get("questions", []))}],
    }


def study_plan_node(state: AgentState) -> Dict[str, Any]:
    """Node: Handles study plan generation intent."""
    user_id = state.get("user_id", "default_user")
    logger.info(f"[Node: study_plan_node] Generating weekly plan for user {user_id}")

    plan_data = generate_study_plan(user_id=user_id)
    return {
        "answer": f"Here is your personalized weekly study plan: '{plan_data.get('title')}'. Focus areas: {', '.join(plan_data.get('weak_topics', []))}.",
        "source_type": "study_plan",
        "sources": [{"plan_id": plan_data.get("plan_id"), "priority": plan_data.get("priority")}],
    }


def off_topic_node(state: AgentState) -> Dict[str, Any]:
    """Node: Handles off-topic queries politely or delegates to web search."""
    question = state.get("question", "")
    logger.info(f"[Node: off_topic_node] Query classified as OFF_TOPIC: '{question}'")

    if is_web_search_available():
        return web_search_fallback_node(state)

    return {
        "answer": "I am StudyMate AI, your dedicated academic study assistant. I'm best equipped to explain concepts from your study notes, generate quizzes, or create structured study plans. How can I help with your studies today?",
        "source_type": "system",
        "sources": [],
    }
