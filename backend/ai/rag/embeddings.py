"""
Embeddings factory for StudyMate AI.
Configures OpenAI embeddings with environment variables and provides
a deterministic fallback for local testing when API key is unset.
"""
import os
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from core.logging_config import get_logger

logger = get_logger("rag.embeddings")

DEFAULT_MODEL = "text-embedding-3-small"


class DeterministicMockEmbeddings(Embeddings):
    """
    Deterministic mock embedding generator for local testing/offline mode
    when OPENAI_API_KEY is not configured.
    Produces consistent 1536-dimensional float vectors using hash.
    """
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def _embed(self, text: str) -> list[float]:
        import hashlib
        # Generate deterministic vector based on MD5 and length
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16)
        vec = []
        for i in range(self.dimension):
            val = ((seed * (i + 1) * 9301 + 49297) % 233280) / 233280.0
            vec.append(round(val * 2.0 - 1.0, 6))
        # Normalize
        norm = sum(x * x for x in vec) ** 0.5 or 1.0
        return [x / norm for x in vec]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def get_embeddings() -> Embeddings:
    """
    Returns an Embeddings instance.
    Uses OpenAIEmbeddings if OPENAI_API_KEY is set.
    Otherwise logs a warning and uses DeterministicMockEmbeddings.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_EMBEDDING_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL

    if api_key:
        logger.info(f"Using OpenAIEmbeddings with model: {model}")
        return OpenAIEmbeddings(
            model=model,
            openai_api_key=api_key,
        )
    else:
        logger.warning(
            "OPENAI_API_KEY not found in environment. Using DeterministicMockEmbeddings "
            "for local/test execution. Configure OPENAI_API_KEY in .env for production."
        )
        return DeterministicMockEmbeddings()
