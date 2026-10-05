"""
Serializers for study plan app.
"""
from rest_framework import serializers


class DailyTaskSerializer(serializers.Serializer):
    day = serializers.CharField()
    task = serializers.CharField()
    topic = serializers.CharField()
    estimated_time = serializers.CharField()
    priority = serializers.CharField()
    resources_to_review = serializers.CharField(required=False, allow_null=True)


class TopicAnalysisSerializer(serializers.Serializer):
    topic = serializers.CharField()
    accuracy_percentage = serializers.FloatField()
    status = serializers.CharField()
    recommendation = serializers.CharField()


class StudyPlanResponseSerializer(serializers.Serializer):
    plan_id = serializers.CharField()
    title = serializers.CharField()
    week = serializers.CharField()
    goals = serializers.ListField(child=serializers.CharField())
    weak_topics = serializers.ListField(child=serializers.CharField())
    topic_analysis = TopicAnalysisSerializer(many=True)
    daily_tasks = DailyTaskSerializer(many=True)
    priority = serializers.CharField()
    reason = serializers.CharField()
    created_at = serializers.CharField()
