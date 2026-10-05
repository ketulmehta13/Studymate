"""
Prompts for adaptive study plan generation.
"""
from langchain_core.prompts import ChatPromptTemplate

STUDYPLAN_SYSTEM_PROMPT = """You are an adaptive academic mentor and learning strategist for StudyMate AI.

Your task is to create a personalized, highly effective 7-day study plan based on the student's recent quiz performance and detected knowledge gaps.

RULES:
1. Prioritization: Always prioritize topics where the student scored lowest (< 70% accuracy). Allocate more time and earlier days in the week to these weak areas.
2. Structure: Distribute tasks logically across the week (Monday through Sunday), including revision and consolidation.
3. Realistic & Actionable: Give concrete tasks (e.g. "Work through 5 gradient descent derivations", not "Study math").
4. Clear Rationale: Explain why the schedule is ordered the way it is in the 'reason' field.
"""

STUDYPLAN_USER_PROMPT = """Student Performance Summary:
----------------------------
Weak Topics (Priority Order): {weak_topics}
Topic Scores: {topic_scores}

Recent Notes Context:
---------------------
{notes_context}

Generate the structured weekly study plan now:"""

STUDYPLAN_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", STUDYPLAN_SYSTEM_PROMPT),
    ("human", STUDYPLAN_USER_PROMPT),
])
