"""
Retriever service for StudyMate AI.
Provides unified interface for similarity and MMR search with user isolation.
"""
from typing import List, Optional
from langchain_core.documents import Document

from ai.rag.vectorstore import (
    similarity_search_user_isolated,
    max_marginal_relevance_search_user_isolated,
)
from core.logging_config import get_logger

logger = get_logger("rag.retriever")

DEFAULT_K = 4


def retrieve_documents(
    query: str,
    user_id: str,
    k: int = DEFAULT_K,
    search_type: str = "similarity",
    topic: Optional[str] = None
) -> List[Document]:
    """
    Retrieves top-k relevant document chunks for a specific user.
    
    Args:
        query: User question or search query.
        user_id: Authenticated user ID (strictly enforced).
        k: Number of chunks to retrieve (default: 4).
        search_type: 'similarity' or 'mmr'.
        topic: Optional academic topic filter.
        
    Returns:
        List of relevant LangChain Document chunks.
    """
    logger.info(f"Retrieving top {k} chunks for user {user_id} using {search_type} search (topic={topic}).")
    
    if search_type.lower() == "mmr":
        return max_marginal_relevance_search_user_isolated(
            query=query,
            user_id=user_id,
            k=k,
            topic=topic
        )
    
    return similarity_search_user_isolated(
        query=query,
        user_id=user_id,
        k=k,
        topic=topic
    )


class UserIsolatedRetriever:
    """
    LangChain compatible Runnable retriever wrapper scoped to a user.
    """
    def __init__(self, user_id: str, k: int = DEFAULT_K, search_type: str = "similarity", topic: Optional[str] = None):
        self.user_id = user_id
        self.k = k
        self.search_type = search_type
        self.topic = topic

    def invoke(self, query: str) -> List[Document]:
        return retrieve_documents(
            query=query,
            user_id=self.user_id,
            k=self.k,
            search_type=self.search_type,
            topic=self.topic
        )
