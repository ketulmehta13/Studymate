"""
Text cleaning utilities for document preprocessing.
Normalizes whitespace, line breaks, and removes obvious noise without
damaging mathematical formulas or technical notation.
"""
import re
from typing import List
from langchain_core.documents import Document

from core.logging_config import get_logger

logger = get_logger("rag.cleaner")

# Regex to safely clean hyphenated line breaks (e.g., "algo-\nrithm" -> "algorithm")
HYPHENATED_LINE_BREAK_REGEX = re.compile(r'([a-zA-Z]{2,})-\n([a-zA-Z]{2,})')

# Regex for common page header/footer noise (e.g. "Page 1 of 10", "--- 5 ---")
PAGE_HEADER_FOOTER_REGEX = re.compile(r'(?i)^\s*(page\s+\d+(\s+of\s+\d+)?|-+\s*\d+\s*-+)\s*$', re.MULTILINE)

# Regex for horizontal rule / decorative divider noise
DIVIDER_REGEX = re.compile(r'^[_\-*=]{4,}\s*$', re.MULTILINE)

# Regex to normalize multiple consecutive spaces and tabs (not newlines)
HORIZONTAL_WHITESPACE_REGEX = re.compile(r'[ \t]{2,}')

# Regex to normalize excessive blank lines (more than 2 consecutive newlines)
CONSECUTIVE_NEWLINES_REGEX = re.compile(r'\n{3,}')


def clean_text(text: str) -> str:
    """
    Cleans raw text extracted from documents.
    Preserves mathematical symbols, brackets, and code indentation.
    """
    if not text:
        return ""

    # Replace null bytes or carriage returns
    cleaned = text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")

    # Remove safe page headers/footers
    cleaned = PAGE_HEADER_FOOTER_REGEX.sub("", cleaned)

    # Remove decorative lines
    cleaned = DIVIDER_REGEX.sub("", cleaned)

    # Rejoin words broken across lines by hyphenation
    cleaned = HYPHENATED_LINE_BREAK_REGEX.sub(r'\1\2', cleaned)

    # Normalize horizontal whitespace on each line
    cleaned = HORIZONTAL_WHITESPACE_REGEX.sub(" ", cleaned)

    # Collapse excessive vertical blank lines to at most two
    cleaned = CONSECUTIVE_NEWLINES_REGEX.sub("\n\n", cleaned)

    return cleaned.strip()


def clean_documents(docs: List[Document]) -> List[Document]:
    """
    Cleans page_content for all documents in a list,
    filtering out documents that become completely empty after cleaning.
    """
    cleaned_docs = []
    for doc in docs:
        cleaned_content = clean_text(doc.page_content)
        if cleaned_content:
            doc.page_content = cleaned_content
            cleaned_docs.append(doc)
    logger.info(f"Cleaned {len(docs)} document pages -> {len(cleaned_docs)} non-empty pages retained.")
    return cleaned_docs
