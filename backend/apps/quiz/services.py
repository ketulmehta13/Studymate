"""
Quiz service layer managing quiz generation, persistence, and evaluation.
"""
import datetime
from typing import Dict, Any, List, Optional

from core.mongo import get_collection
from core.exceptions import QuizError
from core.logging_config import get_logger
from ai.quiz.generator import generate_quiz

logger = get_logger("quiz.services")


def create_and_store_quiz(
    topic: str,
    difficulty: str,
    number_of_questions: int,
    user_id: str
) -> Dict[str, Any]:
    """
    Generates a structured quiz and stores it in MongoDB quizzes collection.
    """
    quiz_data = generate_quiz(
        topic=topic,
        difficulty=difficulty,
        number_of_questions=number_of_questions,
        user_id=user_id
    )

    quiz_id = quiz_data.get("quiz_id")
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    quizzes_col = get_collection("quizzes")
    quiz_doc = {
        "quiz_id": quiz_id,
        "user_id": str(user_id),
        "topic": quiz_data.get("topic", topic),
        "difficulty": quiz_data.get("difficulty", difficulty),
        "questions": quiz_data.get("questions", []),
        "created_at": now_iso,
    }
    quizzes_col.insert_one(quiz_doc)
    logger.info(f"Stored quiz {quiz_id} in MongoDB for user {user_id}")

    return {
        "quiz_id": quiz_id,
        "topic": quiz_data.get("topic"),
        "difficulty": quiz_data.get("difficulty"),
        "questions": quiz_data.get("questions"),
    }


def evaluate_quiz_submission(
    quiz_id: str,
    user_answers: Dict[str, str],
    user_id: str
) -> Dict[str, Any]:
    """
    Evaluates student quiz answers, calculates percentage and score,
    and records results in quiz_results collection for adaptive learning.
    """
    quizzes_col = get_collection("quizzes")
    quiz_doc = quizzes_col.find_one({"quiz_id": quiz_id})

    if not quiz_doc:
        raise QuizError("Quiz not found or has expired.", details={"quiz_id": quiz_id})

    questions = quiz_doc.get("questions", [])
    total_questions = len(questions)
    if total_questions == 0:
        raise QuizError("Quiz contains no questions.")

    score = 0
    detailed_results = []

    for idx, q in enumerate(questions):
        idx_str = str(idx)
        user_choice = user_answers.get(idx_str, "").strip()
        correct_answer = q.get("answer", "").strip()

        is_correct = user_choice.lower() == correct_answer.lower()
        if is_correct:
            score += 1

        detailed_results.append({
            "question_index": idx,
            "question": q.get("question"),
            "user_answer": user_choice,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": q.get("explanation"),
        })

    percentage = round((score / total_questions) * 100, 1)
    topic = quiz_doc.get("topic", "General")
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    result_doc = {
        "user_id": str(user_id),
        "quiz_id": quiz_id,
        "topic": topic,
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage,
        "answers": user_answers,
        "created_at": now_iso,
    }

    quiz_results_col = get_collection("quiz_results")
    quiz_results_col.insert_one(result_doc)
    logger.info(f"User {user_id} completed quiz {quiz_id}: {score}/{total_questions} ({percentage}%) on topic '{topic}'")

    return {
        "quiz_id": quiz_id,
        "topic": topic,
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage,
        "topic_performance": {
            topic: f"{percentage}%"
        },
        "detailed_results": detailed_results,
    }


def get_user_quiz_history(user_id: str) -> List[Dict[str, Any]]:
    """Retrieves all past quiz submissions and scores for a user."""
    results_col = get_collection("quiz_results")
    cursor = results_col.find({"user_id": str(user_id)}).sort("created_at", -1)

    history = []
    for doc in cursor:
        doc.pop("_id", None)
        history.append(doc)
    return history


def get_quiz_by_id(quiz_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves a quiz by ID."""
    quizzes_col = get_collection("quizzes")
    doc = quizzes_col.find_one({"quiz_id": quiz_id})
    if not doc:
        raise QuizError("Quiz not found.", details={"quiz_id": quiz_id})
    doc.pop("_id", None)
    return doc
