"""
Views for feedback loop API.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .feedback_loop import (
    get_feedback_collector, get_quality_scorer, get_template_optimizer,
    get_ml_pipeline, QualityScore
)


@extend_schema(
    summary="Submit feedback for a result",
    description="Submit quality feedback for a result",
    tags=["Feedback"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback(request):
    """Submit feedback for a result."""
    result_id = request.data.get('result_id')
    quality_scores = request.data.get('quality_scores', {})
    comments = request.data.get('comments')
    tags = request.data.get('tags', [])
    
    if not result_id:
        return Response(
            {'error': 'result_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create quality score object
    quality_score = QualityScore(
        accuracy=quality_scores.get('accuracy', 0.8),
        relevance=quality_scores.get('relevance', 0.8),
        completeness=quality_scores.get('completeness', 0.8),
        clarity=quality_scores.get('clarity', 0.8),
        usefulness=quality_scores.get('usefulness', 0.8)
    )
    
    try:
        collector = get_feedback_collector()
        feedback = collector.collect_feedback(
            result_id=result_id,
            user_id=str(request.user.id),
            quality_score=quality_score,
            comments=comments,
            tags=tags
        )
        
        return Response({
            'id': str(feedback.id),
            'result_id': result_id,
            'quality_score': quality_score.to_dict(),
            'message': 'Feedback submitted successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Get feedback statistics",
    description="Get feedback statistics for results",
    tags=["Feedback"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feedback_stats(request):
    """Get feedback statistics."""
    result_id = request.query_params.get('result_id')
    
    collector = get_feedback_collector()
    stats = collector.get_feedback_stats(result_id)
    
    return Response(stats)


@extend_schema(
    summary="Auto-score result quality",
    description="Automatically score result quality using AI",
    tags=["Feedback"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_score_result(request):
    """Automatically score result quality."""
    result_id = request.data.get('result_id')
    
    if not result_id:
        return Response(
            {'error': 'result_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from apps.results.models import Result
        result = Result.objects.get(id=result_id)
        
        scorer = get_quality_scorer()
        quality_score = scorer.score_result(result)
        
        return Response({
            'result_id': result_id,
            'quality_score': quality_score.to_dict()
        })
        
    except Result.DoesNotExist:
        return Response(
            {'error': 'Result not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Optimize template",
    description="Get optimization suggestions for a template",
    tags=["Feedback"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def optimize_template(request):
    """Get template optimization suggestions."""
    template_id = request.data.get('template_id')
    template_type = request.data.get('template_type', 'command')
    
    if not template_id:
        return Response(
            {'error': 'template_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    optimizer = get_template_optimizer()
    suggestions = optimizer.optimize_template(template_id, template_type)
    
    return Response(suggestions)


@extend_schema(
    summary="Retrain ML model",
    description="Retrain ML model based on feedback data",
    tags=["Feedback"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def retrain_model(request):
    """Retrain ML model."""
    model_type = request.data.get('model_type', 'agent')
    
    pipeline = get_ml_pipeline()
    results = pipeline.retrain_model(model_type)
    
    return Response(results, status=status.HTTP_200_OK)

