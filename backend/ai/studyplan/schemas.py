"""
Pydantic schemas for adaptive weekly study plans.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class DailyTask(BaseModel):
    """Daily study assignment."""
    day: str = Field(description="Day of the week (e.g. 'Monday', 'Tuesday').")
    task: str = Field(description="Concrete action item or study objective.")
    topic: str = Field(description="Subject/topic covered in this task.")
    estimated_time: str = Field(description="Estimated duration (e.g. '45 minutes', '1 hour').")
    priority: str = Field(default="Medium", description="Priority level: 'High', 'Medium', or 'Low'.")
    resources_to_review: Optional[str] = Field(default=None, description="Suggested notes, textbook chapters, or exercises.")


class TopicAnalysis(BaseModel):
    """Performance evaluation of a specific topic."""
    topic: str = Field(description="Subject name.")
    accuracy_percentage: float = Field(description="Percentage score achieved on quizzes (0-100).")
    status: str = Field(description="Performance rating: 'Weak', 'Moderate', or 'Strong'.")
    recommendation: str = Field(description="Tailored study advice for this topic.")


class StudyPlan(BaseModel):
    """Adaptive study plan tailored to quiz performance and detected weaknesses."""
    title: str = Field(description="Descriptive title of the study plan.")
    week: str = Field(default="Week 1", description="Target study week or timeframe.")
    goals: List[str] = Field(description="Key learning milestones for the week.", min_length=1)
    weak_topics: List[str] = Field(default_factory=list, description="List of topics prioritized due to lower quiz scores.")
    topic_analysis: List[TopicAnalysis] = Field(default_factory=list, description="Breakdown of performance per topic.")
    daily_tasks: List[DailyTask] = Field(description="Scheduled daily tasks from Monday to Sunday.", min_length=1)
    priority: str = Field(default="High", description="Overall urgency of the plan.")
    reason: str = Field(description="Pedagogical reasoning behind the prioritization.")
