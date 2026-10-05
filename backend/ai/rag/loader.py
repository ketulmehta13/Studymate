"""
Document loader supporting PDF and TXT files.
Extracts content and attaches metadata (document_id, user_id, filename, page).
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from core.exceptions import DocumentError
from core.logging_config import get_logger

logger = get_logger("rag.loader")


def load_document(
    file_path: str,
    document_id: str,
    user_id: str,
    original_filename: Optional[str] = None
) -> List[Document]:
    """
    Loads a PDF or TXT file and attaches standard metadata.
    
    Args:
        file_path: Absolute path to the file.
        document_id: Unique identifier for the document.
        user_id: Identifier of the user owning the document.
        original_filename: The original name of the uploaded file.
    
    Returns:
        List of Document objects with metadata:
            {
                "document_id": "...",
                "user_id": "...",
                "source": "filename.pdf",
                "filename": "filename.pdf",
                "page": int
            }
    """
    path_obj = Path(file_path)
    if not path_obj.exists():
        raise DocumentError(f"File not found: {file_path}", status_code=404)

    filename = original_filename or path_obj.name
    ext = path_obj.suffix.lower()

    logger.info(f"Loading document '{filename}' ({ext}) for user {user_id}")

    docs: List[Document] = []

    if ext == ".pdf":
        try:
            loader = PyPDFLoader(str(path_obj))
            raw_docs = loader.load()
        except Exception as e:
            logger.error(f"Failed to read PDF file '{filename}': {e}")
            raise DocumentError(f"Failed to read PDF document: {str(e)}")

        for doc in raw_docs:
            # PyPDFLoader pages are 0-indexed; convert to 1-indexed for human readability
            raw_page = doc.metadata.get("page", 0)
            page_num = raw_page + 1 if isinstance(raw_page, int) else 1

            doc.metadata["document_id"] = document_id
            doc.metadata["user_id"] = str(user_id)
            doc.metadata["filename"] = filename
            doc.metadata["source"] = filename
            doc.metadata["page"] = page_num
            docs.append(doc)

    elif ext in (".txt", ".text", ".md"):
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        content = None
        for enc in encodings:
            try:
                with open(path_obj, "r", encoding=enc) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, Exception):
                continue

        if content is None:
            raise DocumentError(f"Could not decode text file '{filename}' with supported encodings.")

        doc = Document(
            page_content=content,
            metadata={
                "document_id": document_id,
                "user_id": str(user_id),
                "filename": filename,
                "source": filename,
                "page": 1,
            }
        )
        docs.append(doc)

    else:
        raise DocumentError(f"Unsupported file type '{ext}'. Only PDF and TXT are supported.")

    if not docs or all(len(d.page_content.strip()) == 0 for d in docs):
        raise DocumentError("Document appears to be empty or contains no extractable text.")

    logger.info(f"Successfully loaded {len(docs)} pages/sections from '{filename}'")
    return docs
