"""
Text splitting and chunking module for StudyMate AI.
Uses RecursiveCharacterTextSplitter and preserves metadata on each chunk.
"""
import uuid
from typing import List, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.logging_config import get_logger

logger = get_logger("rag.splitter")

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


def split_documents(
    docs: List[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    topic: Optional[str] = None
) -> List[Document]:
    """
    Splits documents into overlapping chunks and attaches unique chunk IDs
    and verified metadata to each chunk.
    
    Preserved metadata fields:
    - document_id
    - user_id
    - filename
    - page
    - topic
    - chunk_id
    - chunk_index
    """
    if not docs:
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
        is_separator_regex=False,
    )

    chunks: List[Document] = []
    chunk_index = 0

    for doc in docs:
        split_chunks = text_splitter.split_documents([doc])
        for chunk in split_chunks:
            # Preserve or inherit all metadata
            chunk_id = str(uuid.uuid4())
            meta = dict(chunk.metadata)
            meta["chunk_id"] = chunk_id
            meta["chunk_index"] = chunk_index
            if topic:
                meta["topic"] = topic
            elif "topic" not in meta:
                meta["topic"] = "General"

            # Ensure essential keys are string formatted
            meta["document_id"] = str(meta.get("document_id", ""))
            meta["user_id"] = str(meta.get("user_id", ""))
            meta["filename"] = str(meta.get("filename", meta.get("source", "unknown")))
            meta["page"] = int(meta.get("page", 1))

            chunk.metadata = meta
            chunks.append(chunk)
            chunk_index += 1

    logger.info(f"Split {len(docs)} documents into {len(chunks)} chunks (size={chunk_size}, overlap={chunk_overlap}).")
    return chunks
