"""
URL configuration for agents app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgentViewSet, AgentExecutionViewSet

router = DefaultRouter()
router.register(r'', AgentViewSet, basename='agent')
router.register(r'executions', AgentExecutionViewSet, basename='agentexecution')

urlpatterns = [
    path('', include(router.urls)),
]
