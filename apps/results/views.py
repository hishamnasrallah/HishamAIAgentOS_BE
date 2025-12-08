"""
Views for results app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Result, ResultFeedback
from .serializers import ResultSerializer, ResultFeedbackSerializer
from .output_generator import OutputGenerator


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
    
    @extend_schema(
        summary="Generate formatted output",
        description="Generate output in specified format (json, markdown, html, text, code, mixed)",
        parameters=[
            {
                'name': 'format',
                'in': 'query',
                'required': False,
                'schema': {'type': 'string', 'enum': ['json', 'markdown', 'html', 'text', 'code', 'mixed']},
                'description': 'Output format (defaults to result format)'
            }
        ],
        responses={200: {'description': 'Formatted output'}}
    )
    @action(detail=True, methods=['get'])
    def generate_output(self, request, pk=None):
        """Generate formatted output for a result."""
        result = self.get_object()
        
        # Get format from query parameter or use result's format
        output_format = request.query_params.get('format', result.format)
        
        # Prepare result data
        result_data = {
            'title': result.title,
            'content': result.content,
            'format': result.format,
            'metadata': result.metadata,
            'critique': result.critique,
            'action_items': result.action_items,
            'quality_score': result.quality_score,
            'confidence_score': result.confidence_score,
            'tags': result.tags,
        }
        
        # Generate output
        generator = OutputGenerator(result_data)
        formatted_output = generator.generate(output_format)
        
        # Set appropriate content type
        content_types = {
            'json': 'application/json',
            'html': 'text/html',
            'markdown': 'text/markdown',
            'text': 'text/plain',
            'code': 'text/plain',
            'mixed': 'text/markdown',
        }
        
        return Response(
            {'output': formatted_output, 'format': output_format},
            content_type=content_types.get(output_format, 'text/plain')
        )


class ResultFeedbackViewSet(viewsets.ModelViewSet):
    """Result feedback viewset."""
    
    queryset = ResultFeedback.objects.all()
    serializer_class = ResultFeedbackSerializer
    filterset_fields = ['result', 'user', 'rating']
    ordering_fields = ['created_at', 'rating']
    
    def get_queryset(self):
        return ResultFeedback.objects.select_related('result', 'user')
