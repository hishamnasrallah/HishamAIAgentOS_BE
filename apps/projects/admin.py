"""
Django admin configuration for projects app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Project, Sprint, Epic, UserStory, Task


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
            'fields': ('name', 'slug', 'description', 'status')
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
            obj.get_status_display()
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
            obj.get_status_display()
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
            'fields': ('project', 'title', 'description', 'status')
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
            obj.get_status_display()
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
            'fields': ('status', 'priority', 'story_points')
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
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def priority_badge(self, obj):
        """Display priority as colored badge."""
        colors = {
            'low': '#6c757d',
            'medium': '#17a2b8',
            'high': '#ffc107',
            'critical': '#dc3545',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
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
            obj.get_status_display()
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
