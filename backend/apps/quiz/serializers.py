"""
Serializers for quiz app.
"""
from rest_framework import serializers


class QuizGenerateRequestSerializer(serializers.Serializer):
    topic = serializers.CharField(required=True, min_length=2)
    difficulty = serializers.ChoiceField(choices=["easy", "medium", "hard"], default="medium")
    number_of_questions = serializers.IntegerField(default=5, min_value=1, max_value=20)


class QuizSubmitRequestSerializer(serializers.Serializer):
    quiz_id = serializers.CharField(required=True)
    answers = serializers.DictField(
        child=serializers.CharField(),
        required=True,
        help_text="Dictionary mapping question index (as string '0', '1'...) to chosen answer string."
    )
