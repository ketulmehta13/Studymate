"""
Document ingestion pipeline and document management service.
Handles: upload -> load -> clean -> classify -> split -> embed -> FAISS -> MongoDB.
"""
import os
import uuid
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from django.conf import settings

from core.mongo import get_collection
from core.exceptions import DocumentError, DocumentNotFoundError, PermissionDeniedError
from core.logging_config import get_logger

from ai.rag.loader import load_document
from ai.rag.cleaner import clean_documents
from ai.classifier.predictor import predict_topic
from ai.rag.splitter import split_documents
from ai.rag.vectorstore import add_documents_to_vectorstore, delete_documents_by_document_id

logger = get_logger("documents.services")


def process_uploaded_document(uploaded_file, user_id: str) -> Dict[str, Any]:
    """
    Executes the complete document ingestion pipeline.
    """
    doc_id = str(uuid.uuid4())
    original_name = Path(uploaded_file.name).name
    ext = Path(original_name).suffix.lower()
    file_type = "pdf" if ext == ".pdf" else "txt"

    # 1. Save file locally in data/uploads/
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_filename = f"{doc_id}_{original_name}"
    saved_path = upload_dir / saved_filename

    with open(saved_path, "wb+") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    logger.info(f"Saved uploaded file to {saved_path}")

    # 2. Record initial document state in MongoDB
    docs_col = get_collection("documents")
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    doc_record = {
        "document_id": doc_id,
        "user_id": str(user_id),
        "filename": original_name,
        "file_type": file_type,
        "file_path": str(saved_path),
        "status": "processing",
        "topic": None,
        "page_count": 0,
        "chunks_count": 0,
        "created_at": now_iso,
        "error_message": None,
    }
    docs_col.insert_one(doc_record)

    try:
        # 3. Load Document
        raw_pages = load_document(
            file_path=str(saved_path),
            document_id=doc_id,
            user_id=user_id,
            original_filename=original_name
        )
        page_count = len(raw_pages)

        # 4. Clean Document Pages
        cleaned_pages = clean_documents(raw_pages)
        if not cleaned_pages:
            raise DocumentError("Document contains no valid text after cleaning.")

        # 5. Classify Academic Topic
        combined_preview = " ".join([p.page_content for p in cleaned_pages[:3]])
        classification = predict_topic(combined_preview)
        predicted_topic = classification.get("topic", "Other")
        logger.info(f"Document '{original_name}' classified as '{predicted_topic}' (confidence: {classification.get('confidence')})")

        # 6. Split into Chunks with Metadata
        chunks = split_documents(docs=cleaned_pages, topic=predicted_topic)

        # 7. Add Chunks to FAISS Vectorstore
        add_documents_to_vectorstore(chunks)

        # 8. Persist Chunk Metadata to MongoDB
        chunks_col = get_collection("chunks")
        chunk_docs = []
        for c in chunks:
            chunk_docs.append({
                "chunk_id": c.metadata["chunk_id"],
                "document_id": doc_id,
                "user_id": str(user_id),
                "filename": original_name,
                "page": c.metadata.get("page", 1),
                "topic": predicted_topic,
                "chunk_index": c.metadata.get("chunk_index", 0),
                "preview": c.page_content[:200],
                "created_at": now_iso,
            })
        if chunk_docs:
            chunks_col.insert_many(chunk_docs)

        # 9. Update Document status = "completed"
        docs_col.update_one(
            {"document_id": doc_id},
            {
                "$set": {
                    "status": "completed",
                    "topic": predicted_topic,
                    "page_count": page_count,
                    "chunks_count": len(chunks),
                }
            }
        )

        doc_record["status"] = "completed"
        doc_record["topic"] = predicted_topic
        doc_record["page_count"] = page_count
        doc_record["chunks_count"] = len(chunks)
        doc_record.pop("_id", None)
        doc_record.pop("file_path", None)

        logger.info(f"Document pipeline successfully completed for {doc_id}")
        return doc_record

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Document ingestion failed for {doc_id}: {error_msg}")
        docs_col.update_one(
            {"document_id": doc_id},
            {
                "$set": {
                    "status": "failed",
                    "error_message": "An error occurred while processing the document.",
                }
            }
        )
        raise DocumentError(f"Unable to process the uploaded document: {error_msg}")


def list_user_documents(user_id: str) -> List[Dict[str, Any]]:
    """Returns list of documents belonging to user."""
    docs_col = get_collection("documents")
    cursor = docs_col.find({"user_id": str(user_id)}).sort("created_at", -1)

    result = []
    for doc in cursor:
        doc.pop("_id", None)
        doc.pop("file_path", None)
        result.append(doc)
    return result


def get_document_by_id(document_id: str, user_id: str) -> Dict[str, Any]:
    """Retrieves single document metadata ensuring user ownership."""
    docs_col = get_collection("documents")
    doc = docs_col.find_one({"document_id": document_id})

    if not doc:
        raise DocumentNotFoundError("Document not found.")

    if str(doc.get("user_id")) != str(user_id):
        raise PermissionDeniedError("You do not have access to this document.")

    doc.pop("_id", None)
    doc.pop("file_path", None)
    return doc


def delete_user_document(document_id: str, user_id: str) -> None:
    """Deletes document record, local file, chunks, and FAISS vectors."""
    docs_col = get_collection("documents")
    doc = docs_col.find_one({"document_id": document_id})

    if not doc:
        raise DocumentNotFoundError("Document not found.")

    if str(doc.get("user_id")) != str(user_id):
        raise PermissionDeniedError("You do not have permission to delete this document.")

    # 1. Delete local file
    file_path = doc.get("file_path")
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"Removed file {file_path}")
        except Exception as e:
            logger.warning(f"Could not remove local file {file_path}: {e}")

    # 2. Remove from FAISS index
    try:
        delete_documents_by_document_id(document_id=document_id, user_id=user_id)
    except Exception as e:
        logger.warning(f"Failed to remove chunks from FAISS: {e}")

    # 3. Delete chunks from MongoDB
    chunks_col = get_collection("chunks")
    chunks_col.delete_many({"document_id": document_id, "user_id": str(user_id)})

    # 4. Delete document record from MongoDB
    docs_col.delete_one({"document_id": document_id})
    logger.info(f"Document {document_id} deleted successfully.")
