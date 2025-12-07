"""
Django admin configuration for workflows app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Workflow, WorkflowExecution, WorkflowStep


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    """Workflow admin."""
    
    list_display = (
        'name',
        'version',
        'status_badge',
        'is_template_badge',
        'execution_count',
        'execution_count_display',
        'created_by',
        'created_at',
        'updated_at'
    )
    list_filter = ('status', 'is_template', 'created_at', 'updated_at', 'created_by')
    search_fields = ('name', 'slug', 'description', 'created_by__email')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('id', 'execution_count', 'created_at', 'updated_at', 'execution_count_display')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'version', 'status', 'is_template')
        }),
        ('Definition', {
            'fields': ('definition',),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('execution_count', 'execution_count_display')
        }),
        ('Metadata', {
            'fields': ('created_by',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_workflows', 'archive_workflows', 'mark_as_template', 'unmark_as_template']
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'draft': '#6c757d',
            'active': '#28a745',
            'archived': '#dc3545',
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
    
    def is_template_badge(self, obj):
        """Display template status."""
        if obj.is_template:
            return format_html(
                '<span style="background-color: #6f42c1; color: white; '
                'padding: 3px 8px; border-radius: 4px;">Template</span>'
            )
        return '-'
    is_template_badge.short_description = 'Template'
    is_template_badge.admin_order_field = 'is_template'
    
    def execution_count_display(self, obj):
        """Display execution count with link."""
        count = obj.execution_count
        return format_html(
            '<span style="font-weight: bold; color: #007bff;">{}</span>',
            count
        )
    execution_count_display.short_description = 'Executions'
    
    def activate_workflows(self, request, queryset):
        """Activate selected workflows."""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} workflow(s) activated.')
    activate_workflows.short_description = 'Activate selected workflows'
    
    def archive_workflows(self, request, queryset):
        """Archive selected workflows."""
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} workflow(s) archived.')
    archive_workflows.short_description = 'Archive selected workflows'
    
    def mark_as_template(self, request, queryset):
        """Mark selected workflows as templates."""
        updated = queryset.update(is_template=True)
        self.message_user(request, f'{updated} workflow(s) marked as templates.')
    mark_as_template.short_description = 'Mark as template'
    
    def unmark_as_template(self, request, queryset):
        """Unmark selected workflows as templates."""
        updated = queryset.update(is_template=False)
        self.message_user(request, f'{updated} workflow(s) unmarked as templates.')
    unmark_as_template.short_description = 'Unmark as template'


@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(admin.ModelAdmin):
    """Workflow Execution admin."""
    
    list_display = (
        'workflow',
        'status_badge',
        'user',
        'current_step',
        'step_count',
        'retry_count',
        'started_at',
        'completed_at'
    )
    list_filter = ('status', 'started_at', 'completed_at', 'workflow')
    search_fields = (
        'workflow__name',
        'workflow__slug',
        'user__email',
        'user__username',
        'current_step'
    )
    readonly_fields = (
        'id',
        'created_at',
        'started_at',
        'completed_at',
        'step_count'
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Execution Information', {
            'fields': ('workflow', 'user', 'status', 'current_step')
        }),
        ('Data', {
            'fields': ('input_data', 'output_data', 'state'),
            'classes': ('collapse',)
        }),
        ('Error Handling', {
            'fields': ('error_message', 'retry_count')
        }),
        ('Statistics', {
            'fields': ('step_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'mark_failed', 'mark_cancelled']
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'pending': '#6c757d',
            'running': '#007bff',
            'completed': '#28a745',
            'failed': '#dc3545',
            'cancelled': '#ffc107',
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
    
    def step_count(self, obj):
        """Display number of steps."""
        return obj.steps.count()
    step_count.short_description = 'Steps'
    
    def mark_completed(self, request, queryset):
        """Mark selected executions as completed."""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} execution(s) marked as completed.')
    mark_completed.short_description = 'Mark as completed'
    
    def mark_failed(self, request, queryset):
        """Mark selected executions as failed."""
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} execution(s) marked as failed.')
    mark_failed.short_description = 'Mark as failed'
    
    def mark_cancelled(self, request, queryset):
        """Mark selected executions as cancelled."""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} execution(s) marked as cancelled.')
    mark_cancelled.short_description = 'Mark as cancelled'


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    """Workflow Step admin."""
    
    list_display = (
        'execution',
        'step_name',
        'step_order',
        'status_badge',
        'agent_execution',
        'started_at',
        'completed_at'
    )
    list_filter = ('status', 'started_at', 'completed_at', 'execution__workflow')
    search_fields = (
        'execution__workflow__name',
        'execution__workflow__slug',
        'step_name',
        'execution__user__email'
    )
    readonly_fields = (
        'id',
        'created_at',
        'started_at',
        'completed_at'
    )
    date_hierarchy = 'created_at'
    ordering = ('execution', 'step_order')
    
    fieldsets = (
        ('Step Information', {
            'fields': ('execution', 'step_name', 'step_order', 'status')
        }),
        ('Agent Execution', {
            'fields': ('agent_execution',)
        }),
        ('Data', {
            'fields': ('input_data', 'output_data'),
            'classes': ('collapse',)
        }),
        ('Error Handling', {
            'fields': ('error_message',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_completed', 'mark_failed', 'mark_skipped']
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'pending': '#6c757d',
            'running': '#007bff',
            'completed': '#28a745',
            'failed': '#dc3545',
            'skipped': '#ffc107',
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
    
    def mark_completed(self, request, queryset):
        """Mark selected steps as completed."""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} step(s) marked as completed.')
    mark_completed.short_description = 'Mark as completed'
    
    def mark_failed(self, request, queryset):
        """Mark selected steps as failed."""
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} step(s) marked as failed.')
    mark_failed.short_description = 'Mark as failed'
    
    def mark_skipped(self, request, queryset):
        """Mark selected steps as skipped."""
        updated = queryset.update(status='skipped')
        self.message_user(request, f'{updated} step(s) marked as skipped.')
    mark_skipped.short_description = 'Mark as skipped'
