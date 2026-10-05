"""
LangGraph graph assembly and compilation for StudyMate AI.
Defines nodes, conditional edges, and state transitions.
"""
from typing import Literal
from langgraph.graph import StateGraph, START, END

from ai.agent.state import AgentState
from ai.agent.nodes import (
    route_query_node,
    retrieve_node,
    grade_node,
    rewrite_query_node,
    web_search_fallback_node,
    generate_node,
    self_check_node,
    quiz_node,
    study_plan_node,
    off_topic_node,
)
from core.logging_config import get_logger

logger = get_logger("agent.graph")


def route_decision(state: AgentState) -> Literal["retrieve", "quiz", "study_plan", "off_topic"]:
    """Decides initial routing path based on query classification."""
    q_type = state.get("query_type", "Q&A")
    if q_type == "QUIZ":
        return "quiz"
    elif q_type == "STUDY_PLAN":
        return "study_plan"
    elif q_type == "OFF_TOPIC":
        return "off_topic"
    return "retrieve"


def grade_decision(state: AgentState) -> Literal["generate", "rewrite", "web_search"]:
    """
    Decides whether to proceed to generation, rewrite query, or fallback to web search.
    Enforces maximum of 2 retrieval retries.
    """
    grade = state.get("grade", "GOOD")
    retries = state.get("retry_count", 0)

    if grade == "GOOD":
        logger.info("[Graph Edge] Grade is GOOD. Proceeding to generate.")
        return "generate"

    if retries < 2:
        logger.info(f"[Graph Edge] Grade is POOR (retry {retries}/2). Proceeding to query rewrite.")
        return "rewrite"

    logger.info(f"[Graph Edge] Grade is POOR and max retries ({retries}) reached. Falling back to web search.")
    return "web_search"


def self_check_decision(state: AgentState) -> Literal["generate", "end"]:
    """
    Decides whether answer passes groundedness check or needs one strict regeneration.
    """
    check_result = state.get("self_check_result", "PASS")
    retries = state.get("self_check_retries", 0)

    if check_result == "FAIL" and retries < 1:
        logger.warning("[Graph Edge] Groundedness check failed. Regenerating answer once.")
        return "generate"

    return "end"


def build_agent_graph():
    """Assembles and compiles the StudyMate agentic LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # 1. Add Nodes
    workflow.add_node("route_query", route_query_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade", grade_node)
    workflow.add_node("rewrite_query", rewrite_query_node)
    workflow.add_node("web_search", web_search_fallback_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("self_check", self_check_node)
    workflow.add_node("quiz", quiz_node)
    workflow.add_node("study_plan", study_plan_node)
    workflow.add_node("off_topic", off_topic_node)

    # 2. Add Edges
    workflow.add_edge(START, "route_query")

    # Routing conditional edges
    workflow.add_conditional_edges(
        "route_query",
        route_decision,
        {
            "retrieve": "retrieve",
            "quiz": "quiz",
            "study_plan": "study_plan",
            "off_topic": "off_topic",
        }
    )

    # Retrieval flows to grading
    workflow.add_edge("retrieve", "grade")

    # Grade conditional edges
    workflow.add_conditional_edges(
        "grade",
        grade_decision,
        {
            "generate": "generate",
            "rewrite": "rewrite_query",
            "web_search": "web_search",
        }
    )

    # Rewrite flows back to retrieve
    workflow.add_edge("rewrite_query", "retrieve")

    # Web search flows to generate
    workflow.add_edge("web_search", "generate")

    # Generate flows to self_check
    workflow.add_edge("generate", "self_check")

    # Self check conditional edge (max 1 regen)
    workflow.add_conditional_edges(
        "self_check",
        self_check_decision,
        {
            "generate": "generate",
            "end": END,
        }
    )

    # Terminal nodes
    workflow.add_edge("quiz", END)
    workflow.add_edge("study_plan", END)
    workflow.add_edge("off_topic", END)

    compiled_graph = workflow.compile()
    logger.info("Compiled StudyMate LangGraph agent workflow successfully.")
    return compiled_graph


# Pre-compiled agent graph singleton
agent_app = build_agent_graph()
