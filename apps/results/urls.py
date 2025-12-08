"""
URL configuration for results app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResultViewSet, ResultFeedbackViewSet
from .feedback_views import (
    submit_feedback, feedback_stats, auto_score_result,
    optimize_template, retrain_model
)

router = DefaultRouter()
router.register(r'results', ResultViewSet, basename='result')
router.register(r'feedback', ResultFeedbackViewSet, basename='resultfeedback')

urlpatterns = [
    path('', include(router.urls)),
    # Feedback loop endpoints
    path('feedback/submit/', submit_feedback, name='submit_feedback'),
    path('feedback/stats/', feedback_stats, name='feedback_stats'),
    path('feedback/auto-score/', auto_score_result, name='auto_score_result'),
    path('feedback/optimize-template/', optimize_template, name='optimize_template'),
    path('feedback/retrain-model/', retrain_model, name='retrain_model'),
]
