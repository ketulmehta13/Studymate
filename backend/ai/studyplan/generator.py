"""
Adaptive study plan generator service for StudyMate AI.
Analyzes user quiz performance from MongoDB, detects weak topics, and generates a structured plan.
"""
import os
import uuid
import datetime
from typing import Dict, Any, List, Tuple, Optional

from ai.studyplan.schemas import StudyPlan, DailyTask, TopicAnalysis
from ai.studyplan.prompts import STUDYPLAN_PROMPT_TEMPLATE
from ai.rag.retriever import retrieve_documents
from ai.rag.chain import get_chat_llm, format_context_with_citations
from core.mongo import get_collection
from core.logging_config import get_logger

logger = get_logger("studyplan.generator")


def analyze_user_quiz_performance(user_id: str) -> Tuple[List[str], Dict[str, float], List[TopicAnalysis]]:
    """
    Queries MongoDB quiz_results for user, aggregates scores by topic,
    and returns (weak_topics_sorted, topic_scores, topic_analysis_objects).
    """
    quiz_results_col = get_collection("quiz_results")
    cursor = quiz_results_col.find({"user_id": str(user_id)})

    topic_totals: Dict[str, List[float]] = {}
    for doc in cursor:
        topic = doc.get("topic", "General")
        pct = float(doc.get("percentage", 0.0))
        if topic not in topic_totals:
            topic_totals[topic] = []
        topic_totals[topic].append(pct)

    if not topic_totals:
        # Default starter topics if user hasn't completed any quizzes yet
        topic_totals = {
            "Machine Learning": [70.0],
            "NLP": [50.0],
            "Mathematics": [60.0]
        }

    topic_scores: Dict[str, float] = {}
    analyses: List[TopicAnalysis] = []
    weak_topics: List[str] = []

    for topic, scores in topic_totals.items():
        avg_score = round(sum(scores) / len(scores), 1)
        topic_scores[topic] = avg_score

        if avg_score < 60.0:
            status = "Weak"
            rec = f"Prioritize fundamental concepts and practice questions for {topic}."
            weak_topics.append((topic, avg_score))
        elif avg_score < 75.0:
            status = "Moderate"
            rec = f"Review intermediate problem sets and refine weak areas in {topic}."
            weak_topics.append((topic, avg_score))
        else:
            status = "Strong"
            rec = f"Maintain mastery with brief periodic revision in {topic}."

        analyses.append(TopicAnalysis(
            topic=topic,
            accuracy_percentage=avg_score,
            status=status,
            recommendation=rec
        ))

    # Sort weak topics ascending by score (lowest score = highest priority)
    weak_topics.sort(key=lambda x: x[1])
    sorted_weak_topic_names = [t[0] for t in weak_topics]

    logger.info(f"Analyzed performance for user {user_id}: Weak topics = {sorted_weak_topic_names}")
    return sorted_weak_topic_names, topic_scores, analyses


def _generate_fallback_study_plan(
    weak_topics: List[str],
    topic_scores: Dict[str, float],
    analyses: List[TopicAnalysis]
) -> StudyPlan:
    """Fallback study plan generator for offline/testing environments."""
    primary_weak = weak_topics[0] if weak_topics else "Core Fundamentals"
    secondary_weak = weak_topics[1] if len(weak_topics) > 1 else "Advanced Concepts"

    tasks = [
        DailyTask(
            day="Monday",
            task=f"Deep dive into foundational principles of {primary_weak}",
            topic=primary_weak,
            estimated_time="1 hour",
            priority="High",
            resources_to_review=f"Lecture notes and introductory readings on {primary_weak}",
        ),
        DailyTask(
            day="Tuesday",
            task=f"Work through 5 practical exercises and definitions in {primary_weak}",
            topic=primary_weak,
            estimated_time="45 minutes",
            priority="High",
            resources_to_review=f"Practice problems in {primary_weak}",
        ),
        DailyTask(
            day="Wednesday",
            task=f"Review intermediate equations and theorems for {secondary_weak}",
            topic=secondary_weak,
            estimated_time="1 hour",
            priority="Medium",
            resources_to_review=f"Study guides covering {secondary_weak}",
        ),
        DailyTask(
            day="Thursday",
            task=f"Active recall flashcards and self-quiz on {primary_weak} and {secondary_weak}",
            topic=primary_weak,
            estimated_time="45 minutes",
            priority="High",
            resources_to_review="Previous quiz errors and summaries",
        ),
        DailyTask(
            day="Friday",
            task="Comprehensive synthesis and comparative analysis across all subjects",
            topic="Integration",
            estimated_time="1 hour",
            priority="Medium",
            resources_to_review="Course overview notes",
        ),
        DailyTask(
            day="Saturday",
            task="Timed practice quiz and mock exam questions",
            topic="Mock Exam",
            estimated_time="1.5 hours",
            priority="High",
            resources_to_review="Full-length quiz bank",
        ),
        DailyTask(
            day="Sunday",
            task="Weekly reflection, error log analysis, and schedule planning for next week",
            topic="Review",
            estimated_time="30 minutes",
            priority="Low",
            resources_to_review="Study journal",
        ),
    ]

    return StudyPlan(
        title=f"Adaptive Mastery Plan: Focus on {primary_weak}",
        week="Week 1",
        goals=[
            f"Boost comprehension of {primary_weak} past 75% accuracy",
            f"Consolidate problem-solving techniques in {secondary_weak}",
            "Complete end-of-week comprehensive diagnostic quiz",
        ],
        weak_topics=weak_topics,
        topic_analysis=analyses,
        daily_tasks=tasks,
        priority="High",
        reason=f"Prioritizing {primary_weak} first because quiz analytics show an average score of {topic_scores.get(primary_weak, 50)}%."
    )


def generate_study_plan(
    user_id: str,
    custom_topics: Optional[List[str]] = None,
    exam_date: Optional[str] = None,
    available_time: Optional[str] = None,
    priority: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generates an adaptive weekly study plan for a user based on their quiz performance or specified topics.
    """
    logger.info(f"Generating adaptive study plan for user {user_id}...")
    weak_topics, topic_scores, analyses = analyze_user_quiz_performance(user_id)

    if custom_topics and len(custom_topics) > 0:
        # User explicitly requested focus on these topics
        for ct in custom_topics:
            if ct not in weak_topics:
                weak_topics.insert(0, ct)
                if ct not in topic_scores:
                    topic_scores[ct] = 60.0
                    analyses.insert(0, TopicAnalysis(
                        topic=ct,
                        accuracy_percentage=60.0,
                        status="Target Subject",
                        recommendation=f"Requested study focus for upcoming exam ({exam_date or 'soon'})."
                    ))

    # Retrieve relevant notes for weak topics if available
    search_query = " ".join(weak_topics[:2]) if weak_topics else "Core concepts"
    docs = retrieve_documents(query=search_query, user_id=user_id, k=4)
    notes_context = format_context_with_citations(docs) if docs else "No uploaded notes found."

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.info("OPENAI_API_KEY not configured. Generating offline study plan.")
        plan_obj = _generate_fallback_study_plan(weak_topics, topic_scores, analyses)
        data = plan_obj.model_dump()
        if exam_date:
            data["exam_date"] = exam_date
        if available_time:
            data["available_time"] = available_time
        if priority:
            data["priority"] = priority
        data["plan_id"] = str(uuid.uuid4())
        data["user_id"] = str(user_id)
        data["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return data

    try:
        llm = get_chat_llm(temperature=0.2)
        structured_llm = llm.with_structured_output(StudyPlan)

        prompt_messages = STUDYPLAN_PROMPT_TEMPLATE.format_messages(
            weak_topics=", ".join(weak_topics) if weak_topics else "None specifically detected",
            topic_scores=str(topic_scores),
            notes_context=notes_context,
        )

        plan_obj: StudyPlan = structured_llm.invoke(prompt_messages)
        plan_data = plan_obj.model_dump()
        plan_data["plan_id"] = str(uuid.uuid4())
        plan_data["user_id"] = str(user_id)
        plan_data["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return plan_data

    except Exception as e:
        logger.error(f"Structured study plan generation failed: {e}. Falling back to default plan.")
        fallback = _generate_fallback_study_plan(weak_topics, topic_scores, analyses)
        data = fallback.model_dump()
        data["plan_id"] = str(uuid.uuid4())
        data["user_id"] = str(user_id)
        data["created_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return data
