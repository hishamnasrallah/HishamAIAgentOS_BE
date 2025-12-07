"""
Serializers for results app.
"""

from rest_framework import serializers
from .models import Result, ResultFeedback


class ResultSerializer(serializers.ModelSerializer):
    """Result serializer."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True, allow_null=True)
    feedback_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Result
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_feedback_count(self, obj):
        return obj.feedback.count()


class ResultFeedbackSerializer(serializers.ModelSerializer):
    """Result feedback serializer."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True, allow_null=True)
    result_title = serializers.CharField(source='result.title', read_only=True)
    
    class Meta:
        model = ResultFeedback
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
