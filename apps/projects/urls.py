"""
URL configuration for projects app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, SprintViewSet, UserStoryViewSet, TaskViewSet, EpicViewSet

# Create router for nested resources
router = DefaultRouter()
router.register(r'sprints', SprintViewSet, basename='sprint')
router.register(r'stories', UserStoryViewSet, basename='userstory')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'epics', EpicViewSet, basename='epic')

# Create explicit URL patterns for projects to avoid conflicts
urlpatterns = [
    # Project CRUD endpoints
    path('', ProjectViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-list'),
    path('<uuid:pk>/', ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='project-detail'),
    path('<uuid:pk>/generate-stories/', ProjectViewSet.as_view({'post': 'generate_stories'}), name='project-generate-stories'),
    path('<uuid:pk>/velocity/', ProjectViewSet.as_view({'get': 'velocity'}), name='project-velocity'),
    
    # Router URLs for sprints, stories, tasks
    path('', include(router.urls)),
]
