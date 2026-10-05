"""
LCEL RAG Chain implementation for StudyMate AI.
Combines retriever, citation formatting, prompt template, ChatOpenAI, and StrOutputParser.
"""
import os
from typing import Dict, Any, List, Optional
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from ai.rag.retriever import retrieve_documents
from ai.rag.prompts import RAG_PROMPT_TEMPLATE
from core.logging_config import get_logger

logger = get_logger("rag.chain")

DEFAULT_MODEL = "gpt-4o-mini"


def get_chat_llm(temperature: float = 0.2):
    """
    Returns ChatOpenAI instance configured via environment variables.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model_name = os.getenv("OPENAI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL

    if not api_key:
        logger.warning("OPENAI_API_KEY is not set. LLM calls will fail unless mocked.")
    
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        openai_api_key=api_key or "sk-dummy-key",
    )


def format_context_with_citations(docs: List[Document]) -> str:
    """Formats list of retrieved documents into annotated context string."""
    if not docs:
        return "No relevant study notes found in the database."

    formatted = []
    for doc in docs:
        filename = doc.metadata.get("filename", "unknown")
        page = doc.metadata.get("page", 1)
        formatted.append(f"[Document: {filename} | Page: {page}]\n{doc.page_content}")

    return "\n\n".join(formatted)


def extract_unique_sources(docs: List[Document]) -> List[Dict[str, Any]]:
    """Extracts unique source files and page numbers from retrieved docs."""
    sources: List[Dict[str, Any]] = []
    seen = set()

    for doc in docs:
        filename = str(doc.metadata.get("filename", "unknown"))
        page = int(doc.metadata.get("page", 1))
        key = (filename, page)
        if key not in seen:
            seen.add(key)
            sources.append({
                "filename": filename,
                "page": page,
            })

    return sources


def execute_rag_pipeline(
    question: str,
    user_id: str,
    k: int = 4,
    topic: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the complete RAG pipeline:
    1. Retrieve top-k chunks for user
    2. Format context with source citations
    3. Generate response via LLM
    4. Return structured response with answer and sources
    """
    logger.info(f"Executing RAG pipeline for user {user_id}: '{question}'")

    docs = retrieve_documents(query=question, user_id=user_id, k=k, topic=topic)
    sources = extract_unique_sources(docs)

    if not docs:
        return {
            "answer": "I could not find this information in your uploaded notes.",
            "source_type": "notes",
            "sources": [],
        }

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        # Offline / Test fallback when API key is not supplied
        logger.info("OPENAI_API_KEY not configured. Running offline RAG generator.")
        summary_snippets = [f"{d.metadata.get('filename')}: {d.page_content[:120]}..." for d in docs]
        return {
            "answer": f"Based on your notes: {docs[0].page_content[:300]} [Source: {docs[0].metadata.get('filename')}, Page {docs[0].metadata.get('page')}]",
            "source_type": "notes",
            "sources": sources,
        }

    formatted_context = format_context_with_citations(docs)
    llm = get_chat_llm(temperature=0.1)

    chain = (
        RAG_PROMPT_TEMPLATE
        | llm
        | StrOutputParser()
    )

    try:
        raw_answer = chain.invoke({
            "context": formatted_context,
            "question": question,
        })
    except Exception as e:
        logger.error(f"Error during RAG LLM execution: {e}")
        return {
            "answer": f"An error occurred while generating the answer: {str(e)}",
            "source_type": "notes",
            "sources": sources,
        }

    return {
        "answer": raw_answer.strip(),
        "source_type": "notes",
        "sources": sources,
    }
