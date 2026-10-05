"""
Quiz views for StudyMate AI.
Handles quiz generation and student answer submission.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.quiz.serializers import QuizGenerateRequestSerializer, QuizSubmitRequestSerializer
from apps.quiz.services import create_and_store_quiz, evaluate_quiz_submission


class QuizGenerateView(APIView):
    """
    POST /api/quiz/generate/
    Generates a structured quiz based on topic and notes.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuizGenerateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        topic = serializer.validated_data["topic"]
        difficulty = serializer.validated_data["difficulty"]
        number_of_questions = serializer.validated_data["number_of_questions"]

        quiz_data = create_and_store_quiz(
            topic=topic,
            difficulty=difficulty,
            number_of_questions=number_of_questions,
            user_id=request.user.id
        )

        return Response(quiz_data, status=status.HTTP_201_CREATED)


class QuizSubmitView(APIView):
    """
    POST /api/quiz/submit/
    Submits student answers, calculates score, and updates topic mastery.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuizSubmitRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quiz_id = serializer.validated_data["quiz_id"]
        answers = serializer.validated_data["answers"]

        result = evaluate_quiz_submission(
            quiz_id=quiz_id,
            user_answers=answers,
            user_id=request.user.id
        )

        return Response(result, status=status.HTTP_200_OK)
