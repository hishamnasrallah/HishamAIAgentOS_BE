"""
Admin interface for AI platform integrations.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import AIPlatform, PlatformUsage


@admin.register(AIPlatform)
class AIPlatformAdmin(admin.ModelAdmin):
    """Admin interface for AI platforms with full field integration."""

    # --------------------------------------------------
    # LIST VIEW CONFIGURATION
    # --------------------------------------------------
    list_display = [
        'display_name',
        'platform_name',
        'status_badge',
        'is_enabled_badge',
        'is_healthy_badge',
        'priority',
        'total_requests',
        'total_cost_display',
        'updated_at',
    ]

    list_filter = [
        'platform_name',
        'status',
        'is_enabled',
        'is_healthy',
        'supports_vision',
        'supports_json_mode',
        'supports_image_generation',
        'created_at',
    ]

    search_fields = [
        'display_name',
        'platform_name',
        'api_type',
        'default_model',
    ]

    readonly_fields = [
        'id',
        'api_key_status',
        'total_requests',
        'failed_requests',
        'total_tokens',
        'total_cost',
        'last_health_check',
        'created_at',
        'updated_at',
        'is_healthy',
    ]

    # --------------------------------------------------
    # FIELD GROUPS
    # --------------------------------------------------
    fieldsets = (
        ('Basic Information', {
            'fields': (
            'display_name', 'platform_name', 'api_type', 'default_model', 'status', 'is_default', 'is_enabled',
            'priority')
        }),
        ('API Configuration', {
            'fields': ('api_key', 'api_key_status', 'api_url', 'organization_id', 'timeout', 'max_tokens'),
            'description': 'API key is encrypted at rest. Enter a new key to update it.'
        }),
        ('Capabilities', {
            'fields': ('supports_vision', 'supports_json_mode', 'supports_image_generation')
        }),
        ('Rate Limiting', {
            'fields': ('rate_limit_per_minute', 'rate_limit_per_day')
        }),
        ('Statistics', {
            'fields': (
                'total_requests',
                'failed_requests',
                'total_tokens',
                'total_cost',
                'last_health_check',
                'is_healthy'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # --------------------------------------------------
    # BADGES
    # --------------------------------------------------
    def status_badge(self, obj):
        colors = {
            'active': '#28a745',
            'inactive': '#dc3545',
            'maintenance': '#ffc107',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 8px; border-radius: 4px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def is_enabled_badge(self, obj):
        if obj.is_enabled:
            return format_html('<span style="color: #28a745;">Enabled</span>')
        return format_html('<span style="color: #dc3545;">Disabled</span>')
    is_enabled_badge.short_description = 'Enabled'
    is_enabled_badge.admin_order_field = 'is_enabled'

    def is_healthy_badge(self, obj):
        if obj.is_healthy:
            return format_html('<span style="color: #28a745;">✓ Healthy</span>')
        return format_html('<span style="color: #ffc107;">⚠ Unhealthy</span>')
    is_healthy_badge.short_description = 'Health'
    is_healthy_badge.admin_order_field = 'is_healthy'

    def total_cost_display(self, obj):
        cost = float(obj.total_cost) if obj.total_cost else 0.0
        # Return plain formatted string - no HTML needed
        return f"${cost:.4f}"
    total_cost_display.short_description = 'Total Cost'
    total_cost_display.admin_order_field = 'total_cost'
    
    def api_key_status(self, obj):
        """Display API key status without exposing the key."""
        if not obj.has_api_key():
            return format_html('<span style="color: #dc3545;">No API key set</span>')
        
        encrypted = obj.is_api_key_encrypted()
        if encrypted:
            return format_html(
                '<span style="color: #28a745;">✓ Encrypted</span> '
                '<span style="color: #6c757d; font-size: 0.9em;">(Key is encrypted at rest)</span>'
            )
        else:
            return format_html(
                '<span style="color: #ffc107;">⚠ Plain text</span> '
                '<span style="color: #6c757d; font-size: 0.9em;">(Should be encrypted)</span>'
            )
    api_key_status.short_description = 'API Key Status'
    
    def save_model(self, request, obj, form, change):
        """Override save to handle API key encryption."""
        # If api_key field was changed and is not empty, encrypt it
        if 'api_key' in form.changed_data and obj.api_key:
            # Check if it's already encrypted
            from .utils.encryption import is_encrypted
            if not is_encrypted(obj.api_key):
                # Encrypt the plain text key
                obj.set_api_key(obj.api_key)
        
        super().save_model(request, obj, form, change)

    # --------------------------------------------------
    # ACTIONS
    # --------------------------------------------------
    actions = ['enable_platforms', 'disable_platforms']

    def enable_platforms(self, request, queryset):
        updated = queryset.update(is_enabled=True, status='active')
        self.message_user(request, f'{updated} platform(s) enabled.')
    enable_platforms.short_description = 'Enable selected platforms'

    def disable_platforms(self, request, queryset):
        updated = queryset.update(is_enabled=False, status='inactive')
        self.message_user(request, f'{updated} platform(s) disabled.')
    disable_platforms.short_description = 'Disable selected platforms'


@admin.register(PlatformUsage)
class PlatformUsageAdmin(admin.ModelAdmin):
    """Admin interface for platform usage tracking."""
    
    list_display = [
        'timestamp',
        'platform_link',
        'user_link',
        'model',
        'tokens_used',
        'cost_display',
        'success_badge',
        'response_time_display',
    ]
    
    list_filter = [
        'platform__platform_name',
        'success',
        'timestamp',
    ]
    
    search_fields = [
        'platform__display_name',
        'user__email',
        'model',
    ]
    
    readonly_fields = [
        'id',
        'platform',
        'user',
        'model',
        'tokens_used',
        'cost',
        'success',
        'error_message',
        'response_time',
        'timestamp',
    ]
    
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('platform', 'user', 'model')
        }),
        ('Usage Metrics', {
            'fields': ('tokens_used', 'cost', 'response_time')
        }),
        ('Status', {
            'fields': ('success', 'error_message')
        }),
        ('Metadata', {
            'fields': ('id', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
    
    def platform_link(self, obj):
        """Link to platform."""
        return obj.platform.display_name
    platform_link.short_description = 'Platform'
    platform_link.admin_order_field = 'platform__display_name'
    
    def user_link(self, obj):
        """Link to user."""
        if obj.user:
            return obj.user.email
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__email'
    
    def cost_display(self, obj):
        """Display cost formatted."""
        cost = float(obj.cost) if obj.cost else 0.0
        # Return plain formatted string - no HTML needed
        return f"${cost:.6f}"
    cost_display.short_description = 'Cost'
    cost_display.admin_order_field = 'cost'
    
    def response_time_display(self, obj):
        """Display response time formatted."""
        time = float(obj.response_time) if obj.response_time else 0.0
        # Return plain formatted string - no HTML needed
        return f"{time:.2f}s"
    response_time_display.short_description = 'Response Time'
    response_time_display.admin_order_field = 'response_time'
    
    def success_badge(self, obj):
        """Display success status as badge."""
        if obj.success:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 10px; border-radius: 3px;">✓ Success</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; '
            'padding: 3px 10px; border-radius: 3px;">✗ Error</span>'
        )
    success_badge.short_description = 'Status'
    success_badge.admin_order_field = 'success'
    
    def has_add_permission(self, request):
        """Disable manual creation."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make read-only."""
        return False
