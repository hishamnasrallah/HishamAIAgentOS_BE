"""
URL configuration for workflows app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowViewSet, WorkflowExecutionViewSet, WorkflowStepViewSet

router = DefaultRouter()
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'executions', WorkflowExecutionViewSet, basename='workflowexecution')
router.register(r'steps', WorkflowStepViewSet, basename='workflowstep')

urlpatterns = [
    path('', include(router.urls)),
]
