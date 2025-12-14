"""
URL routing for chat API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MemberConversationViewSet

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'member-conversations', MemberConversationViewSet, basename='member-conversation')

urlpatterns = [
    path('', include(router.urls)),
]
