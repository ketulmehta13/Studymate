"""
FAISS Vector Store persistence and query layer for StudyMate AI.
Ensures strict user-level isolation and disk persistence.
"""
import os
import threading
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from ai.rag.embeddings import get_embeddings
from core.exceptions import VectorStoreError
from core.logging_config import get_logger

logger = get_logger("rag.vectorstore")

_vectorstore_lock = threading.Lock()
_vectorstore_instance: Optional[FAISS] = None

INDEX_NAME = "index"


def get_vectorstore_path() -> Path:
    """Returns absolute path to vectorstore directory."""
    from django.conf import settings
    path = Path(settings.VECTORSTORE_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load_vectorstore_unlocked() -> Optional[FAISS]:
    """
    Loads persisted FAISS vectorstore from disk if it exists.
    MUST only be called while holding _vectorstore_lock.
    """
    global _vectorstore_instance
    vs_dir = get_vectorstore_path()
    index_file = vs_dir / f"{INDEX_NAME}.faiss"

    if not index_file.exists():
        logger.info("No existing FAISS index found on disk.")
        return None

    try:
        embeddings = get_embeddings()
        vs = FAISS.load_local(
            folder_path=str(vs_dir),
            embeddings=embeddings,
            index_name=INDEX_NAME,
            allow_dangerous_deserialization=True,
        )
        _vectorstore_instance = vs
        logger.info(f"Loaded FAISS vectorstore from {vs_dir}")
        return vs
    except Exception as e:
        logger.error(f"Error loading FAISS vectorstore: {e}")
        return None


def get_vectorstore() -> Optional[FAISS]:
    """Returns in-memory or loaded vectorstore instance (thread-safe)."""
    global _vectorstore_instance
    if _vectorstore_instance is None:
        with _vectorstore_lock:
            if _vectorstore_instance is None:
                _vectorstore_instance = _load_vectorstore_unlocked()
    return _vectorstore_instance


def save_vectorstore(vs: FAISS) -> None:
    """Saves FAISS vectorstore to disk."""
    vs_dir = get_vectorstore_path()
    try:
        vs.save_local(folder_path=str(vs_dir), index_name=INDEX_NAME)
        logger.info(f"FAISS index successfully saved to {vs_dir}")
    except Exception as e:
        logger.error(f"Failed to save FAISS vectorstore to {vs_dir}: {e}")
        raise VectorStoreError(f"Failed to persist vector index: {str(e)}")


def add_documents_to_vectorstore(documents: List[Document]) -> FAISS:
    """
    Adds new document chunks to the FAISS vectorstore and persists to disk.
    If no vectorstore exists yet, creates a new one.
    """
    global _vectorstore_instance
    if not documents:
        raise VectorStoreError("No documents provided to index.")

    with _vectorstore_lock:
        embeddings = get_embeddings()

        # Access instance directly (already holding the lock)
        vs = _vectorstore_instance
        if vs is None:
            vs = _load_vectorstore_unlocked()

        if vs is None:
            logger.info(f"Creating new FAISS vectorstore with {len(documents)} chunks...")
            vs = FAISS.from_documents(documents=documents, embedding=embeddings)
        else:
            logger.info(f"Adding {len(documents)} chunks to existing FAISS vectorstore...")
            vs.add_documents(documents=documents)

        save_vectorstore(vs)
        _vectorstore_instance = vs
        return vs


def similarity_search_user_isolated(
    query: str,
    user_id: str,
    k: int = 4,
    topic: Optional[str] = None
) -> List[Document]:
    """
    Performs similarity search with STRICT user_id isolation.
    Ensures no user can retrieve chunks belonging to another user.
    """
    vs = get_vectorstore()
    if vs is None:
        logger.info("Vectorstore is empty; returning 0 results.")
        return []

    # Fetch extra candidates to account for user filtering
    fetch_k = max(k * 4, 20)
    try:
        raw_results = vs.similarity_search(query, k=fetch_k)
    except Exception as e:
        logger.error(f"FAISS search failed: {e}")
        return []

    filtered_docs: List[Document] = []
    for doc in raw_results:
        doc_user_id = str(doc.metadata.get("user_id", ""))
        if doc_user_id == str(user_id):
            if topic and doc.metadata.get("topic", "").lower() != topic.lower():
                continue
            filtered_docs.append(doc)
            if len(filtered_docs) >= k:
                break

    logger.info(f"Retrieved {len(filtered_docs)}/{k} chunks for user {user_id}")
    return filtered_docs


def max_marginal_relevance_search_user_isolated(
    query: str,
    user_id: str,
    k: int = 4,
    fetch_k: int = 20,
    topic: Optional[str] = None
) -> List[Document]:
    """
    Performs MMR search with user_id isolation for enhanced diversity.
    """
    vs = get_vectorstore()
    if vs is None:
        return []

    try:
        raw_results = vs.max_marginal_relevance_search(
            query=query,
            k=fetch_k,
            fetch_k=fetch_k * 2
        )
    except Exception as e:
        logger.warning(f"MMR search fallback to similarity search: {e}")
        return similarity_search_user_isolated(query=query, user_id=user_id, k=k, topic=topic)

    filtered_docs: List[Document] = []
    for doc in raw_results:
        if str(doc.metadata.get("user_id", "")) == str(user_id):
            if topic and doc.metadata.get("topic", "").lower() != topic.lower():
                continue
            filtered_docs.append(doc)
            if len(filtered_docs) >= k:
                break

    return filtered_docs


def delete_documents_by_document_id(document_id: str, user_id: str) -> None:
    """
    Removes all chunks belonging to a document from the FAISS vectorstore.
    Reconstructs the index from remaining in-store documents to maintain consistency.
    """
    global _vectorstore_instance
    with _vectorstore_lock:
        # Access instance directly (already holding the lock)
        vs = _vectorstore_instance
        if vs is None:
            vs = _load_vectorstore_unlocked()
        if vs is None:
            return

        # Extract all remaining documents
        remaining_docs: List[Document] = []
        docstore = getattr(vs, "docstore", None)
        if docstore and hasattr(docstore, "_dict"):
            for doc in docstore._dict.values():
                if isinstance(doc, Document):
                    m = doc.metadata
                    if str(m.get("document_id")) == str(document_id) and str(m.get("user_id")) == str(user_id):
                        continue
                    remaining_docs.append(doc)

        embeddings = get_embeddings()
        vs_dir = get_vectorstore_path()

        if remaining_docs:
            new_vs = FAISS.from_documents(documents=remaining_docs, embedding=embeddings)
            save_vectorstore(new_vs)
            _vectorstore_instance = new_vs
            logger.info(f"Rebuilt FAISS index after deleting document {document_id}. {len(remaining_docs)} chunks remain.")
        else:
            # All documents deleted
            _vectorstore_instance = None
            index_file = vs_dir / f"{INDEX_NAME}.faiss"
            pkl_file = vs_dir / f"{INDEX_NAME}.pkl"
            if index_file.exists():
                index_file.unlink()
            if pkl_file.exists():
                pkl_file.unlink()
            logger.info(f"Cleared FAISS vectorstore as no documents remain.")
