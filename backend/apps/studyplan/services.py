"""
Study plan service layer managing adaptive plan generation and retrieval.
"""
from typing import Dict, Any, Optional

from core.mongo import get_collection
from core.exceptions import StudyPlanError
from core.logging_config import get_logger
from ai.studyplan.generator import generate_study_plan

logger = get_logger("studyplan.services")


def create_and_store_study_plan(user_id: str) -> Dict[str, Any]:
    """
    Generates a new adaptive weekly study plan and saves it in MongoDB.
    """
    plan_data = generate_study_plan(user_id=user_id)
    plan_id = plan_data.get("plan_id")

    study_plans_col = get_collection("study_plans")
    doc = dict(plan_data)
    doc["user_id"] = str(user_id)
    study_plans_col.insert_one(doc)

    logger.info(f"Generated and stored study plan {plan_id} for user {user_id}")
    plan_data.pop("_id", None)
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
