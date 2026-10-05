"""
Prompts for LangGraph Agent nodes: Router, Grader, Rewriter, and Self-Check.
"""
from langchain_core.prompts import ChatPromptTemplate

# 1. Router Prompt
ROUTER_SYSTEM_PROMPT = """You are an intent classifier for StudyMate AI study assistant.

Analyze the user's message and categorize it into exactly ONE of the following 4 classes:
- Q&A: Questions asking for explanations, definitions, concepts, or problem-solving related to study materials.
- QUIZ: Requests asking to generate a quiz, practice questions, flashcards, or tests.
- STUDY_PLAN: Requests asking for a study schedule, weekly plan, exam timetable, or learning roadmap.
- OFF_TOPIC: General banter, non-academic queries (weather, sports, politics), or unrelated topics.

Output ONLY the category name: 'Q&A', 'QUIZ', 'STUDY_PLAN', or 'OFF_TOPIC'. Do not add any punctuation or extra words.
"""

ROUTER_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", ROUTER_SYSTEM_PROMPT),
    ("human", "User message: {question}\nCategory:"),
])

# 2. Retrieval Grader Prompt
GRADER_SYSTEM_PROMPT = """You are an academic retrieval relevance grader for StudyMate AI.

Your task is to assess whether the retrieved context passages contain facts or concepts relevant to answering the user's question.

CRITERIA:
- If the passages contain keywords, semantic concepts, or background directly helpful in addressing the question, grade as: GOOD
- If the passages are completely unrelated, off-topic, or empty, grade as: POOR

Output ONLY 'GOOD' or 'POOR'. Do not include explanations.
"""

GRADER_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", GRADER_SYSTEM_PROMPT),
    ("human", "Retrieved Passages:\n{context}\n\nUser Question: {question}\nRelevance Grade (GOOD or POOR):"),
])

# 3. Query Rewriter Prompt
REWRITER_SYSTEM_PROMPT = """You are an academic query rewriter for StudyMate AI.

The previous retrieval failed to locate relevant study notes for the user's question.
Your task is to rephrase and optimize the question so it performs better in semantic and lexical document search.
Extract core academic terms, eliminate ambiguity, and make the query specific.

Output ONLY the rewritten search query.
"""

REWRITER_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", REWRITER_SYSTEM_PROMPT),
    ("human", "Original Question: {question}\nRewritten search query:"),
])

# 4. Self Check (Groundedness) Prompt
SELF_CHECK_SYSTEM_PROMPT = """You are a groundedness and hallucination checker for StudyMate AI.

Assess whether the generated answer is strictly supported by the provided retrieved context.

RULES:
- If the answer relies on facts directly stated in the context without ungrounded hallucinations, output: PASS
- If the answer makes up facts or contradicts the context, output: FAIL

Output ONLY 'PASS' or 'FAIL'.
"""

SELF_CHECK_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SELF_CHECK_SYSTEM_PROMPT),
    ("human", "Context:\n{context}\n\nGenerated Answer:\n{answer}\n\nGroundedness result (PASS or FAIL):"),
])
