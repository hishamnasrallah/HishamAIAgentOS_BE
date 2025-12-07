"""
Django admin configuration for monitoring app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import SystemMetric, HealthCheck, AuditLog


@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    """System Metric admin."""
    
    list_display = (
        'metric_type',
        'value_display',
        'unit',
        'timestamp',
        'metadata_preview'
    )
    list_filter = (
        'metric_type',
        'unit',
        'timestamp'
    )
    search_fields = ('metric_type', 'metadata')
    readonly_fields = ('id', 'timestamp')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Metric Information', {
            'fields': (
                'metric_type',
                'value',
                'unit'
            )
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
    
    def value_display(self, obj):
        """Display value with unit."""
        return f"{obj.value} {obj.unit}"
    value_display.short_description = 'Value'
    value_display.admin_order_field = 'value'
    
    def metadata_preview(self, obj):
        """Preview metadata."""
        if obj.metadata:
            import json
            preview = json.dumps(obj.metadata)[:50]
            return preview + '...' if len(json.dumps(obj.metadata)) > 50 else preview
        return '-'
    metadata_preview.short_description = 'Metadata'
    
    def has_add_permission(self, request):
        """Metrics are typically created by system, not manually."""
        return True
    
    def has_change_permission(self, request, obj=None):
        """Allow editing for manual corrections."""
        return True


@admin.register(HealthCheck)
class HealthCheckAdmin(admin.ModelAdmin):
    """Health Check admin."""
    
    list_display = (
        'component',
        'status_badge',
        'response_time_display',
        'timestamp',
        'message_preview'
    )
    list_filter = (
        'component',
        'status',
        'timestamp'
    )
    search_fields = ('component', 'message', 'details')
    readonly_fields = ('id', 'timestamp')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Health Check Information', {
            'fields': (
                'component',
                'status',
                'response_time',
                'message'
            )
        }),
        ('Details', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_healthy', 'mark_degraded', 'mark_unhealthy']
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'healthy': '#28a745',
            'degraded': '#ffc107',
            'unhealthy': '#dc3545',
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
    
    def response_time_display(self, obj):
        """Display response time formatted."""
        time = float(obj.response_time) if obj.response_time else 0.0
        # Return plain formatted string - no HTML needed
        return f"{time:.2f}ms"
    response_time_display.short_description = 'Response Time'
    response_time_display.admin_order_field = 'response_time'
    
    def message_preview(self, obj):
        """Preview message."""
        if obj.message:
            return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
        return '-'
    message_preview.short_description = 'Message'
    
    def mark_healthy(self, request, queryset):
        """Mark selected health checks as healthy."""
        updated = queryset.update(status='healthy')
        self.message_user(request, f'{updated} health check(s) marked as healthy.')
    mark_healthy.short_description = 'Mark as healthy'
    
    def mark_degraded(self, request, queryset):
        """Mark selected health checks as degraded."""
        updated = queryset.update(status='degraded')
        self.message_user(request, f'{updated} health check(s) marked as degraded.')
    mark_degraded.short_description = 'Mark as degraded'
    
    def mark_unhealthy(self, request, queryset):
        """Mark selected health checks as unhealthy."""
        updated = queryset.update(status='unhealthy')
        self.message_user(request, f'{updated} health check(s) marked as unhealthy.')
    mark_unhealthy.short_description = 'Mark as unhealthy'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Audit Log admin."""
    
    list_display = (
        'timestamp',
        'user',
        'action_badge',
        'resource_type',
        'resource_id',
        'description_preview',
        'ip_address'
    )
    list_filter = (
        'action',
        'resource_type',
        'timestamp'
    )
    search_fields = (
        'user__email',
        'user__username',
        'resource_type',
        'resource_id',
        'description',
        'ip_address'
    )
    readonly_fields = (
        'id',
        'user',
        'action',
        'resource_type',
        'resource_id',
        'description',
        'changes',
        'ip_address',
        'user_agent',
        'timestamp'
    )
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Action Information', {
            'fields': (
                'user',
                'action',
                'resource_type',
                'resource_id',
                'description'
            )
        }),
        ('Changes', {
            'fields': ('changes',),
            'classes': ('collapse',)
        }),
        ('Request Information', {
            'fields': (
                'ip_address',
                'user_agent'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
    
    def action_badge(self, obj):
        """Display action as colored badge."""
        colors = {
            'create': '#28a745',
            'update': '#007bff',
            'delete': '#dc3545',
            'execute': '#6f42c1',
            'login': '#17a2b8',
            'logout': '#6c757d',
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display().upper()
        )
    action_badge.short_description = 'Action'
    action_badge.admin_order_field = 'action'
    
    def description_preview(self, obj):
        """Preview description."""
        if obj.description:
            return obj.description[:60] + '...' if len(obj.description) > 60 else obj.description
        return '-'
    description_preview.short_description = 'Description'
    
    def has_add_permission(self, request):
        """Audit logs are created by system, not manually."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Audit logs should not be modified."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup (with caution)."""
        return request.user.is_superuser
