"""
Pydantic schemas for structured quiz generation and validation.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class QuizQuestion(BaseModel):
    """Represents an individual multiple-choice quiz question."""
    question: str = Field(description="Clear, well-formed question testing conceptual understanding.")
    options: List[str] = Field(description="List of 4 distinct answer choices.", min_length=2, max_length=4)
    answer: str = Field(description="The single correct answer choice, matching exactly one of the options.")
    difficulty: str = Field(default="medium", description="Difficulty level: 'easy', 'medium', or 'hard'.")
    source_chunk: Optional[str] = Field(default=None, description="Source reference or snippet supporting the question.")
    explanation: Optional[str] = Field(default=None, description="Brief explanation of why the answer is correct.")

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        valid = {"easy", "medium", "hard"}
        v_clean = v.strip().lower()
        if v_clean not in valid:
            return "medium"
        return v_clean

    @model_validator(mode="after")
    def validate_answer_in_options(self):
        answer = self.answer.strip()
        options_stripped = [opt.strip() for opt in self.options]

        # Case-insensitive matching if exact doesn't match
        if answer not in options_stripped:
            for opt in options_stripped:
                if answer.lower() == opt.lower():
                    self.answer = opt
                    break
            else:
                # If LLM wrote something like "A) Option text"
                for opt in options_stripped:
                    if answer.endswith(opt) or opt.endswith(answer):
                        self.answer = opt
                        break
                else:
                    raise ValueError(f"Correct answer '{answer}' is not listed among the options: {self.options}")
        return self


class Quiz(BaseModel):
    """Complete structured quiz schema."""
    topic: str = Field(description="Academic topic of the quiz.")
    difficulty: str = Field(default="medium", description="Overall quiz difficulty.")
    questions: List[QuizQuestion] = Field(description="List of multiple-choice questions.", min_length=1)

    @field_validator("difficulty")
    @classmethod
    def validate_overall_difficulty(cls, v: str) -> str:
        valid = {"easy", "medium", "hard"}
        v_clean = v.strip().lower()
        if v_clean not in valid:
            return "medium"
        return v_clean
