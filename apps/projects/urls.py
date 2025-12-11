"""
URL configuration for projects app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, SprintViewSet, UserStoryViewSet, TaskViewSet, EpicViewSet, BugViewSet, IssueViewSet, TimeLogViewSet,
    WatcherViewSet, ProjectConfigurationViewSet, MentionViewSet, StoryCommentViewSet,
    StoryDependencyViewSet, StoryAttachmentViewSet, NotificationViewSet, ActivityViewSet, EditHistoryViewSet,
    SearchViewSet, SavedSearchViewSet, StatusChangeApprovalViewSet, StatisticsViewSet, ProjectLabelPresetViewSet,
    MilestoneViewSet, TicketReferenceViewSet, StoryLinkViewSet, CardTemplateViewSet, BoardTemplateViewSet,
    SearchHistoryViewSet, FilterPresetViewSet, TimeBudgetViewSet, OvertimeRecordViewSet, QuickFiltersViewSet,
    CardCoverImageViewSet, CardChecklistViewSet, CardVoteViewSet, StoryArchiveViewSet, StoryVersionViewSet,
    WebhookViewSet, StoryCloneViewSet, GitHubIntegrationViewSet, JiraIntegrationViewSet, SlackIntegrationViewSet,
    ProjectMemberViewSet
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
router.register(r'status-change-approvals', StatusChangeApprovalViewSet, basename='statuschangeapproval')
router.register(r'statistics', StatisticsViewSet, basename='statistics')
router.register(r'label-presets', ProjectLabelPresetViewSet, basename='labelpreset')
router.register(r'milestones', MilestoneViewSet, basename='milestone')
router.register(r'ticket-references', TicketReferenceViewSet, basename='ticketreference')
router.register(r'story-links', StoryLinkViewSet, basename='storylink')
router.register(r'card-templates', CardTemplateViewSet, basename='cardtemplate')
router.register(r'board-templates', BoardTemplateViewSet, basename='boardtemplate')
router.register(r'search-history', SearchHistoryViewSet, basename='searchhistory')
router.register(r'filter-presets', FilterPresetViewSet, basename='filterpreset')
router.register(r'time-budgets', TimeBudgetViewSet, basename='timebudget')
router.register(r'overtime-records', OvertimeRecordViewSet, basename='overtimerecord')
router.register(r'quick-filters', QuickFiltersViewSet, basename='quickfilters')
router.register(r'card-cover-images', CardCoverImageViewSet, basename='cardcoverimage')
router.register(r'card-checklists', CardChecklistViewSet, basename='cardchecklist')
router.register(r'card-votes', CardVoteViewSet, basename='cardvote')
router.register(r'story-archives', StoryArchiveViewSet, basename='storyarchive')
router.register(r'story-versions', StoryVersionViewSet, basename='storyversion')
router.register(r'webhooks', WebhookViewSet, basename='webhook')
router.register(r'story-clones', StoryCloneViewSet, basename='storyclone')
router.register(r'github-integrations', GitHubIntegrationViewSet, basename='githubintegration')
router.register(r'jira-integrations', JiraIntegrationViewSet, basename='jiraintegration')
router.register(r'slack-integrations', SlackIntegrationViewSet, basename='slackintegration')
router.register(r'project-members', ProjectMemberViewSet, basename='projectmember')

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
    path('<uuid:pk>/permissions/', ProjectViewSet.as_view({'get': 'permissions'}), name='project-permissions'),
    
    # Project tag endpoints
    path('tags/', ProjectViewSet.as_view({'get': 'tags'}), name='project-tags'),
    path('tags/autocomplete/', ProjectViewSet.as_view({'get': 'tags_autocomplete'}), name='project-tags-autocomplete'),
    
    # Router URLs for sprints, stories, tasks
    path('', include(router.urls)),
]
