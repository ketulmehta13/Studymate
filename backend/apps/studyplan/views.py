from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.studyplan.services import (
    get_latest_study_plan,
    create_and_store_study_plan,
    list_user_study_plans,
    get_study_plan_by_id,
    delete_study_plan,
    toggle_study_plan_task,
)


class StudyPlanView(APIView):
    """
    GET /api/study-plan/ -> Returns latest adaptive study plan.
    POST /api/study-plan/ -> Generates a study plan with optional custom inputs.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan = get_latest_study_plan(user_id=request.user.id)
        return Response(plan, status=status.HTTP_200_OK)

    def post(self, request):
        custom_topics = request.data.get("topics") or request.data.get("subjects") or []
        if isinstance(custom_topics, str):
            custom_topics = [t.strip() for t in custom_topics.split(",") if t.strip()]

        plan = create_and_store_study_plan(
            user_id=request.user.id,
            custom_topics=custom_topics,
            exam_date=request.data.get("exam_date"),
            available_time=request.data.get("available_time"),
            priority=request.data.get("priority"),
        )
        return Response(plan, status=status.HTTP_201_CREATED)


class StudyPlanGenerateView(APIView):
    """
    POST /api/study-plan/generate/
    Forces generation of study plan with optional custom targets.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        custom_topics = request.data.get("topics") or request.data.get("subjects") or []
        if isinstance(custom_topics, str):
            custom_topics = [t.strip() for t in custom_topics.split(",") if t.strip()]

        plan = create_and_store_study_plan(
            user_id=request.user.id,
            custom_topics=custom_topics,
            exam_date=request.data.get("exam_date"),
            available_time=request.data.get("available_time"),
            priority=request.data.get("priority"),
        )
        return Response(plan, status=status.HTTP_201_CREATED)


class StudyPlanHistoryView(APIView):
    """
    GET /api/study-plan/history/
    Returns all previous study plans for authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plans = list_user_study_plans(user_id=request.user.id)
        return Response(plans, status=status.HTTP_200_OK)


class StudyPlanDetailView(APIView):
    """
    GET /api/study-plan/<plan_id>/
    DELETE /api/study-plan/<plan_id>/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, plan_id):
        plan = get_study_plan_by_id(plan_id=plan_id, user_id=request.user.id)
        return Response(plan, status=status.HTTP_200_OK)

    def delete(self, request, plan_id):
        delete_study_plan(plan_id=plan_id, user_id=request.user.id)
        return Response({"message": "Study plan deleted successfully."}, status=status.HTTP_200_OK)


class StudyPlanToggleTaskView(APIView):
    """
    POST /api/study-plan/<plan_id>/toggle-task/
    Body: {"task_index": 0}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, plan_id):
        task_index = int(request.data.get("task_index", 0))
        updated_plan = toggle_study_plan_task(
            plan_id=plan_id,
            task_index=task_index,
            user_id=request.user.id
        )
        return Response(updated_plan, status=status.HTTP_200_OK)
