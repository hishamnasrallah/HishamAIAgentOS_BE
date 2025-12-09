"""
URL configuration for projects app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, SprintViewSet, UserStoryViewSet, TaskViewSet, EpicViewSet, BugViewSet, IssueViewSet, TimeLogViewSet,
    WatcherViewSet, ProjectConfigurationViewSet, MentionViewSet, StoryCommentViewSet,
    StoryDependencyViewSet, StoryAttachmentViewSet, NotificationViewSet, ActivityViewSet, EditHistoryViewSet,
    SearchViewSet, SavedSearchViewSet
)

# Create router for nested resources
router = DefaultRouter()
router.register(r'sprints', SprintViewSet, basename='sprint')
router.register(r'stories', UserStoryViewSet, basename='userstory')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'bugs', BugViewSet, basename='bug')
router.register(r'issues', IssueViewSet, basename='issue')
router.register(r'time-logs', TimeLogViewSet, basename='timelog')
router.register(r'watchers', WatcherViewSet, basename='watcher')
router.register(r'epics', EpicViewSet, basename='epic')
router.register(r'configurations', ProjectConfigurationViewSet, basename='projectconfiguration')
router.register(r'mentions', MentionViewSet, basename='mention')
router.register(r'comments', StoryCommentViewSet, basename='storycomment')
router.register(r'dependencies', StoryDependencyViewSet, basename='storydependency')
router.register(r'attachments', StoryAttachmentViewSet, basename='storyattachment')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'edit-history', EditHistoryViewSet, basename='edithistory')
router.register(r'search', SearchViewSet, basename='search')
router.register(r'saved-searches', SavedSearchViewSet, basename='savedsearch')

# Create explicit URL patterns for projects to avoid conflicts
urlpatterns = [
    # Project CRUD endpoints
    path('', ProjectViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-list'),
    path('<uuid:pk>/', ProjectViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='project-detail'),
    path('<uuid:pk>/generate-stories/', ProjectViewSet.as_view({'post': 'generate_stories'}), name='project-generate-stories'),
    path('<uuid:pk>/velocity/', ProjectViewSet.as_view({'get': 'velocity'}), name='project-velocity'),
    path('<uuid:pk>/members/', ProjectViewSet.as_view({'get': 'members'}), name='project-members'),
    path('<uuid:pk>/members/add/', ProjectViewSet.as_view({'post': 'add_member'}), name='project-add-member'),
    path('<uuid:pk>/members/remove/', ProjectViewSet.as_view({'post': 'remove_member'}), name='project-remove-member'),
    
    # Project tag endpoints
    path('tags/', ProjectViewSet.as_view({'get': 'tags'}), name='project-tags'),
    path('tags/autocomplete/', ProjectViewSet.as_view({'get': 'tags_autocomplete'}), name='project-tags-autocomplete'),
    
    # Router URLs for sprints, stories, tasks
    path('', include(router.urls)),
]
