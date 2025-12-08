"""
Django admin configuration for monitoring app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import SystemMetric, HealthCheck, AuditLog, AuditConfiguration


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


@admin.register(AuditConfiguration)
class AuditConfigurationAdmin(admin.ModelAdmin):
    """Audit Configuration admin."""
    
    list_display = (
        'name',
        'configuration_type_badge',
        'is_active',
        'is_default',
        'priority',
        'rules_summary',
        'created_at',
        'updated_at'
    )
    list_filter = (
        'configuration_type',
        'is_active',
        'is_default',
        'created_at'
    )
    search_fields = ('name', 'description', 'configuration_type')
    readonly_fields = ('id', 'created_at', 'updated_at', 'created_by')
    ordering = ('-priority', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'description',
                'configuration_type',
                'is_active',
                'is_default',
                'priority'
            )
        }),
        ('What to Audit - Actions', {
            'fields': (
                'audit_actions',
                'exclude_actions',
            ),
            'description': 'Specify which actions to audit. Leave audit_actions empty to audit all actions.'
        }),
        ('What to Audit - Resources', {
            'fields': (
                'audit_resource_types',
                'exclude_resource_types',
                'exclude_resources',
            ),
            'description': 'Specify which resource types to audit. Leave audit_resource_types empty to audit all resources.'
        }),
        ('User Filtering', {
            'fields': (
                'audit_all_users',
                'audit_users',
                'exclude_users',
            ),
            'description': 'Control which users are audited. If audit_all_users is False, only users in audit_users will be audited.'
        }),
        ('IP Address Filtering', {
            'fields': (
                'audit_all_ips',
                'audit_ips',
                'exclude_ips',
            ),
            'description': 'Control which IP addresses are audited. Useful for filtering internal vs external access.'
        }),
        ('Audit Details', {
            'fields': (
                'include_changes',
                'include_ip_address',
                'include_user_agent',
            ),
            'description': 'Control what additional information is included in audit logs.'
        }),
        ('Metadata', {
            'fields': (
                'id',
                'created_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_configurations', 'deactivate_configurations', 'set_as_default', 'remove_default']
    
    def save_model(self, request, obj, form, change):
        """Set created_by on first save."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def configuration_type_badge(self, obj):
        """Display configuration type as colored badge."""
        colors = {
            'default': '#6c757d',
            'gdpr': '#28a745',
            'security': '#dc3545',
            'compliance': '#007bff',
            'financial': '#ffc107',
            'data_access': '#17a2b8',
            'user_management': '#6f42c1',
            'system_changes': '#fd7e14',
            'custom': '#20c997',
        }
        color = colors.get(obj.configuration_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_configuration_type_display()
        )
    configuration_type_badge.short_description = 'Type'
    configuration_type_badge.admin_order_field = 'configuration_type'
    
    def rules_summary(self, obj):
        """Display summary of rules."""
        parts = []
        if obj.audit_actions:
            parts.append(f"{len(obj.audit_actions)} actions")
        if obj.audit_resource_types:
            parts.append(f"{len(obj.audit_resource_types)} resource types")
        if obj.exclude_actions or obj.exclude_resource_types:
            parts.append("with exclusions")
        if not obj.audit_all_users:
            parts.append(f"{len(obj.audit_users)} users")
        return ", ".join(parts) if parts else "All actions & resources"
    rules_summary.short_description = 'Rules Summary'
    
    def activate_configurations(self, request, queryset):
        """Activate selected configurations."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} configuration(s) activated.')
    activate_configurations.short_description = 'Activate selected configurations'
    
    def deactivate_configurations(self, request, queryset):
        """Deactivate selected configurations."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} configuration(s) deactivated.')
    deactivate_configurations.short_description = 'Deactivate selected configurations'
    
    def set_as_default(self, request, queryset):
        """Set selected configurations as default."""
        # First, unset all other defaults of the same type
        for config in queryset:
            AuditConfiguration.objects.filter(
                configuration_type=config.configuration_type,
                is_default=True
            ).exclude(id=config.id).update(is_default=False)
        
        updated = queryset.update(is_default=True)
        self.message_user(request, f'{updated} configuration(s) set as default.')
    set_as_default.short_description = 'Set as default configuration'
    
    def remove_default(self, request, queryset):
        """Remove default flag from selected configurations."""
        updated = queryset.update(is_default=False)
        self.message_user(request, f'{updated} configuration(s) removed from default.')
    remove_default.short_description = 'Remove default flag'
