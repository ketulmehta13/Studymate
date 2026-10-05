"""
Web search tool using Tavily API for external fallback queries.
Safely handles missing API keys without crashing the system.
"""
import os
from typing import Dict, Any, List, Optional
from core.logging_config import get_logger

logger = get_logger("tools.web_search")


def is_web_search_available() -> bool:
    """Checks if TAVILY_API_KEY is configured in the environment."""
    key = os.getenv("TAVILY_API_KEY", "").strip()
    return bool(key)


def perform_web_search(query: str, max_results: int = 4) -> Dict[str, Any]:
    """
    Executes a web search query via Tavily Search.
    
    Returns:
        {
            "available": True/False,
            "query": query,
            "results": [
                {"title": "...", "url": "...", "snippet": "..."}
            ],
            "error": Optional error message if search failed or key missing
        }
    """
    api_key = os.getenv("TAVILY_API_KEY", "").strip()

    if not api_key:
        logger.warning("Web search requested but TAVILY_API_KEY is not configured.")
        return {
            "available": False,
            "query": query,
            "results": [],
            "error": "Web search fallback is not configured. Set TAVILY_API_KEY in .env to enable web search.",
        }

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
        )

        raw_results = response.get("results", [])
        cleaned_results = []
        for r in raw_results:
            cleaned_results.append({
                "title": r.get("title", "Web Result"),
                "url": r.get("url", ""),
                "snippet": r.get("content", ""),
            })

        logger.info(f"Web search retrieved {len(cleaned_results)} results for query: '{query}'")
        return {
            "available": True,
            "query": query,
            "results": cleaned_results,
            "error": None,
        }
    except Exception as e:
        logger.error(f"Web search execution error: {e}")
        return {
            "available": False,
            "query": query,
            "results": [],
            "error": f"Web search failed: {str(e)}",
        }
