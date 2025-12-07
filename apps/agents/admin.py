"""
Django admin configuration for agents app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Agent, AgentExecution


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    """Agent admin."""
    
    list_display = (
        'name',
        'agent_id',
        'status_badge',
        'preferred_platform',
        'total_invocations',
        'success_rate_display',
        'total_cost_display',
        'execution_count',
        'last_invoked_at'
    )
    list_filter = (
        'status',
        'preferred_platform',
        'created_at',
        'updated_at'
    )
    search_fields = ('name', 'agent_id', 'description', 'model_name')
    readonly_fields = (
        'id',
        'total_invocations',
        'total_tokens_used',
        'total_cost',
        'average_response_time',
        'success_rate',
        'created_at',
        'updated_at',
        'last_invoked_at',
        'execution_count'
    )
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('agent_id', 'name', 'description', 'status', 'version')
        }),
        ('Capabilities', {
            'fields': ('capabilities',)
        }),
        ('Configuration', {
            'fields': (
                'system_prompt',
                'preferred_platform',
                'fallback_platforms',
                'model_name',
                'temperature',
                'max_tokens'
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'total_invocations',
                'total_tokens_used',
                'total_cost',
                'average_response_time',
                'success_rate',
                'execution_count'
            )
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at', 'last_invoked_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_agents', 'deactivate_agents', 'reset_metrics']
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'active': '#28a745',
            'inactive': '#6c757d',
            'maintenance': '#ffc107',
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
    
    def success_rate_display(self, obj):
        """Display success rate with color coding."""
        rate = float(obj.success_rate) if obj.success_rate else 0.0
        if rate >= 90:
            color = '#28a745'
        elif rate >= 70:
            color = '#ffc107'
        else:
            color = '#dc3545'
        # Format the number first, then pass to format_html
        rate_str = f"{rate:.1f}%"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            rate_str
        )
    success_rate_display.short_description = 'Success Rate'
    success_rate_display.admin_order_field = 'success_rate'
    
    def total_cost_display(self, obj):
        """Display total cost formatted."""
        cost = float(obj.total_cost) if obj.total_cost else 0.0
        # Return plain formatted string - no HTML needed
        return f"${cost:.4f}"
    total_cost_display.short_description = 'Total Cost'
    total_cost_display.admin_order_field = 'total_cost'
    
    def execution_count(self, obj):
        """Display number of executions."""
        return obj.executions.count()
    execution_count.short_description = 'Executions'
    
    def activate_agents(self, request, queryset):
        """Activate selected agents."""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} agent(s) activated.')
    activate_agents.short_description = 'Activate selected agents'
    
    def deactivate_agents(self, request, queryset):
        """Deactivate selected agents."""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} agent(s) deactivated.')
    deactivate_agents.short_description = 'Deactivate selected agents'
    
    def reset_metrics(self, request, queryset):
        """Reset metrics for selected agents."""
        for agent in queryset:
            agent.total_invocations = 0
            agent.total_tokens_used = 0
            agent.total_cost = 0
            agent.average_response_time = 0
            agent.success_rate = 0
            agent.save()
        self.message_user(request, f'Metrics reset for {queryset.count()} agent(s).')
    reset_metrics.short_description = 'Reset metrics for selected agents'


@admin.register(AgentExecution)
class AgentExecutionAdmin(admin.ModelAdmin):
    """Agent Execution admin."""
    
    list_display = (
        'agent',
        'user',
        'status_badge',
        'platform_used',
        'model_used',
        'tokens_used',
        'cost_display',
        'execution_time_display',
        'created_at'
    )
    list_filter = (
        'status',
        'platform_used',
        'created_at',
        'agent'
    )
    search_fields = (
        'agent__name',
        'agent__agent_id',
        'user__email',
        'user__username',
        'model_used'
    )
    readonly_fields = (
        'id',
        'created_at',
        'started_at',
        'completed_at'
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Execution Information', {
            'fields': ('agent', 'user', 'status')
        }),
        ('Input/Output', {
            'fields': ('input_data', 'context', 'output_data', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Execution Details', {
            'fields': ('platform_used', 'model_used')
        }),
        ('Performance Metrics', {
            'fields': ('tokens_used', 'cost', 'execution_time')
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
    
    def cost_display(self, obj):
        """Display cost formatted."""
        cost = float(obj.cost) if obj.cost else 0.0
        # Return plain formatted string - no HTML needed
        return f"${cost:.6f}"
    cost_display.short_description = 'Cost'
    cost_display.admin_order_field = 'cost'
    
    def execution_time_display(self, obj):
        """Display execution time formatted."""
        time = float(obj.execution_time) if obj.execution_time else 0.0
        # Return plain formatted string - no HTML needed
        return f"{time:.2f}s"
    execution_time_display.short_description = 'Time'
    execution_time_display.admin_order_field = 'execution_time'
    
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
