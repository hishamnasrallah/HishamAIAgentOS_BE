"""
Feedback Loop System
Quality scoring, feedback collection, and ML pipeline for continuous improvement.
"""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from django.db import models
from django.utils import timezone
from apps.results.models import Result, ResultFeedback

logger = logging.getLogger(__name__)


@dataclass
class QualityScore:
    """5-axis quality scoring system."""
    accuracy: float  # 0-1: How accurate is the result?
    relevance: float  # 0-1: How relevant to the request?
    completeness: float  # 0-1: How complete is the result?
    clarity: float  # 0-1: How clear and understandable?
    usefulness: float  # 0-1: How useful is the result?
    
    @property
    def overall(self) -> float:
        """Calculate overall quality score (average)."""
        return (
            self.accuracy + self.relevance + self.completeness +
            self.clarity + self.usefulness
        ) / 5.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'accuracy': self.accuracy,
            'relevance': self.relevance,
            'completeness': self.completeness,
            'clarity': self.clarity,
            'usefulness': self.usefulness,
            'overall': self.overall
        }


class FeedbackCollector:
    """
    Collect and analyze user feedback for continuous improvement.
    """
    
    def collect_feedback(
        self,
        result_id: str,
        user_id: str,
        quality_score: QualityScore,
        comments: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> ResultFeedback:
        """
        Collect feedback for a result.
        
        Args:
            result_id: Result ID
            user_id: User ID providing feedback
            quality_score: Quality score object
            comments: Optional comments
            tags: Optional tags
        
        Returns:
            ResultFeedback instance
        """
        try:
            result = Result.objects.get(id=result_id)
            
            # Create or update feedback
            feedback, created = ResultFeedback.objects.update_or_create(
                result=result,
                user_id=user_id,
                defaults={
                    'rating': int(quality_score.overall * 5),  # Convert to 1-5 scale
                    'comment': comments or '',
                    'quality_metrics': quality_score.to_dict(),
                    'tags': tags or [],
                    'created_at': timezone.now()
                }
            )
            
            # Update result quality score
            self._update_result_quality(result, quality_score)
            
            logger.info(f"Feedback collected for result {result_id}: {quality_score.overall:.2f}")
            return feedback
            
        except Result.DoesNotExist:
            logger.error(f"Result {result_id} not found")
            raise
        except Exception as e:
            logger.error(f"Error collecting feedback: {e}")
            raise
    
    def _update_result_quality(self, result: Result, quality_score: QualityScore):
        """Update result with quality metrics."""
        if not hasattr(result, 'quality_metrics'):
            # Store in metadata if quality_metrics field doesn't exist
            metadata = result.metadata or {}
            metadata['quality_score'] = quality_score.to_dict()
            result.metadata = metadata
        else:
            result.quality_metrics = quality_score.to_dict()
        result.save(update_fields=['metadata'])
    
    def get_feedback_stats(self, result_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get feedback statistics.
        
        Args:
            result_id: Optional result ID to filter by
        
        Returns:
            Statistics dictionary
        """
        queryset = ResultFeedback.objects.all()
        if result_id:
            queryset = queryset.filter(result_id=result_id)
        
        total = queryset.count()
        if total == 0:
            return {
                'total': 0,
                'average_rating': 0.0,
                'average_quality': 0.0,
                'distribution': {}
            }
        
        # Calculate averages
        avg_rating = queryset.aggregate(
            avg=models.Avg('rating')
        )['avg'] or 0.0
        
        # Calculate average quality metrics
        quality_scores = []
        for feedback in queryset:
            if feedback.quality_metrics:
                quality_scores.append(feedback.quality_metrics.get('overall', 0))
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Rating distribution
        distribution = {}
        for rating in range(1, 6):
            count = queryset.filter(rating=rating).count()
            distribution[rating] = count
        
        return {
            'total': total,
            'average_rating': float(avg_rating),
            'average_quality': avg_quality,
            'distribution': distribution
        }


class QualityScorer:
    """
    Automated quality scoring using AI analysis.
    """
    
    def score_result(
        self,
        result: Result,
        request_context: Optional[Dict] = None
    ) -> QualityScore:
        """
        Automatically score result quality.
        
        Args:
            result: Result object
            request_context: Optional request context
        
        Returns:
            QualityScore object
        """
        # This would use AI to analyze the result
        # For now, return a basic scoring based on result properties
        
        # Analyze result quality based on multiple factors
        # This provides a more sophisticated scoring than simple placeholders
        
        # Base scores
        accuracy = 0.6
        relevance = 0.7
        completeness = 0.6
        clarity = 0.7
        usefulness = 0.6
        
        # Adjust based on result status
        if result.status == 'success':
            accuracy += 0.2
            completeness += 0.15
        elif result.status == 'partial':
            accuracy += 0.1
            completeness += 0.05
        
        # Adjust based on metadata confidence
        if result.metadata and result.metadata.get('confidence'):
            confidence = float(result.metadata['confidence'])
            accuracy = min(1.0, accuracy + confidence * 0.2)
            relevance = min(1.0, relevance + confidence * 0.15)
        
        # Adjust based on output quality indicators
        if result.output:
            output_str = str(result.output)
            
            # Completeness: Check if output has substantial content
            if len(output_str) > 100:
                completeness += 0.1
            if len(output_str) > 500:
                completeness += 0.1
            
            # Clarity: Check for structure indicators
            if '\n' in output_str or '\t' in output_str:
                clarity += 0.1  # Has structure
            if any(marker in output_str for marker in ['##', '**', '*', '-', '1.', '2.']):
                clarity += 0.1  # Has formatting
            
            # Relevance: Check if output contains keywords from input
            if result.metadata and result.metadata.get('input_keywords'):
                keywords = result.metadata['input_keywords']
                found_keywords = sum(1 for kw in keywords if kw.lower() in output_str.lower())
                if keywords:
                    relevance += min(0.2, (found_keywords / len(keywords)) * 0.3)
        
        # Adjust based on execution metrics
        if result.metadata:
            # If execution was fast, likely more relevant
            if result.metadata.get('execution_time'):
                exec_time = float(result.metadata['execution_time'])
                if exec_time < 2.0:  # Fast execution
                    relevance += 0.05
            
            # If tokens used is reasonable, likely better quality
            if result.metadata.get('tokens_used'):
                tokens = int(result.metadata['tokens_used'])
                if 50 < tokens < 2000:  # Reasonable token range
                    usefulness += 0.1
        
        # Adjust based on feedback if available
        if result.metadata and result.metadata.get('user_feedback'):
            feedback_score = float(result.metadata.get('user_feedback', 0.5))
            # Weight feedback into all metrics
            accuracy = (accuracy + feedback_score) / 2
            relevance = (relevance + feedback_score) / 2
            usefulness = (usefulness + feedback_score) / 2
        
        return QualityScore(
            accuracy=max(0.0, min(1.0, accuracy)),
            relevance=max(0.0, min(1.0, relevance)),
            completeness=max(0.0, min(1.0, completeness)),
            clarity=max(0.0, min(1.0, clarity)),
            usefulness=max(0.0, min(1.0, usefulness))
        )


class TemplateOptimizer:
    """
    Optimize command/workflow templates based on feedback.
    """
    
    def optimize_template(
        self,
        template_id: str,
        template_type: str = 'command',  # 'command' or 'workflow'
        feedback_data: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Optimize a template based on feedback.
        
        Args:
            template_id: Template ID
            template_type: Type of template
            feedback_data: Optional feedback data
        
        Returns:
            Optimization suggestions
        """
        suggestions = []
        
        if not feedback_data:
            # Get feedback for this template
            if template_type == 'command':
                from apps.commands.models import CommandTemplate
                try:
                    template = CommandTemplate.objects.get(id=template_id)
                    # Get related results and feedback
                    # This is a simplified version
                    feedback_data = []
                except CommandTemplate.DoesNotExist:
                    logger.warning(f"Template {template_id} not found")
                    return {'suggestions': []}
        
        # Analyze feedback patterns
        low_scores = [f for f in feedback_data if f.get('quality_score', {}).get('overall', 0) < 0.6]
        
        if low_scores:
            suggestions.append({
                'type': 'template_structure',
                'message': 'Consider simplifying template structure based on low quality scores',
                'priority': 'high'
            })
        
        # Check for common issues
        common_issues = self._identify_common_issues(feedback_data)
        suggestions.extend(common_issues)
        
        return {
            'template_id': template_id,
            'suggestions': suggestions,
            'optimization_score': self._calculate_optimization_score(feedback_data)
        }
    
    def _identify_common_issues(self, feedback_data: List[Dict]) -> List[Dict]:
        """Identify common issues from feedback."""
        issues = []
        
        if not feedback_data:
            return issues
        
        # Check for clarity issues
        clarity_scores = [f.get('quality_score', {}).get('clarity', 0) for f in feedback_data]
        if clarity_scores and sum(clarity_scores) / len(clarity_scores) < 0.6:
            issues.append({
                'type': 'clarity',
                'message': 'Template output lacks clarity. Consider adding more explanations.',
                'priority': 'medium'
            })
        
        # Check for completeness issues
        completeness_scores = [f.get('quality_score', {}).get('completeness', 0) for f in feedback_data]
        if completeness_scores and sum(completeness_scores) / len(completeness_scores) < 0.6:
            issues.append({
                'type': 'completeness',
                'message': 'Template output is incomplete. Consider expanding coverage.',
                'priority': 'medium'
            })
        
        return issues
    
    def _calculate_optimization_score(self, feedback_data: List[Dict]) -> float:
        """Calculate optimization score (0-1)."""
        if not feedback_data:
            return 0.5  # Neutral
        
        scores = [f.get('quality_score', {}).get('overall', 0.5) for f in feedback_data]
        return sum(scores) / len(scores) if scores else 0.5


class MLPipeline:
    """
    ML pipeline for model retraining and optimization.
    """
    
    def retrain_model(
        self,
        model_type: str = 'agent',  # 'agent', 'command', 'workflow'
        training_data: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Retrain ML model based on feedback data.
        
        NOTE: This is a framework implementation. Full ML training requires:
        - ML framework integration (TensorFlow/PyTorch)
        - Training infrastructure
        - Model versioning and deployment
        
        For now, this collects training data and prepares it for future ML integration.
        
        Args:
            model_type: Type of model to retrain
            training_data: Optional training data
        
        Returns:
            Training results
        """
        logger.info(f"Preparing {model_type} model retraining data...")
        
        if not training_data:
            # Collect training data from feedback
            training_data = self._collect_training_data(model_type)
        
        if not training_data:
            return {
                'model_type': model_type,
                'status': 'no_data',
                'training_samples': 0,
                'message': 'No training data available. Collect feedback first.'
            }
        
        # Prepare training data summary
        # In production, this would:
        # 1. Preprocess data (tokenization, feature extraction)
        # 2. Split into train/validation sets
        # 3. Train model using ML framework
        # 4. Validate model performance
        # 5. Deploy new model version
        
        # Calculate basic statistics
        total_samples = len(training_data)
        avg_quality = sum(
            f.get('quality_score', {}).get('overall', 0.5) 
            for f in training_data
        ) / total_samples if total_samples > 0 else 0.5
        
        avg_rating = sum(
            f.get('rating', 3) 
            for f in training_data
        ) / total_samples if total_samples > 0 else 3
        
        return {
            'model_type': model_type,
            'status': 'data_prepared',
            'training_samples': total_samples,
            'average_quality': round(avg_quality, 3),
            'average_rating': round(avg_rating, 2),
            'message': f'Training data prepared ({total_samples} samples). ML training framework integration required for actual model training.',
            'next_steps': [
                'Integrate ML framework (TensorFlow/PyTorch)',
                'Implement data preprocessing pipeline',
                'Set up model training infrastructure',
                'Configure model versioning system',
                'Implement model deployment pipeline'
            ]
        }
    
    def _collect_training_data(self, model_type: str) -> List[Dict]:
        """Collect training data from feedback."""
        training_data = []
        
        # Get results with feedback
        results = Result.objects.filter(
            feedback__isnull=False
        ).select_related('feedback').distinct()
        
        for result in results:
            if result.feedback.exists():
                feedback = result.feedback.first()
                training_data.append({
                    'input': result.metadata.get('input', {}),
                    'output': result.content,
                    'quality_score': feedback.quality_metrics or {},
                    'rating': feedback.rating
                })
        
        return training_data


# Global instances
_feedback_collector = None
_quality_scorer = None
_template_optimizer = None
_ml_pipeline = None


def get_feedback_collector() -> FeedbackCollector:
    """Get or create the global feedback collector instance."""
    global _feedback_collector
    if _feedback_collector is None:
        _feedback_collector = FeedbackCollector()
    return _feedback_collector


def get_quality_scorer() -> QualityScorer:
    """Get or create the global quality scorer instance."""
    global _quality_scorer
    if _quality_scorer is None:
        _quality_scorer = QualityScorer()
    return _quality_scorer


def get_template_optimizer() -> TemplateOptimizer:
    """Get or create the global template optimizer instance."""
    global _template_optimizer
    if _template_optimizer is None:
        _template_optimizer = TemplateOptimizer()
    return _template_optimizer


def get_ml_pipeline() -> MLPipeline:
    """Get or create the global ML pipeline instance."""
    global _ml_pipeline
    if _ml_pipeline is None:
        _ml_pipeline = MLPipeline()
    return _ml_pipeline

