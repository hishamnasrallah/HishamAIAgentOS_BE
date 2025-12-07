"""
Views for results app.
"""

from rest_framework import viewsets
from .models import Result, ResultFeedback
from .serializers import ResultSerializer, ResultFeedbackSerializer


class ResultViewSet(viewsets.ModelViewSet):
    """Result viewset."""
    
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filterset_fields = ['result_type', 'user', 'format']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'quality_score', 'confidence_score']
    
    def get_queryset(self):
        return Result.objects.select_related(
            'user', 'agent_execution', 'workflow_execution'
        ).prefetch_related('feedback')


class ResultFeedbackViewSet(viewsets.ModelViewSet):
    """Result feedback viewset."""
    
    queryset = ResultFeedback.objects.all()
    serializer_class = ResultFeedbackSerializer
    filterset_fields = ['result', 'user', 'rating']
    ordering_fields = ['created_at', 'rating']
    
    def get_queryset(self):
        return ResultFeedback.objects.select_related('result', 'user')
