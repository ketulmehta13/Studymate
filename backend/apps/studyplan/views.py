"""
Study plan views for StudyMate AI.
Handles retrieving current plan and generating updated plans.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.studyplan.services import get_latest_study_plan, create_and_store_study_plan


class StudyPlanView(APIView):
    """
    GET /api/study-plan/
    Returns the user's latest adaptive study plan.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan = get_latest_study_plan(user_id=request.user.id)
        return Response(plan, status=status.HTTP_200_OK)


class StudyPlanGenerateView(APIView):
    """
    POST /api/study-plan/generate/
    Forces re-generation of a new adaptive study plan based on updated quiz performance.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan = create_and_store_study_plan(user_id=request.user.id)
        return Response(plan, status=status.HTTP_201_CREATED)
