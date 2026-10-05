"""
Study plan service layer managing adaptive plan generation and retrieval.
"""
from typing import Dict, Any, Optional

from core.mongo import get_collection
from core.exceptions import StudyPlanError
from core.logging_config import get_logger
from ai.studyplan.generator import generate_study_plan

logger = get_logger("studyplan.services")


def create_and_store_study_plan(
    user_id: str,
    custom_topics: Optional[list] = None,
    exam_date: Optional[str] = None,
    available_time: Optional[str] = None,
    priority: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generates a new adaptive weekly study plan and saves it in MongoDB.
    """
    plan_data = generate_study_plan(
        user_id=user_id,
        custom_topics=custom_topics,
        exam_date=exam_date,
        available_time=available_time,
        priority=priority,
    )
    plan_id = plan_data.get("plan_id")

    study_plans_col = get_collection("study_plans")
    doc = dict(plan_data)
    doc["user_id"] = str(user_id)
    doc["completed_tasks"] = []
    study_plans_col.insert_one(doc)

    logger.info(f"Generated and stored study plan {plan_id} for user {user_id}")
    plan_data.pop("_id", None)
    plan_data["completed_tasks"] = []
    return plan_data


def get_latest_study_plan(user_id: str) -> Dict[str, Any]:
    """
    Retrieves the most recent study plan for the user,
    or generates one if none exists.
    """
    study_plans_col = get_collection("study_plans")
    doc = study_plans_col.find_one(
        {"user_id": str(user_id)},
        sort=[("created_at", -1)]
    )

    if doc:
        doc.pop("_id", None)
        return doc

    # If no study plan exists yet, generate one
    logger.info(f"No existing study plan for user {user_id}. Generating initial plan...")
    return create_and_store_study_plan(user_id=user_id)


def list_user_study_plans(user_id: str) -> list:
    """Lists all study plans for user."""
    study_plans_col = get_collection("study_plans")
    cursor = study_plans_col.find({"user_id": str(user_id)}).sort("created_at", -1)
    plans = []
    for doc in cursor:
        doc.pop("_id", None)
        plans.append(doc)
    return plans


def get_study_plan_by_id(plan_id: str, user_id: str) -> Dict[str, Any]:
    """Retrieves specific study plan by ID ensuring user isolation."""
    study_plans_col = get_collection("study_plans")
    doc = study_plans_col.find_one({"plan_id": plan_id, "user_id": str(user_id)})
    if not doc:
        raise StudyPlanError("Study plan not found.", details={"plan_id": plan_id})
    doc.pop("_id", None)
    return doc


def delete_study_plan(plan_id: str, user_id: str) -> None:
    """Deletes a study plan by ID ensuring user isolation."""
    study_plans_col = get_collection("study_plans")
    res = study_plans_col.delete_one({"plan_id": plan_id, "user_id": str(user_id)})
    if res.deleted_count == 0:
        raise StudyPlanError("Study plan not found or already deleted.", details={"plan_id": plan_id})


def toggle_study_plan_task(plan_id: str, task_index: int, user_id: str) -> Dict[str, Any]:
    """Toggles completion state of a task in the study plan."""
    study_plans_col = get_collection("study_plans")
    plan = study_plans_col.find_one({"plan_id": plan_id, "user_id": str(user_id)})
    if not plan:
        raise StudyPlanError("Study plan not found.")

    completed_tasks = plan.get("completed_tasks", [])
    if task_index in completed_tasks:
        completed_tasks.remove(task_index)
    else:
        completed_tasks.append(task_index)

    study_plans_col.update_one(
        {"plan_id": plan_id},
        {"$set": {"completed_tasks": completed_tasks}}
    )

    plan["completed_tasks"] = completed_tasks
    plan.pop("_id", None)
    return plan
