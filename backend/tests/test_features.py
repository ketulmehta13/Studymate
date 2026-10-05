"""
End-to-end integration tests for StudyMate AI features:
Health, Classifier, Quiz flow, Study Plan flow, Chat/RAG flow, and Progress Analytics.
"""
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

import pytest
from rest_framework.test import APIRequestFactory
from core.security import generate_tokens, MongoUser
from core.views import HealthCheckView
from apps.classifier.views import PredictTopicView, ClassifierStatusView
from apps.quiz.views import QuizGenerateView, QuizSubmitView, QuizHistoryView, QuizDetailView
from apps.studyplan.views import (
    StudyPlanView,
    StudyPlanGenerateView,
    StudyPlanHistoryView,
    StudyPlanDetailView,
    StudyPlanToggleTaskView,
)
from apps.chat.views import ChatView, ChatHistoryView
from apps.analytics.views import ProgressSummaryView
from core.mongo import get_collection


@pytest.fixture
def auth_user():
    user_id = "test_user_features_999"
    user_doc = {
        "_id": user_id,
        "username": "featuretester",
        "email": "tester@studymate.ai",
    }
    # Ensure user exists in MongoDB so JWTAuthentication can find it
    users_col = get_collection("users")
    users_col.update_one({"_id": user_id}, {"$set": user_doc}, upsert=True)

    tokens = generate_tokens(user_id, "featuretester", "tester@studymate.ai")
    return {
        "user_id": user_id,
        "mongo_user": MongoUser(user_doc),
        "access": tokens["access"],
    }


class TestHealthEndpoint:
    def test_health_check(self):
        factory = APIRequestFactory()
        request = factory.get("/api/health/")
        response = HealthCheckView.as_view()(request)
        assert response.status_code == 200
        assert response.data["status"] == "healthy"
        assert response.data["services"]["mongodb"] == "connected"


class TestClassifierAPI:
    def test_predict_topic_nlp(self):
        factory = APIRequestFactory()
        request = factory.post("/api/classifier/predict/", {
            "text": "Tokenization, lemmatization, and transformer language models in natural language processing"
        }, format="json")
        response = PredictTopicView.as_view()(request)
        assert response.status_code == 200
        assert response.data["success"] is True
        assert "topic" in response.data["data"]
        assert "confidence" in response.data["data"]

    def test_predict_topic_empty_text(self):
        factory = APIRequestFactory()
        request = factory.post("/api/classifier/predict/", {"text": ""}, format="json")
        response = PredictTopicView.as_view()(request)
        assert response.status_code == 400

    def test_classifier_status(self):
        factory = APIRequestFactory()
        request = factory.get("/api/classifier/status/")
        response = ClassifierStatusView.as_view()(request)
        assert response.status_code == 200
        assert response.data["status"] == "ready"
        assert len(response.data["classes"]) > 0


class TestQuizFlow:
    def test_quiz_lifecycle(self, auth_user):
        factory = APIRequestFactory()
        auth_header = {"HTTP_AUTHORIZATION": f"Bearer {auth_user['access']}"}

        # 1. Generate Quiz
        gen_req = factory.post(
            "/api/quiz/generate/",
            {"topic": "Data Structures", "difficulty": "medium", "number_of_questions": 3},
            format="json",
            **auth_header
        )
        gen_resp = QuizGenerateView.as_view()(gen_req)
        assert gen_resp.status_code == 201
        quiz_id = gen_resp.data["quiz_id"]
        assert len(gen_resp.data["questions"]) > 0

        # 2. Get Quiz by ID
        get_req = factory.get(f"/api/quiz/{quiz_id}/", **auth_header)
        get_resp = QuizDetailView.as_view()(get_req, quiz_id=quiz_id)
        assert get_resp.status_code == 200
        assert get_resp.data["quiz_id"] == quiz_id

        # 3. Submit Quiz
        q0 = gen_resp.data["questions"][0]
        correct_ans = q0["answer"]
        submit_req = factory.post(
            "/api/quiz/submit/",
            {"quiz_id": quiz_id, "answers": {"0": correct_ans}},
            format="json",
            **auth_header
        )
        submit_resp = QuizSubmitView.as_view()(submit_req)
        assert submit_resp.status_code == 200
        assert submit_resp.data["score"] >= 1
        assert "percentage" in submit_resp.data

        # 4. View Quiz History
        hist_req = factory.get("/api/quiz/history/", **auth_header)
        hist_resp = QuizHistoryView.as_view()(hist_req)
        assert hist_resp.status_code == 200
        assert len(hist_resp.data) >= 1


class TestStudyPlanFlow:
    def test_study_plan_lifecycle(self, auth_user):
        factory = APIRequestFactory()
        auth_header = {"HTTP_AUTHORIZATION": f"Bearer {auth_user['access']}"}

        # 1. Generate Custom Study Plan
        gen_req = factory.post(
            "/api/study-plan/",
            {
                "subjects": ["Algorithms", "Operating Systems"],
                "exam_date": "2026-11-15",
                "available_time": "2 hours/day",
                "priority": "High"
            },
            format="json",
            **auth_header
        )
        gen_resp = StudyPlanView.as_view()(gen_req)
        assert gen_resp.status_code == 201
        plan_id = gen_resp.data["plan_id"]
        assert "daily_tasks" in gen_resp.data

        # 2. Toggle a Task
        toggle_req = factory.post(
            f"/api/study-plan/{plan_id}/toggle-task/",
            {"task_index": 0},
            format="json",
            **auth_header
        )
        toggle_resp = StudyPlanToggleTaskView.as_view()(toggle_req, plan_id=plan_id)
        assert toggle_resp.status_code == 200
        assert 0 in toggle_resp.data["completed_tasks"]

        # 3. List Plans History
        hist_req = factory.get("/api/study-plan/history/", **auth_header)
        hist_resp = StudyPlanHistoryView.as_view()(hist_req)
        assert hist_resp.status_code == 200
        assert len(hist_resp.data) >= 1

        # 4. Delete Plan
        del_req = factory.delete(f"/api/study-plan/{plan_id}/", **auth_header)
        del_resp = StudyPlanDetailView.as_view()(del_req, plan_id=plan_id)
        assert del_resp.status_code == 200


class TestChatFlow:
    def test_chat_message_and_history(self, auth_user):
        factory = APIRequestFactory()
        auth_header = {"HTTP_AUTHORIZATION": f"Bearer {auth_user['access']}"}

        chat_req = factory.post(
            "/api/chat/",
            {"message": "What is reinforcement learning and how does policy gradient work?"},
            format="json",
            **auth_header
        )
        chat_resp = ChatView.as_view()(chat_req)
        assert chat_resp.status_code == 200
        assert "answer" in chat_resp.data
        conv_id = chat_resp.data["conversation_id"]

        # Fetch history
        hist_req = factory.get(f"/api/chat/{conv_id}/", **auth_header)
        hist_resp = ChatHistoryView.as_view()(hist_req, conversation_id=conv_id)
        assert hist_resp.status_code == 200
        assert len(hist_resp.data) >= 1


class TestProgressAnalytics:
    def test_analytics_summary(self, auth_user):
        factory = APIRequestFactory()
        auth_header = {"HTTP_AUTHORIZATION": f"Bearer {auth_user['access']}"}

        req = factory.get("/api/progress/", **auth_header)
        resp = ProgressSummaryView.as_view()(req)
        assert resp.status_code == 200
        assert resp.data["success"] is True
        assert "metrics" in resp.data
        assert "topic_mastery" in resp.data
