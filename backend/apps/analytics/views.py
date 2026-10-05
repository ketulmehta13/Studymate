"""
Analytics views summarizing student learning metrics, quiz mastery, and study progress.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.mongo import get_collection


class ProgressSummaryView(APIView):
    """
    GET /api/progress/ or /api/analytics/
    Returns aggregated metrics for the authenticated student's dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = str(request.user.id)

        # 1. Documents statistics
        docs_col = get_collection("documents")
        total_docs = docs_col.count_documents({"user_id": user_id})
        recent_docs_cursor = docs_col.find(
            {"user_id": user_id},
            {"_id": 0, "file_path": 0}
        ).sort("created_at", -1).limit(5)
        recent_docs = list(recent_docs_cursor)

        # 2. Quiz statistics
        results_col = get_collection("quiz_results")
        quiz_cursor = results_col.find({"user_id": user_id}).sort("created_at", -1)
        quiz_list = list(quiz_cursor)
        total_quizzes = len(quiz_list)

        avg_score = 0.0
        topic_scores = {}
        if total_quizzes > 0:
            scores = [float(q.get("percentage", 0.0)) for q in quiz_list]
            avg_score = round(sum(scores) / total_quizzes, 1)

            # Topic breakdown
            for q in quiz_list:
                t = q.get("topic", "General")
                if t not in topic_scores:
                    topic_scores[t] = []
                topic_scores[t].append(float(q.get("percentage", 0.0)))

        topic_mastery = {}
        for t, s_list in topic_scores.items():
            topic_mastery[t] = round(sum(s_list) / len(s_list), 1)

        recent_quizzes = []
        for q in quiz_list[:5]:
            recent_quizzes.append({
                "quiz_id": q.get("quiz_id"),
                "topic": q.get("topic"),
                "score": q.get("score"),
                "total_questions": q.get("total_questions"),
                "percentage": q.get("percentage"),
                "created_at": q.get("created_at"),
            })

        # 3. Study Plan statistics
        plans_col = get_collection("study_plans")
        latest_plan = plans_col.find_one({"user_id": user_id}, sort=[("created_at", -1)])
        plan_summary = None
        if latest_plan:
            completed_tasks = latest_plan.get("completed_tasks", [])
            daily_tasks = latest_plan.get("daily_tasks", [])
            plan_summary = {
                "plan_id": latest_plan.get("plan_id"),
                "title": latest_plan.get("title"),
                "week": latest_plan.get("week"),
                "total_tasks": len(daily_tasks),
                "completed_tasks_count": len(completed_tasks),
                "completion_rate": round((len(completed_tasks) / len(daily_tasks)) * 100, 1) if daily_tasks else 0,
                "priority": latest_plan.get("priority"),
                "goals": latest_plan.get("goals", [])[:3],
            }

        # 4. Chat history statistics
        chat_col = get_collection("chat_history")
        total_chats = chat_col.count_documents({"user_id": user_id})

        return Response({
            "success": True,
            "metrics": {
                "documents_uploaded": total_docs,
                "quizzes_completed": total_quizzes,
                "average_quiz_score": avg_score,
                "questions_asked": total_chats,
                "completed_tasks": plan_summary["completed_tasks_count"] if plan_summary else 0,
            },
            "topic_mastery": topic_mastery,
            "recent_documents": recent_docs,
            "recent_quizzes": recent_quizzes,
            "active_study_plan": plan_summary,
        }, status=status.HTTP_200_OK)
