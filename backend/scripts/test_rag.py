"""
Standalone RAG testing script for StudyMate AI.
Tests document indexing and RAG question-answering independently from Django.
Usage:
    python scripts/test_rag.py
"""
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Setup Django settings environment so all components can load
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from langchain_core.documents import Document
from ai.rag.vectorstore import add_documents_to_vectorstore
from ai.rag.chain import execute_rag_pipeline

SEPARATOR = "=" * 60


def run_rag_test():
    print(SEPARATOR)
    print("      STUDYMATE AI — STANDALONE RAG VERIFICATION SCRIPT")
    print(SEPARATOR)

    test_user_id = "test_student_user"

    # Index sample study notes for verification
    sample_notes = [
        Document(
            page_content="Machine learning is a field of artificial intelligence focused on building algorithms that learn from data and improve their performance over time without being explicitly programmed.",
            metadata={
                "document_id": "test_doc_001",
                "user_id": test_user_id,
                "filename": "ml_foundations.pdf",
                "page": 1,
                "topic": "Machine Learning",
                "chunk_id": "test_chunk_001",
            }
        ),
        Document(
            page_content="Supervised learning uses labeled training datasets to train models for classification and regression tasks. Common algorithms include linear regression, logistic regression, and decision trees.",
            metadata={
                "document_id": "test_doc_001",
                "user_id": test_user_id,
                "filename": "ml_foundations.pdf",
                "page": 2,
                "topic": "Machine Learning",
                "chunk_id": "test_chunk_002",
            }
        ),
        Document(
            page_content="Overfitting occurs when a model learns noise and details from the training data to the extent that it negatively impacts the model's ability to generalize to new, unseen data. Techniques like dropout, regularization, and cross-validation help mitigate overfitting.",
            metadata={
                "document_id": "test_doc_001",
                "user_id": test_user_id,
                "filename": "ml_foundations.pdf",
                "page": 5,
                "topic": "Machine Learning",
                "chunk_id": "test_chunk_003",
            }
        ),
    ]

    print("\n[Step 1] Indexing test document chunks into FAISS vectorstore...")
    add_documents_to_vectorstore(sample_notes)
    print(" -> Indexing completed successfully.\n")

    test_cases = [
        "What is machine learning?",
        "What is overfitting and how do you prevent it?",
        "What is the average rainfall in the Amazon rainforest in July?",
    ]

    for idx, q in enumerate(test_cases, 1):
        print(f"\n--- Test Case #{idx} ---")
        result = execute_rag_pipeline(question=q, user_id=test_user_id, k=3)

        print(f"QUESTION:    {q}")
        print(f"ANSWER:      {result.get('answer')}")
        print(f"SOURCE TYPE: {result.get('source_type')}")
        
        sources = result.get("sources", [])
        if sources:
            for s in sources:
                print(f"SOURCE:      {s.get('filename')}")
                print(f"PAGE:        {s.get('page')}")
        else:
            print("SOURCE:      None (Information absent from notes)")
            print("PAGE:        N/A")
        print("-" * 40)

    print(f"\n{SEPARATOR}")
    print("      ALL STANDALONE RAG TESTS COMPLETED SUCCESSFULLY")
    print(f"{SEPARATOR}\n")


if __name__ == "__main__":
    run_rag_test()
