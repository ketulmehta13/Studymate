"""
Structured quiz generator service for StudyMate AI.
Uses Pydantic structured LLM output and retrieved study notes context.
"""
import os
import uuid
from typing import Dict, Any, Optional

from ai.quiz.schemas import Quiz, QuizQuestion
from ai.quiz.prompts import QUIZ_PROMPT_TEMPLATE
from ai.rag.retriever import retrieve_documents
from ai.rag.chain import get_chat_llm, format_context_with_citations
from core.exceptions import QuizError
from core.logging_config import get_logger

logger = get_logger("quiz.generator")


def _generate_fallback_quiz(topic: str, difficulty: str, number_of_questions: int) -> Quiz:
    """
    Provides a high-quality deterministic fallback quiz for offline/test environments
    when OPENAI_API_KEY is not configured.
    """
    sample_bank = [
        QuizQuestion(
            question=f"What is a primary objective when studying {topic}?",
            options=[
                f"Understanding core fundamental principles of {topic}",
                "Memorizing random unstructured numbers without context",
                "Deleting all training data before model optimization",
                "Avoiding mathematical formulas and conceptual analysis",
            ],
            answer=f"Understanding core fundamental principles of {topic}",
            difficulty=difficulty,
            explanation=f"Foundational understanding is the basis for mastery in {topic}.",
        ),
        QuizQuestion(
            question=f"Which method is commonly applied for evaluating models in {topic}?",
            options=[
                "Cross-validation and quantitative performance metrics",
                "Ignoring validation sets completely during training",
                "Relying solely on training error without test validation",
                "Guessing predictions randomly without metrics",
            ],
            answer="Cross-validation and quantitative performance metrics",
            difficulty=difficulty,
            explanation="Rigorous validation ensures the model generalizes well to unseen data.",
        ),
        QuizQuestion(
            question=f"Why is regularization important when training models in {topic}?",
            options=[
                "It helps prevent overfitting and improves generalization",
                "It guarantees 100% training accuracy in all scenarios",
                "It permanently removes all gradient calculations",
                "It replaces neural layers with random linear transforms",
            ],
            answer="It helps prevent overfitting and improves generalization",
            difficulty=difficulty,
            explanation="Regularization penalizes extreme weights to prevent overfitting.",
        ),
        QuizQuestion(
            question=f"What role does feature representation play in {topic}?",
            options=[
                "It converts raw inputs into meaningful vectors for processing",
                "It introduces deliberate noise to corrupt the model",
                "It slows down convergence without any analytical benefit",
                "It eliminates the need for any training algorithms",
            ],
            answer="It converts raw inputs into meaningful vectors for processing",
            difficulty=difficulty,
            explanation="Effective representations capture semantic properties of the domain.",
        ),
        QuizQuestion(
            question=f"In {topic}, what does hyperparameter tuning achieve?",
            options=[
                "Optimizing configuration settings to maximize model performance",
                "Hardcoding arbitrary values directly into the operating system",
                "Increasing computational latency without accuracy improvements",
                "Disabling validation loss monitoring during training",
            ],
            answer="Optimizing configuration settings to maximize model performance",
            difficulty=difficulty,
            explanation="Hyperparameter optimization finds the best settings for the architecture.",
        ),
    ]

    selected = sample_bank[:max(1, min(number_of_questions, len(sample_bank)))]
    return Quiz(topic=topic, difficulty=difficulty, questions=selected)


def generate_quiz(
    topic: str,
    difficulty: str = "medium",
    number_of_questions: int = 5,
    user_id: str = "default_user",
) -> Dict[str, Any]:
    """
    Generates a structured quiz on the requested topic using retrieved notes.
    """
    logger.info(f"Generating quiz for user {user_id} on topic '{topic}' (difficulty: {difficulty}, count: {number_of_questions})")

    # 1. Retrieve relevant notes chunks
    docs = retrieve_documents(query=topic, user_id=user_id, k=6, topic=topic)
    context_str = format_context_with_citations(docs) if docs else f"No uploaded notes found specifically for {topic}. Generate conceptual questions based on standard curriculum."

    # 2. Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.info("OPENAI_API_KEY not configured. Generating offline structured quiz.")
        quiz_obj = _generate_fallback_quiz(topic=topic, difficulty=difficulty, number_of_questions=number_of_questions)
        quiz_data = quiz_obj.model_dump()
        quiz_data["quiz_id"] = str(uuid.uuid4())
        return quiz_data

    # 3. Invoke LLM with Pydantic structured output
    try:
        llm = get_chat_llm(temperature=0.3)
        structured_llm = llm.with_structured_output(Quiz)

        prompt_messages = QUIZ_PROMPT_TEMPLATE.format_messages(
            topic=topic,
            difficulty=difficulty,
            number_of_questions=number_of_questions,
            context=context_str,
        )

        quiz_obj: Quiz = structured_llm.invoke(prompt_messages)
        quiz_data = quiz_obj.model_dump()
        quiz_data["quiz_id"] = str(uuid.uuid4())
        logger.info(f"Successfully generated structured quiz with {len(quiz_obj.questions)} questions.")
        return quiz_data

    except Exception as e:
        logger.error(f"Structured quiz generation failed: {e}. Falling back to starter quiz.")
        fallback = _generate_fallback_quiz(topic=topic, difficulty=difficulty, number_of_questions=number_of_questions)
        data = fallback.model_dump()
        data["quiz_id"] = str(uuid.uuid4())
        return data
