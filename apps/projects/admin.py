"""
Django admin configuration for projects app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Project, Sprint, Epic, UserStory, Task, Bug, Issue, TimeLog, ProjectConfiguration,
    Mention, StoryComment, StoryDependency, StoryAttachment, Notification, Activity, EditHistory, Watcher, SavedSearch,
    StatusChangeApproval, ProjectLabelPreset, Milestone, TicketReference, StoryLink, CardTemplate, BoardTemplate,
    SearchHistory, FilterPreset, TimeBudget, OvertimeRecord, CardCoverImage, CardChecklist, CardVote,
    StoryArchive, StoryVersion, Webhook, StoryClone, GitHubIntegration, JiraIntegration, SlackIntegration
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Project admin."""
    
    list_display = (
        'name',
        'status_badge',
        'owner',
        'member_count',
        'start_date',
        'end_date',
        'created_at'
    )
    list_filter = ('status', 'created_at', 'start_date', 'end_date')
    search_fields = ('name', 'slug', 'description', 'owner__email', 'owner__username')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('members',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'member_count', 'story_count', 'sprint_count')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'status', 'tags')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Team', {
            'fields': ('owner', 'members')
        }),
        ('Statistics', {
            'fields': ('member_count', 'story_count', 'sprint_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_active', 'mark_on_hold', 'mark_completed', 'mark_cancelled']
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'planning': '#6c757d',
            'active': '#28a745',
            'on_hold': '#ffc107',
            'completed': '#17a2b8',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.status.replace('_', ' ').title() if obj.status else 'Unknown'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def member_count(self, obj):
        """Display number of members."""
        count = obj.members.count()
        return format_html(
            '<span style="font-weight: bold; color: #007bff;">{}</span>',
            count
        )
    member_count.short_description = 'Members'
    
    def story_count(self, obj):
        """Display number of stories."""
        return obj.stories.count()
    story_count.short_description = 'Stories'
    
    def sprint_count(self, obj):
        """Display number of sprints."""
        return obj.sprints.count()
    sprint_count.short_description = 'Sprints'
    
    def mark_active(self, request, queryset):
        """Mark selected projects as active."""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} project(s) marked as active.')
    mark_active.short_description = 'Mark as active'
    
    def mark_on_hold(self, request, queryset):
        """Mark selected projects as on hold."""
        updated = queryset.update(status='on_hold')
        self.message_user(request, f'{updated} project(s) marked as on hold.')
    mark_on_hold.short_description = 'Mark as on hold'
    
    def mark_completed(self, request, queryset):
        """Mark selected projects as completed."""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} project(s) marked as completed.')
    mark_completed.short_description = 'Mark as completed'
    
    def mark_cancelled(self, request, queryset):
        """Mark selected projects as cancelled."""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} project(s) marked as cancelled.')
    mark_cancelled.short_description = 'Mark as cancelled'


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    """Sprint admin."""
    
    list_display = (
        'project',
        'sprint_number',
        'name',
        'status_badge',
        'start_date',
        'end_date',
        'story_points_progress',
        'story_count'
    )
    list_filter = ('status', 'start_date', 'end_date', 'project')
    search_fields = ('name', 'goal', 'project__name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'story_count')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'sprint_number', 'name', 'goal', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Metrics', {
            'fields': ('total_story_points', 'completed_story_points', 'story_count')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_active', 'mark_completed']
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'planned': '#6c757d',
            'active': '#28a745',
            'completed': '#17a2b8',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.status.replace('_', ' ').title() if obj.status else 'Unknown'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def story_points_progress(self, obj):
        """Display story points progress."""
        if obj.total_story_points > 0:
            percentage = (obj.completed_story_points / obj.total_story_points) * 100
            color = '#28a745' if percentage >= 100 else '#ffc107' if percentage >= 50 else '#dc3545'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}/{} ({:.0f}%)</span>',
                color,
                obj.completed_story_points,
                obj.total_story_points,
                percentage
            )
        return '-'
    story_points_progress.short_description = 'Progress'
    
    def story_count(self, obj):
        """Display number of stories."""
        return obj.stories.count()
    story_count.short_description = 'Stories'
    
    def mark_active(self, request, queryset):
        """Mark selected sprints as active."""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} sprint(s) marked as active.')
    mark_active.short_description = 'Mark as active'
    
    def mark_completed(self, request, queryset):
        """Mark selected sprints as completed."""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} sprint(s) marked as completed.')
    mark_completed.short_description = 'Mark as completed'


@admin.register(Epic)
class EpicAdmin(admin.ModelAdmin):
    """Epic admin."""
    
    list_display = (
        'number',
        'title',
        'project',
        'status_badge',
        'start_date',
        'target_date',
        'story_count',
        'created_at'
    )
    list_filter = ('status', 'created_at', 'start_date', 'target_date', 'project')
    search_fields = ('title', 'description', 'project__name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'story_count')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'title', 'description', 'status', 'tags', 'owner')
        }),
        ('Dates', {
            'fields': ('start_date', 'target_date')
        }),
        ('Statistics', {
            'fields': ('story_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_in_progress', 'mark_completed', 'mark_cancelled']
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'planned': '#6c757d',
            'in_progress': '#28a745',
            'completed': '#17a2b8',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.status.replace('_', ' ').title() if obj.status else 'Unknown'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def story_count(self, obj):
        """Display number of stories."""
        return obj.stories.count()
    story_count.short_description = 'Stories'
    
    def mark_in_progress(self, request, queryset):
        """Mark selected epics as in progress."""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} epic(s) marked as in progress.')
    mark_in_progress.short_description = 'Mark as in progress'
    
    def mark_completed(self, request, queryset):
        """Mark selected epics as completed."""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} epic(s) marked as completed.')
    mark_completed.short_description = 'Mark as completed'
    
    def mark_cancelled(self, request, queryset):
        """Mark selected epics as cancelled."""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} epic(s) marked as cancelled.')
    mark_cancelled.short_description = 'Mark as cancelled'


@admin.register(UserStory)
class UserStoryAdmin(admin.ModelAdmin):
    """User Story admin."""
    
    list_display = (
        'number',
        'title',
        'project',
        'sprint',
        'epic',
        'status_badge',
        'priority_badge',
        'story_points',
        'assigned_to',
        'ai_generated_badge',
        'task_count',
        'created_at'
    )
    list_filter = (
        'status',
        'priority',
        'generated_by_ai',
        'created_at',
        'project',
        'sprint'
    )
    search_fields = (
        'title',
        'description',
        'acceptance_criteria',
        'project__name',
        'sprint__name',
        'epic__title'
    )
    readonly_fields = ('id', 'created_at', 'updated_at', 'task_count')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'sprint', 'epic', 'title', 'description', 'acceptance_criteria')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'story_points', 'story_type', 'component')
        }),
        ('Tags & Labels', {
            'fields': ('tags', 'labels')
        }),
        ('Dates', {
            'fields': ('due_date',)
        }),
        ('AI Generation', {
            'fields': ('generated_by_ai', 'generation_workflow'),
            'classes': ('collapse',)
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Statistics', {
            'fields': ('task_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'move_to_backlog',
        'move_to_todo',
        'move_to_in_progress',
        'move_to_review',
        'move_to_done'
    ]
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'backlog': '#6c757d',
            'todo': '#17a2b8',
            'in_progress': '#007bff',
            'review': '#ffc107',
            'done': '#28a745',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.status.replace('_', ' ').title() if obj.status else 'Unknown'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def priority_badge(self, obj):
        """Display priority as colored badge."""
        priority = obj.priority or 'medium'
        # Map priority to colors
        color_map = {
            'low': '#28a745',
            'medium': '#007bff',
            'high': '#fd7e14',
            'critical': '#dc3545',
        }
        color = color_map.get(priority, '#6c757d')
        display_name = priority.title()
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            display_name
        )
    priority_badge.short_description = 'Priority'
    priority_badge.admin_order_field = 'priority'
    
    def ai_generated_badge(self, obj):
        """Display AI generation status."""
        if obj.generated_by_ai:
            return format_html(
                '<span style="background-color: #6f42c1; color: white; '
                'padding: 3px 8px; border-radius: 4px;">🤖 AI</span>'
            )
        return '-'
    ai_generated_badge.short_description = 'AI Generated'
    ai_generated_badge.admin_order_field = 'generated_by_ai'
    
    def task_count(self, obj):
        """Display number of tasks."""
        return obj.tasks.count()
    task_count.short_description = 'Tasks'
    
    def move_to_backlog(self, request, queryset):
        """Move selected stories to backlog."""
        updated = queryset.update(status='backlog')
        self.message_user(request, f'{updated} story/stories moved to backlog.')
    move_to_backlog.short_description = 'Move to backlog'
    
    def move_to_todo(self, request, queryset):
        """Move selected stories to todo."""
        updated = queryset.update(status='todo')
        self.message_user(request, f'{updated} story/stories moved to todo.')
    move_to_todo.short_description = 'Move to todo'
    
    def move_to_in_progress(self, request, queryset):
        """Move selected stories to in progress."""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} story/stories moved to in progress.')
    move_to_in_progress.short_description = 'Move to in progress'
    
    def move_to_review(self, request, queryset):
        """Move selected stories to review."""
        updated = queryset.update(status='review')
        self.message_user(request, f'{updated} story/stories moved to review.')
    move_to_review.short_description = 'Move to review'
    
    def move_to_done(self, request, queryset):
        """Move selected stories to done."""
        updated = queryset.update(status='done')
        self.message_user(request, f'{updated} story/stories moved to done.')
    move_to_done.short_description = 'Move to done'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Task admin."""
    
    list_display = (
        'number',
        'title',
        'story',
        'status_badge',
        'assigned_to',
        'time_tracking',
        'created_at'
    )
    list_filter = ('status', 'created_at', 'story__project', 'story__sprint')
    search_fields = ('title', 'description', 'story__title', 'story__project__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('story', 'title', 'description', 'status')
        }),
        ('Tags & Dates', {
            'fields': ('tags', 'due_date')
        }),
        ('Assignment', {
            'fields': ('assigned_to',)
        }),
        ('Time Tracking', {
            'fields': ('estimated_hours', 'actual_hours')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_todo', 'mark_in_progress', 'mark_done']
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'todo': '#17a2b8',
            'in_progress': '#007bff',
            'done': '#28a745',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.status.replace('_', ' ').title() if obj.status else 'Unknown'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def time_tracking(self, obj):
        """Display time tracking information."""
        est = obj.estimated_hours or 0
        act = obj.actual_hours or 0
        if act > 0 and est > 0:
            ratio = (act / est) * 100
            if ratio > 120:
                color = '#dc3545'
            elif ratio > 100:
                color = '#ffc107'
            else:
                color = '#28a745'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}h / {}h</span>',
                color,
                act,
                est
            )
        elif est > 0:
            return f"Est: {est}h"
        elif act > 0:
            return f"Act: {act}h"
        return '-'
    time_tracking.short_description = 'Time'
    
    def mark_todo(self, request, queryset):
        """Mark selected tasks as todo."""
        updated = queryset.update(status='todo')
        self.message_user(request, f'{updated} task(s) marked as todo.')
    mark_todo.short_description = 'Mark as todo'
    
    def mark_in_progress(self, request, queryset):
        """Mark selected tasks as in progress."""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} task(s) marked as in progress.')
    mark_in_progress.short_description = 'Mark as in progress'
    
    def mark_done(self, request, queryset):
        """Mark selected tasks as done."""
        updated = queryset.update(status='done')
        self.message_user(request, f'{updated} task(s) marked as done.')
    mark_done.short_description = 'Mark as done'


@admin.register(Bug)
class BugAdmin(admin.ModelAdmin):
    """Bug admin interface."""
    
    list_display = (
        'id', 'title', 'project', 'severity', 'priority', 'status', 'resolution',
        'reporter', 'assigned_to', 'environment', 'created_at'
    )
    list_filter = (
        'status', 'severity', 'priority', 'environment', 'resolution',
        'created_at', 'resolved_at', 'closed_at'
    )
    search_fields = ('title', 'description', 'project__name', 'reporter__email', 'assigned_to__email')
    readonly_fields = ('id', 'created_at', 'updated_at', 'resolved_at', 'closed_at')
    filter_horizontal = ('linked_stories',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'title', 'description', 'component')
        }),
        ('Classification', {
            'fields': ('severity', 'priority', 'status', 'resolution', 'environment')
        }),
        ('Reproduction', {
            'fields': ('reproduction_steps', 'expected_behavior', 'actual_behavior')
        }),
        ('Assignment', {
            'fields': ('reporter', 'assigned_to', 'due_date')
        }),
        ('Relationships', {
            'fields': ('linked_stories', 'duplicate_of')
        }),
        ('Metadata', {
            'fields': ('tags', 'labels')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at', 'closed_at')
        }),
    )


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """Issue admin interface."""
    
    list_display = (
        'id', 'title', 'project', 'issue_type', 'priority', 'status', 'resolution',
        'reporter', 'assigned_to', 'created_at'
    )
    list_filter = (
        'status', 'issue_type', 'priority', 'resolution',
        'created_at', 'resolved_at', 'closed_at'
    )
    search_fields = ('title', 'description', 'project__name', 'reporter__email', 'assigned_to__email')
    readonly_fields = ('id', 'created_at', 'updated_at', 'resolved_at', 'closed_at')
    filter_horizontal = ('linked_stories', 'linked_tasks', 'linked_bugs', 'watchers')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'title', 'description', 'issue_type', 'component')
        }),
        ('Classification', {
            'fields': ('priority', 'status', 'resolution', 'environment')
        }),
        ('Assignment', {
            'fields': ('reporter', 'assigned_to', 'due_date')
        }),
        ('Relationships', {
            'fields': ('linked_stories', 'linked_tasks', 'linked_bugs', 'duplicate_of')
        }),
        ('Watchers', {
            'fields': ('watchers',)
        }),
        ('Metadata', {
            'fields': ('tags', 'labels')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at', 'closed_at')
        }),
    )


@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    """Time log admin interface."""
    
    list_display = (
        'id', 'user', 'work_item_display', 'start_time', 'end_time', 
        'duration_display', 'is_billable', 'created_at'
    )
    list_filter = (
        'is_billable', 'start_time', 'created_at',
        'story', 'task', 'bug', 'issue'
    )
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'description', 'story__title', 'task__title', 'bug__title', 'issue__title'
    )
    readonly_fields = ('id', 'created_at', 'updated_at', 'duration_hours', 'is_active')
    date_hierarchy = 'start_time'
    
    fieldsets = (
        ('Work Item', {
            'fields': ('story', 'task', 'bug', 'issue')
        }),
        ('Time Tracking', {
            'fields': ('user', 'start_time', 'end_time', 'duration_minutes', 'is_billable')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def work_item_display(self, obj):
        """Display the work item this time log is for."""
        if obj.story:
            return f"Story: {obj.story.title[:50]}"
        elif obj.task:
            return f"Task: {obj.task.title[:50]}"
        elif obj.bug:
            return f"Bug: {obj.bug.title[:50]}"
        elif obj.issue:
            return f"Issue: {obj.issue.title[:50]}"
        return "Unknown"
    work_item_display.short_description = 'Work Item'
    
    def duration_display(self, obj):
        """Display duration in a readable format."""
        if obj.duration_minutes:
            hours = obj.duration_minutes // 60
            minutes = obj.duration_minutes % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        return "Active"
    duration_display.short_description = 'Duration'


@admin.register(Watcher)
class WatcherAdmin(admin.ModelAdmin):
    """Watcher admin interface."""

    list_display = (
        'id', 'user', 'content_type', 'object_id', 'content_object_display', 'created_at'
    )
    list_filter = (
        'created_at', 'user', 'content_type'
    )
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'object_id'
    )
    readonly_fields = ('id', 'created_at', 'content_object_display')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Watcher Information', {
            'fields': ('user', 'content_type', 'object_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'id'),
            'classes': ('collapse',)
        }),
    )

    def content_object_display(self, obj):
        """Display the content object being watched."""
        if obj.content_object:
            # Try common title/name fields
            if hasattr(obj.content_object, 'title'):
                return format_html(
                    f'<a href="/admin/projects/{obj.content_type.model}/{obj.object_id}/change/">{obj.content_object.title}</a>'
                )
            elif hasattr(obj.content_object, 'name'):
                return format_html(
                    f'<a href="/admin/projects/{obj.content_type.model}/{obj.object_id}/change/">{obj.content_object.name}</a>'
                )
            return str(obj.content_object)
        return "N/A"
    content_object_display.short_description = 'Watched Item'


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """Activity admin interface."""

    list_display = (
        'id', 'activity_type', 'user', 'project', 'content_type_name', 'content_object_title',
        'created_at'
    )
    list_filter = (
        'activity_type', 'created_at', 'user', 'project', 'content_type'
    )
    search_fields = (
        'description', 'user__email', 'user__first_name', 'user__last_name',
        'project__name', 'object_id', 'metadata'
    )
    readonly_fields = ('id', 'created_at', 'content_object_title', 'content_type_name')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Activity Information', {
            'fields': ('activity_type', 'user', 'project', 'description')
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_id', 'content_type_name', 'content_object_title')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'id'),
            'classes': ('collapse',)
        }),
    )

    def content_type_name(self, obj):
        """Display the content type model name."""
        return obj.content_type.model if obj.content_type else None
    content_type_name.short_description = 'Content Type'

    def content_object_title(self, obj):
        """Display the content object title/name."""
        return obj.content_object_title or 'N/A'
    content_object_title.short_description = 'Related Object'


@admin.register(EditHistory)
class EditHistoryAdmin(admin.ModelAdmin):
    """Edit History admin interface."""

    list_display = (
        'id', 'version', 'user', 'project', 'content_type_name', 'content_object_title',
        'changed_fields_count', 'created_at'
    )
    list_filter = (
        'created_at', 'user', 'project', 'content_type', 'version'
    )
    search_fields = (
        'comment', 'user__email', 'user__first_name', 'user__last_name',
        'project__name', 'object_id', 'changed_fields'
    )
    readonly_fields = ('id', 'created_at', 'content_object_title', 'content_type_name', 'changed_fields_count', 'all_diffs_display')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Edit Information', {
            'fields': ('version', 'user', 'project', 'comment')
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_id', 'content_type_name', 'content_object_title')
        }),
        ('Changes', {
            'fields': ('changed_fields', 'changed_fields_count', 'all_diffs_display')
        }),
        ('Values', {
            'fields': ('old_values', 'new_values', 'diffs'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'id'),
            'classes': ('collapse',)
        }),
    )

    def content_type_name(self, obj):
        """Display the content type model name."""
        return obj.content_type.model if obj.content_type else None
    content_type_name.short_description = 'Content Type'

    def content_object_title(self, obj):
        """Display the content object title/name."""
        return obj.content_object_title or 'N/A'
    content_object_title.short_description = 'Related Object'
    
    def changed_fields_count(self, obj):
        """Display the number of changed fields."""
        return len(obj.changed_fields) if obj.changed_fields else 0
    changed_fields_count.short_description = 'Changed Fields'
    
    def all_diffs_display(self, obj):
        """Display all diffs in a readable format."""
        diffs = obj.get_all_diffs()
        if not diffs:
            return "No diffs"
        
        result = []
        for field_name, diff_data in diffs.items():
            result.append(f"{field_name}:")
            if 'diff' in diff_data and diff_data['diff'].get('unified_diff'):
                result.append(f"  {diff_data['diff']['unified_diff']}")
            else:
                result.append(f"  Old: {diff_data.get('old_value')}")
                result.append(f"  New: {diff_data.get('new_value')}")
        
        return format_html('<pre style="white-space: pre-wrap;">{}</pre>', '\n'.join(result))
    all_diffs_display.short_description = 'All Diffs'


@admin.register(StatusChangeApproval)
class StatusChangeApprovalAdmin(admin.ModelAdmin):
    """Status Change Approval admin interface."""
    
    list_display = (
        'id', 'work_item_type', 'work_item_title', 'old_status', 'new_status', 'status_badge',
        'requested_by', 'approver', 'project', 'created_at', 'approved_at'
    )
    list_filter = ('status', 'created_at', 'approved_at', 'project')
    search_fields = (
        'id', 'old_status', 'new_status', 'reason', 'rejection_reason',
        'requested_by__email', 'requested_by__username',
        'approver__email', 'approver__username',
        'project__name'
    )
    readonly_fields = ('id', 'created_at', 'updated_at', 'approved_at', 'work_item_type', 'work_item_title')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Approval Information', {
            'fields': ('status', 'old_status', 'new_status', 'reason', 'rejection_reason')
        }),
        ('Work Item', {
            'fields': ('content_type', 'object_id', 'work_item_type', 'work_item_title')
        }),
        ('Workflow', {
            'fields': ('requested_by', 'approver', 'approved_by', 'approved_at')
        }),
        ('Project', {
            'fields': ('project',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def work_item_type(self, obj):
        """Get work item type."""
        return obj.content_type.model if obj.content_type else None
    work_item_type.short_description = 'Work Item Type'
    
    def work_item_title(self, obj):
        """Get work item title."""
        try:
            work_item = obj.work_item
            if hasattr(work_item, 'title'):
                return work_item.title
            elif hasattr(work_item, 'name'):
                return work_item.name
            return str(work_item)
        except:
            return 'N/A'
    work_item_title.short_description = 'Work Item'
    
    def status_badge(self, obj):
        """Display status as badge."""
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'cancelled': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; text-transform: capitalize;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    """Saved Search admin interface."""

    list_display = (
        'id', 'name', 'user', 'project', 'content_types', 'usage_count', 'last_used_at', 'created_at'
    )
    list_filter = (
        'created_at', 'last_used_at', 'user', 'project'
    )
    search_fields = (
        'name', 'description', 'query', 'user__email', 'user__first_name', 'user__last_name',
        'project__name'
    )
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_used_at', 'usage_count')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Search Information', {
            'fields': ('name', 'description', 'user', 'project')
        }),
        ('Search Query', {
            'fields': ('query', 'content_types', 'filters')
        }),
        ('Usage Statistics', {
            'fields': ('usage_count', 'last_used_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'id'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectConfiguration)
class ProjectConfigurationAdmin(admin.ModelAdmin):
    """Project Configuration admin."""
    
    list_display = (
        'project',
        'max_story_points_per_sprint',
        'default_sprint_duration_days',
        'default_board_view',
        'swimlane_grouping',
        'updated_by',
        'updated_at'
    )
    list_filter = ('default_board_view', 'swimlane_grouping', 'updated_at')
    search_fields = ('project__name', 'project__slug')
    readonly_fields = ('id', 'created_at', 'updated_at', 'project')
    
    fieldsets = (
        ('Project', {
            'fields': ('project',)
        }),
        ('Story Point Configuration', {
            'fields': (
                'max_story_points_per_story',
                'min_story_points_per_story',
                'story_point_scale',
                'max_story_points_per_sprint',
                'story_points_required'
            )
        }),
        ('Sprint Configuration', {
            'fields': (
                'default_sprint_duration_days',
                'sprint_start_day',
                'auto_close_sprints',
                'allow_overcommitment'
            )
        }),
        ('Board Customization', {
            'fields': (
                'default_board_view',
                'swimlane_grouping',
                'swimlane_custom_field',
                'card_display_fields',
                'card_color_by'
            )
        }),
        ('Workflow & States', {
            'fields': ('custom_states', 'state_transitions', 'board_columns'),
            'classes': ('collapse',)
        }),
        ('Automation', {
            'fields': ('automation_rules',),
            'classes': ('collapse',)
        }),
        ('Notifications', {
            'fields': ('notification_settings',),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('permission_settings',),
            'classes': ('collapse',)
        }),
        ('Integrations', {
            'fields': ('integration_settings',),
            'classes': ('collapse',)
        }),
        ('Custom Fields', {
            'fields': ('custom_fields_schema',),
            'classes': ('collapse',)
        }),
        ('Validation Rules', {
            'fields': ('validation_rules',),
            'classes': ('collapse',)
        }),
        ('Analytics', {
            'fields': ('analytics_settings',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make project readonly after creation."""
        if obj:  # Editing an existing object
            return self.readonly_fields + ('project',)
        return self.readonly_fields


@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    """Mention admin."""
    
    list_display = (
        'mention_text',
        'mentioned_user',
        'story',
        'read_badge',
        'notified_badge',
        'created_at'
    )
    list_filter = ('read', 'notified', 'created_at', 'story__project')
    search_fields = (
        'mention_text',
        'mentioned_user__email',
        'mentioned_user__username',
        'story__title'
    )
    readonly_fields = ('id', 'created_at', 'read_at', 'created_by')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Mention Information', {
            'fields': ('mention_text', 'mentioned_user', 'story', 'comment')
        }),
        ('Status', {
            'fields': ('read', 'read_at', 'notified')
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_notified']
    
    def read_badge(self, obj):
        """Display read status as badge."""
        if obj.read:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 8px; border-radius: 4px;">✓ Read</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; '
            'padding: 3px 8px; border-radius: 4px;">Unread</span>'
        )
    read_badge.short_description = 'Read Status'
    read_badge.admin_order_field = 'read'
    
    def notified_badge(self, obj):
        """Display notification status."""
        if obj.notified:
            return format_html(
                '<span style="background-color: #17a2b8; color: white; '
                'padding: 3px 8px; border-radius: 4px;">Notified</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; '
            'padding: 3px 8px; border-radius: 4px;">Pending</span>'
        )
    notified_badge.short_description = 'Notification'
    notified_badge.admin_order_field = 'notified'
    
    def mark_as_read(self, request, queryset):
        """Mark selected mentions as read."""
        from django.utils import timezone
        updated = queryset.update(read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} mention(s) marked as read.')
    mark_as_read.short_description = 'Mark as read'
    
    def mark_as_unread(self, request, queryset):
        """Mark selected mentions as unread."""
        updated = queryset.update(read=False, read_at=None)
        self.message_user(request, f'{updated} mention(s) marked as unread.')
    mark_as_unread.short_description = 'Mark as unread'
    
    def mark_as_notified(self, request, queryset):
        """Mark selected mentions as notified."""
        updated = queryset.update(notified=True)
        self.message_user(request, f'{updated} mention(s) marked as notified.')
    mark_as_notified.short_description = 'Mark as notified'


@admin.register(StoryComment)
class StoryCommentAdmin(admin.ModelAdmin):
    """Story Comment admin."""
    
    list_display = (
        'content_preview',
        'story',
        'author',
        'parent',
        'replies_count',
        'reactions_count',
        'deleted_badge',
        'created_at'
    )
    list_filter = ('deleted', 'created_at', 'story__project', 'story__sprint')
    search_fields = (
        'content',
        'author__email',
        'author__username',
        'story__title'
    )
    readonly_fields = ('id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'replies_count')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('story', 'parent', 'content', 'author')
        }),
        ('Threading', {
            'fields': ('replies_count',),
            'classes': ('collapse',)
        }),
        ('Reactions', {
            'fields': ('reactions',),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('deleted', 'deleted_at', 'deleted_by'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_deleted', 'restore_deleted']
    
    def content_preview(self, obj):
        """Display content preview."""
        preview = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return format_html('<span title="{}">{}</span>', obj.content, preview)
    content_preview.short_description = 'Content'
    
    def replies_count(self, obj):
        """Display number of replies."""
        count = obj.replies.filter(deleted=False).count()
        if count > 0:
            return format_html(
                '<span style="font-weight: bold; color: #007bff;">{}</span>',
                count
            )
        return '0'
    replies_count.short_description = 'Replies'
    
    def reactions_count(self, obj):
        """Display number of reactions."""
        if obj.reactions:
            total = sum(len(users) for users in obj.reactions.values())
            if total > 0:
                return format_html(
                    '<span style="font-weight: bold; color: #28a745;">{}</span>',
                    total
                )
        return '0'
    reactions_count.short_description = 'Reactions'
    
    def deleted_badge(self, obj):
        """Display deleted status."""
        if obj.deleted:
            return format_html(
                '<span style="background-color: #dc3545; color: white; '
                'padding: 3px 8px; border-radius: 4px;">Deleted</span>'
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; '
            'padding: 3px 8px; border-radius: 4px;">Active</span>'
        )
    deleted_badge.short_description = 'Status'
    deleted_badge.admin_order_field = 'deleted'
    
    def mark_as_deleted(self, request, queryset):
        """Mark selected comments as deleted."""
        from django.utils import timezone
        updated = queryset.update(
            deleted=True,
            deleted_at=timezone.now(),
            deleted_by=request.user
        )
        self.message_user(request, f'{updated} comment(s) marked as deleted.')
    mark_as_deleted.short_description = 'Mark as deleted'
    
    def restore_deleted(self, request, queryset):
        """Restore deleted comments."""
        updated = queryset.update(
            deleted=False,
            deleted_at=None,
            deleted_by=None
        )
        self.message_user(request, f'{updated} comment(s) restored.')
    restore_deleted.short_description = 'Restore deleted'


@admin.register(StoryDependency)
class StoryDependencyAdmin(admin.ModelAdmin):
    """Story Dependency admin."""
    
    list_display = (
        'source_story',
        'dependency_type_badge',
        'target_story',
        'resolved_badge',
        'resolved_by',
        'created_at'
    )
    list_filter = ('dependency_type', 'resolved', 'created_at', 'source_story__project')
    search_fields = (
        'source_story__title',
        'target_story__title',
        'description'
    )
    readonly_fields = ('id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'resolved_at', 'resolved_by')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Dependency Information', {
            'fields': ('source_story', 'target_story', 'dependency_type', 'description')
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolved_at', 'resolved_by'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_resolved', 'mark_as_unresolved']
    
    def dependency_type_badge(self, obj):
        """Display dependency type as badge."""
        colors = {
            'blocks': '#dc3545',
            'blocked_by': '#ffc107',
            'relates_to': '#17a2b8',
            'duplicates': '#6c757d',
            'depends_on': '#007bff',
        }
        color = colors.get(obj.dependency_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_dependency_type_display()
        )
    dependency_type_badge.short_description = 'Type'
    dependency_type_badge.admin_order_field = 'dependency_type'
    
    def resolved_badge(self, obj):
        """Display resolved status."""
        if obj.resolved:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 8px; border-radius: 4px;">✓ Resolved</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; '
            'padding: 3px 8px; border-radius: 4px;">Unresolved</span>'
        )
    resolved_badge.short_description = 'Status'
    resolved_badge.admin_order_field = 'resolved'
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected dependencies as resolved."""
        from django.utils import timezone
        updated = queryset.update(
            resolved=True,
            resolved_at=timezone.now(),
            resolved_by=request.user
        )
        self.message_user(request, f'{updated} dependency/dependencies marked as resolved.')
    mark_as_resolved.short_description = 'Mark as resolved'
    
    def mark_as_unresolved(self, request, queryset):
        """Mark selected dependencies as unresolved."""
        updated = queryset.update(
            resolved=False,
            resolved_at=None,
            resolved_by=None
        )
        self.message_user(request, f'{updated} dependency/dependencies marked as unresolved.')
    mark_as_unresolved.short_description = 'Mark as unresolved'


@admin.register(StoryAttachment)
class StoryAttachmentAdmin(admin.ModelAdmin):
    """Story Attachment admin."""
    
    list_display = (
        'file_name',
        'story',
        'file_size_display',
        'file_type',
        'uploaded_by',
        'created_at'
    )
    list_filter = ('file_type', 'created_at', 'story__project')
    search_fields = (
        'file_name',
        'description',
        'story__title',
        'uploaded_by__email'
    )
    readonly_fields = ('id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'uploaded_by', 'file_size_display')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Attachment Information', {
            'fields': ('story', 'file', 'file_name', 'file_size', 'file_size_display', 'file_type', 'description')
        }),
        ('Upload Information', {
            'fields': ('uploaded_by',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        """Display human-readable file size."""
        return obj.get_file_size_display()
    file_size_display.short_description = 'Size'


@admin.register(ProjectLabelPreset)
class ProjectLabelPresetAdmin(admin.ModelAdmin):
    """Admin interface for ProjectLabelPreset."""
    
    list_display = ['name', 'project', 'color_display', 'is_default', 'created_by', 'created_at']
    list_filter = ['project', 'is_default', 'created_at']
    search_fields = ['name', 'project__name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'name', 'color', 'description', 'is_default')
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def color_display(self, obj):
        """Display color as a colored square."""
        if obj.color:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></span> {}',
                obj.color,
                obj.color
            )
        return '-'
    color_display.short_description = 'Color'
    
    def save_model(self, request, obj, form, change):
        """Set created_by/updated_by on save."""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin."""
    
    list_display = (
        'notification_type',
        'title',
        'recipient',
        'is_read',
        'read_badge',
        'project',
        'story',
        'created_at'
    )
    list_filter = ('notification_type', 'is_read', 'email_sent', 'created_at', 'project')
    search_fields = (
        'title',
        'message',
        'recipient__email',
        'recipient__username',
        'story__title',
        'project__name'
    )
    readonly_fields = ('id', 'created_at', 'read_at', 'email_sent_at', 'created_by', 'read_badge')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('recipient', 'notification_type', 'title', 'message')
        }),
        ('Related Objects', {
            'fields': ('project', 'story', 'comment', 'mention'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'read_badge', 'email_sent', 'email_sent_at')
        }),
        ('Metadata', {
            'fields': ('metadata', 'id', 'created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def read_badge(self, obj):
        """Display read status badge."""
        if obj.is_read:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Read</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">● Unread</span>'
        )
    read_badge.short_description = 'Status'


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    """Milestone admin interface."""
    
    list_display = (
        'name',
        'project',
        'status_badge',
        'target_date',
        'progress_percentage',
        'created_by',
        'created_at'
    )
    list_filter = ('status', 'created_at', 'target_date', 'project')
    search_fields = ('name', 'description', 'project__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'name', 'description', 'status')
        }),
        ('Dates', {
            'fields': ('target_date', 'completed_date')
        }),
        ('Progress', {
            'fields': ('progress_percentage',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_in_progress', 'mark_completed', 'mark_cancelled']
    
    def status_badge(self, obj):
        """Display status as badge."""
        colors = {
            'planned': '#6c757d',
            'in_progress': '#28a745',
            'completed': '#17a2b8',
            'cancelled': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.status.replace('_', ' ').title() if obj.status else 'Unknown'
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def mark_in_progress(self, request, queryset):
        """Mark selected milestones as in progress."""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} milestone(s) marked as in progress.')
    mark_in_progress.short_description = 'Mark as in progress'
    
    def mark_completed(self, request, queryset):
        """Mark selected milestones as completed."""
        from django.utils import timezone
        from datetime import date
        updated = queryset.update(status='completed', completed_date=date.today())
        self.message_user(request, f'{updated} milestone(s) marked as completed.')
    mark_completed.short_description = 'Mark as completed'
    
    def mark_cancelled(self, request, queryset):
        """Mark selected milestones as cancelled."""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} milestone(s) marked as cancelled.')
    mark_cancelled.short_description = 'Mark as cancelled'


@admin.register(TicketReference)
class TicketReferenceAdmin(admin.ModelAdmin):
    """Ticket Reference admin interface."""
    
    list_display = (
        'ticket_id',
        'system_badge',
        'work_item_type',
        'project',
        'title_preview',
        'status',
        'sync_enabled',
        'last_synced_at',
        'created_at'
    )
    list_filter = ('system', 'sync_enabled', 'created_at', 'project')
    search_fields = ('ticket_id', 'title', 'project__name', 'ticket_url')
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_synced_at', 'work_item_type')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Reference Information', {
            'fields': ('project', 'system', 'ticket_id', 'ticket_url', 'title', 'status')
        }),
        ('Work Item', {
            'fields': ('content_type', 'object_id', 'work_item_type')
        }),
        ('Sync Settings', {
            'fields': ('sync_enabled', 'last_synced_at')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def system_badge(self, obj):
        """Display system as badge."""
        colors = {
            'github': '#24292e',
            'jira': '#0052CC',
            'gitlab': '#FC6D26',
            'linear': '#5E6AD2',
            'asana': '#F06A6A',
            'trello': '#0079BF',
            'other': '#6c757d',
        }
        color = colors.get(obj.system, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_system_display()
        )
    system_badge.short_description = 'System'
    system_badge.admin_order_field = 'system'
    
    def work_item_type(self, obj):
        """Display work item type."""
        return obj.content_type.model if obj.content_type else None
    work_item_type.short_description = 'Work Item Type'
    
    def title_preview(self, obj):
        """Display title preview."""
        if obj.title:
            preview = obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
            return format_html('<span title="{}">{}</span>', obj.title, preview)
        return '-'
    title_preview.short_description = 'Title'


@admin.register(StoryLink)
class StoryLinkAdmin(admin.ModelAdmin):
    """Story Link admin interface."""
    
    list_display = (
        'source_story',
        'link_type_badge',
        'target_story',
        'project',
        'created_by',
        'created_at'
    )
    list_filter = ('link_type', 'created_at', 'project')
    search_fields = (
        'source_story__title',
        'target_story__title',
        'description',
        'project__name'
    )
    readonly_fields = ('id', 'created_at', 'updated_at', 'project')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Link Information', {
            'fields': ('project', 'source_story', 'target_story', 'link_type', 'description')
        }),
        ('Timestamps', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def link_type_badge(self, obj):
        """Display link type as badge."""
        colors = {
            'blocks': '#dc3545',
            'blocked_by': '#ffc107',
            'relates_to': '#17a2b8',
            'duplicates': '#6c757d',
            'duplicated_by': '#6c757d',
            'parent': '#007bff',
            'child': '#007bff',
            'depends_on': '#28a745',
            'required_by': '#28a745',
        }
        color = colors.get(obj.link_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_link_type_display()
        )
    link_type_badge.short_description = 'Link Type'
    link_type_badge.admin_order_field = 'link_type'


@admin.register(CardTemplate)
class CardTemplateAdmin(admin.ModelAdmin):
    """Card Template admin interface."""
    
    list_display = (
        'name',
        'scope_badge',
        'project',
        'icon',
        'color_display',
        'is_default',
        'usage_count',
        'created_by',
        'created_at'
    )
    list_filter = ('scope', 'is_default', 'created_at', 'project')
    search_fields = ('name', 'description', 'project__name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'usage_count')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'scope', 'project', 'icon', 'color', 'is_default')
        }),
        ('Template Fields', {
            'fields': ('template_fields',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('usage_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def scope_badge(self, obj):
        """Display scope as badge."""
        colors = {
            'project': '#007bff',
            'global': '#28a745',
        }
        color = colors.get(obj.scope, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_scope_display()
        )
    scope_badge.short_description = 'Scope'
    scope_badge.admin_order_field = 'scope'
    
    def color_display(self, obj):
        """Display color as a colored square."""
        if obj.color:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></span> {}',
                obj.color,
                obj.color
            )
        return '-'
    color_display.short_description = 'Color'


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    """Search History admin interface with comprehensive features."""
    
    list_display = (
        'user',
        'query_preview',
        'project',
        'content_types_display',
        'result_count',
        'filters_count',
        'created_at'
    )
    list_filter = ('created_at', 'project', 'result_count')
    search_fields = ('query', 'user__email', 'user__username', 'project__name')
    readonly_fields = ('id', 'created_at', 'query_full', 'filters_display', 'content_types_display')
    date_hierarchy = 'created_at'
    list_per_page = 50
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Search Details', {
            'fields': ('user', 'project', 'query_full', 'result_count')
        }),
        ('Search Configuration', {
            'fields': ('filters_display', 'content_types_display'),
            'classes': ('collapse',)
        }),
        ('Raw Data', {
            'fields': ('filters', 'content_types'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def query_preview(self, obj):
        """Show truncated query."""
        if obj.query:
            return obj.query[:100] + '...' if len(obj.query) > 100 else obj.query
        return '-'
    query_preview.short_description = 'Query'
    query_preview.admin_order_field = 'query'
    
    def query_full(self, obj):
        """Show full query."""
        return obj.query or '-'
    query_full.short_description = 'Full Query'
    
    def filters_count(self, obj):
        """Display number of filters applied."""
        if obj.filters:
            return len(obj.filters) if isinstance(obj.filters, (list, dict)) else 1
        return 0
    filters_count.short_description = 'Filters'
    filters_count.admin_order_field = 'filters'
    
    def filters_display(self, obj):
        """Display filters in a readable format."""
        if obj.filters:
            import json
            try:
                return format_html('<pre>{}</pre>', json.dumps(obj.filters, indent=2))
            except:
                return str(obj.filters)
        return '-'
    filters_display.short_description = 'Filters (Formatted)'
    
    def content_types_display(self, obj):
        """Display content types in a readable format."""
        if obj.content_types:
            return ', '.join(str(ct) for ct in obj.content_types) if isinstance(obj.content_types, list) else str(obj.content_types)
        return '-'
    content_types_display.short_description = 'Content Types'


@admin.register(FilterPreset)
class FilterPresetAdmin(admin.ModelAdmin):
    """Filter Preset admin interface with comprehensive features."""
    
    list_display = (
        'name',
        'scope_badge',
        'project',
        'user',
        'is_shared',
        'is_default',
        'filters_count',
        'usage_count',
        'created_by',
        'created_at'
    )
    list_filter = ('is_shared', 'is_default', 'created_at', 'project')
    search_fields = ('name', 'description', 'project__name', 'user__email', 'created_by__email')
    readonly_fields = ('id', 'created_at', 'updated_at', 'usage_count', 'filters_display')
    date_hierarchy = 'created_at'
    list_per_page = 50
    ordering = ('is_default', '-usage_count', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'project', 'user', 'is_shared', 'is_default')
        }),
        ('Filter Configuration', {
            'fields': ('filters_display', 'filters'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('usage_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def scope_badge(self, obj):
        """Display scope badge (project vs global)."""
        if obj.project:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">Project</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">Global</span>'
            )
    scope_badge.short_description = 'Scope'
    
    def filters_count(self, obj):
        """Display number of filter rules."""
        if obj.filters:
            return len(obj.filters) if isinstance(obj.filters, list) else 1
        return 0
    filters_count.short_description = 'Filters'
    filters_count.admin_order_field = 'filters'
    
    def filters_display(self, obj):
        """Display filters in a readable format."""
        if obj.filters:
            import json
            try:
                return format_html('<pre>{}</pre>', json.dumps(obj.filters, indent=2))
            except:
                return str(obj.filters)
        return '-'
    filters_display.short_description = 'Filters (Formatted)'


@admin.register(TimeBudget)
class TimeBudgetAdmin(admin.ModelAdmin):
    """Time Budget admin interface."""
    
    list_display = (
        'scope_badge',
        'budget_hours',
        'spent_hours_display',
        'utilization_display',
        'status_badge',
        'project',
        'sprint',
        'user',
        'is_active',
        'created_at'
    )
    list_filter = ('scope', 'period', 'is_active', 'created_at', 'project')
    search_fields = ('project__name', 'sprint__name', 'story__title', 'task__title', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at', 'spent_hours', 'remaining_hours', 
                      'utilization_percentage', 'is_over_budget', 'is_warning_threshold_reached')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('scope', 'period', 'project', 'sprint', 'story', 'task', 'epic', 'user', 'is_active')
        }),
        ('Budget Details', {
            'fields': ('budget_hours', 'warning_threshold', 'period_start', 'period_end', 'auto_alert')
        }),
        ('Statistics', {
            'fields': ('spent_hours', 'remaining_hours', 'utilization_percentage', 'is_over_budget', 'is_warning_threshold_reached'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def scope_badge(self, obj):
        """Display scope as badge."""
        colors = {
            'project': '#3b82f6',
            'sprint': '#10b981',
            'story': '#f59e0b',
            'task': '#8b5cf6',
            'user': '#ec4899',
            'epic': '#6366f1',
        }
        color = colors.get(obj.scope, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_scope_display()
        )
    scope_badge.short_description = 'Scope'
    
    def spent_hours_display(self, obj):
        """Display spent hours."""
        return f"{obj.spent_hours:.2f}h"
    spent_hours_display.short_description = 'Spent'
    
    def utilization_display(self, obj):
        """Display utilization percentage."""
        color = '#dc3545' if obj.is_over_budget else '#ffc107' if obj.is_warning_threshold_reached else '#28a745'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            obj.utilization_percentage
        )
    utilization_display.short_description = 'Utilization'
    
    def status_badge(self, obj):
        """Display status badge."""
        if obj.is_over_budget:
            return format_html('<span style="color: #dc3545; font-weight: bold;">Over Budget</span>')
        elif obj.is_warning_threshold_reached:
            return format_html('<span style="color: #ffc107; font-weight: bold;">Warning</span>')
        else:
            return format_html('<span style="color: #28a745;">OK</span>')
    status_badge.short_description = 'Status'


@admin.register(OvertimeRecord)
class OvertimeRecordAdmin(admin.ModelAdmin):
    """Overtime Record admin interface with comprehensive features."""
    
    list_display = (
        'time_budget',
        'overtime_hours_display',
        'overtime_percentage_display',
        'period_display',
        'status_badge',
        'alert_sent',
        'resolved',
        'created_at'
    )
    list_filter = ('alert_sent', 'resolved', 'created_at', 'time_budget__project', 'time_budget__scope')
    search_fields = ('time_budget__project__name', 'time_budget__sprint__name', 'resolution_notes')
    readonly_fields = ('id', 'created_at', 'updated_at', 'alert_sent', 'alert_sent_at')
    date_hierarchy = 'created_at'
    list_per_page = 50
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Overtime Details', {
            'fields': ('time_budget', 'overtime_hours', 'overtime_percentage', 'period_start', 'period_end')
        }),
        ('Alert Status', {
            'fields': ('alert_sent', 'alert_sent_at'),
            'classes': ('collapse',)
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolved_at', 'resolved_by', 'resolution_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def overtime_hours_display(self, obj):
        """Display overtime hours with formatting."""
        return f"+{obj.overtime_hours:.2f}h"
    overtime_hours_display.short_description = 'Overtime Hours'
    overtime_hours_display.admin_order_field = 'overtime_hours'
    
    def overtime_percentage_display(self, obj):
        """Display overtime percentage with color coding."""
        color = '#dc3545' if obj.overtime_percentage > 20 else '#ffc107' if obj.overtime_percentage > 10 else '#f59e0b'
        return format_html(
            '<span style="color: {}; font-weight: bold;">+{}%</span>',
            color,
            obj.overtime_percentage
        )
    overtime_percentage_display.short_description = 'Overtime %'
    overtime_percentage_display.admin_order_field = 'overtime_percentage'
    
    def period_display(self, obj):
        """Display period range."""
        if obj.period_start and obj.period_end:
            return f"{obj.period_start} to {obj.period_end}"
        elif obj.period_start:
            return str(obj.period_start)
        return '-'
    period_display.short_description = 'Period'
    
    def status_badge(self, obj):
        """Display resolution status badge."""
        if obj.resolved:
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ Resolved</span>')
        else:
            return format_html('<span style="color: #dc3545; font-weight: bold;">⚠ Active</span>')
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'resolved'


@admin.register(CardCoverImage)
class CardCoverImageAdmin(admin.ModelAdmin):
    """Card Cover Image admin interface."""
    
    list_display = ('content_object', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    readonly_fields = ('id', 'created_at')


@admin.register(CardChecklist)
class CardChecklistAdmin(admin.ModelAdmin):
    """Card Checklist admin interface."""
    
    list_display = ('content_object', 'title', 'items_count', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def items_count(self, obj):
        """Display number of items."""
        return len(obj.items) if obj.items else 0
    items_count.short_description = 'Items'


@admin.register(CardVote)
class CardVoteAdmin(admin.ModelAdmin):
    """Card Vote admin interface."""
    
    list_display = ('content_object', 'user', 'vote_type', 'created_at')
    list_filter = ('vote_type', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('id', 'created_at')


@admin.register(StoryArchive)
class StoryArchiveAdmin(admin.ModelAdmin):
    """Story Archive admin interface."""
    
    list_display = ('story', 'archived_by', 'archived_at', 'reason_preview')
    list_filter = ('archived_at',)
    search_fields = ('story__title', 'reason')
    readonly_fields = ('id', 'archived_at')
    
    def reason_preview(self, obj):
        """Show truncated reason."""
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    reason_preview.short_description = 'Reason'


@admin.register(StoryVersion)
class StoryVersionAdmin(admin.ModelAdmin):
    """Story Version admin interface."""
    
    list_display = ('story', 'version_number', 'title', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('story__title', 'title')
    readonly_fields = ('id', 'created_at')


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    """Webhook admin interface."""
    
    list_display = ('name', 'project', 'url_preview', 'events_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'project')
    search_fields = ('name', 'url')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def url_preview(self, obj):
        """Show truncated URL."""
        return obj.url[:50] + '...' if len(obj.url) > 50 else obj.url
    url_preview.short_description = 'URL'
    
    def events_count(self, obj):
        """Display number of events."""
        return len(obj.events) if obj.events else 0
    events_count.short_description = 'Events'


@admin.register(StoryClone)
class StoryCloneAdmin(admin.ModelAdmin):
    """Story Clone admin interface."""
    
    list_display = ('original_story', 'cloned_story', 'cloned_by', 'cloned_at')
    list_filter = ('cloned_at',)
    search_fields = ('original_story__title', 'cloned_story__title')
    readonly_fields = ('id', 'cloned_at')
    
    def color_display(self, obj):
        """Display color as a colored square."""
        if obj.color:
            return format_html(
                '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></span> {}',
                obj.color,
                obj.color
            )
        return '-'
    color_display.short_description = 'Color'


@admin.register(BoardTemplate)
class BoardTemplateAdmin(admin.ModelAdmin):
    """Board Template admin interface."""
    
    list_display = (
        'name',
        'scope_badge',
        'project',
        'icon',
        'is_default',
        'usage_count',
        'created_by',
        'created_at'
    )
    list_filter = ('scope', 'is_default', 'created_at', 'project')
    search_fields = ('name', 'description', 'project__name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'usage_count')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'scope', 'project', 'icon', 'is_default')
        }),
        ('Board Configuration', {
            'fields': ('board_config',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('usage_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def scope_badge(self, obj):
        """Display scope as badge."""
        colors = {
            'project': '#007bff',
            'global': '#28a745',
        }
        color = colors.get(obj.scope, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_scope_display()
        )
    scope_badge.short_description = 'Scope'
    scope_badge.admin_order_field = 'scope'


@admin.register(GitHubIntegration)
class GitHubIntegrationAdmin(admin.ModelAdmin):
    """GitHub Integration admin interface."""
    
    list_display = (
        'project',
        'repository_display',
        'is_active',
        'sync_issues',
        'sync_commits',
        'sync_pull_requests',
        'created_by',
        'created_at'
    )
    list_filter = ('is_active', 'sync_issues', 'sync_commits', 'sync_pull_requests', 'created_at', 'project')
    search_fields = ('repository_owner', 'repository_name', 'project__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Integration Details', {
            'fields': ('project', 'repository_owner', 'repository_name', 'access_token', 'is_active')
        }),
        ('Sync Configuration', {
            'fields': ('sync_issues', 'sync_commits', 'sync_pull_requests',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def repository_display(self, obj):
        """Display repository owner/name."""
        return f"{obj.repository_owner}/{obj.repository_name}"
    repository_display.short_description = 'Repository'


@admin.register(JiraIntegration)
class JiraIntegrationAdmin(admin.ModelAdmin):
    """Jira Integration admin interface."""
    
    list_display = (
        'project',
        'base_url_preview',
        'project_key',
        'is_active',
        'sync_issues',
        'auto_create',
        'created_by',
        'created_at'
    )
    list_filter = ('is_active', 'sync_issues', 'auto_create', 'created_at', 'project')
    search_fields = ('base_url', 'project_key', 'email', 'project__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Integration Details', {
            'fields': ('project', 'base_url', 'project_key', 'email', 'api_token', 'is_active')
        }),
        ('Sync Configuration', {
            'fields': ('sync_issues', 'auto_create',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def base_url_preview(self, obj):
        """Show truncated base URL."""
        if obj.base_url:
            return obj.base_url[:50] + '...' if len(obj.base_url) > 50 else obj.base_url
        return '-'
    base_url_preview.short_description = 'Jira URL'


@admin.register(SlackIntegration)
class SlackIntegrationAdmin(admin.ModelAdmin):
    """Slack Integration admin interface."""
    
    list_display = (
        'project',
        'channel',
        'is_active',
        'notification_events_count',
        'created_by',
        'created_at'
    )
    list_filter = ('is_active', 'created_at', 'project')
    search_fields = ('channel', 'project__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Integration Details', {
            'fields': ('project', 'webhook_url', 'bot_token', 'channel', 'is_active')
        }),
        ('Notification Configuration', {
            'fields': ('notification_events',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def notification_events_count(self, obj):
        """Display number of notification events."""
        return len(obj.notification_events) if obj.notification_events else 0
    notification_events_count.short_description = 'Events'
