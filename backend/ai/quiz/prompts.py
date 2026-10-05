"""
Prompts for structured quiz generation.
"""
from langchain_core.prompts import ChatPromptTemplate

QUIZ_SYSTEM_PROMPT = """You are an expert academic examiner and educator for StudyMate AI.

Your task is to generate high-quality, multiple-choice quiz questions based strictly on the provided study notes context.

RULES:
1. Every question must test comprehension of facts and concepts directly explained in the context.
2. Provide exactly 4 options per question.
3. Only ONE option must be completely correct.
4. The remaining 3 options must be plausible distractors related to the topic.
5. Provide a clear, concise explanation referencing the concepts in the notes.
6. Target the requested difficulty level: 'easy', 'medium', or 'hard'.
"""

QUIZ_USER_PROMPT = """Topic: {topic}
Difficulty: {difficulty}
Number of questions: {number_of_questions}

Study Notes Context:
-------------------
{context}
-------------------

Generate the structured quiz now:"""

QUIZ_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", QUIZ_SYSTEM_PROMPT),
    ("human", QUIZ_USER_PROMPT),
])
