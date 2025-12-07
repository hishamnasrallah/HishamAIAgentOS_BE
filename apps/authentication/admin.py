"""
Django admin configuration for authentication app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, APIKey


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin."""
    
    list_display = ('email', 'username', 'role', 'is_active', 'is_staff', 'two_factor_enabled', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'role', 'two_factor_enabled')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'avatar', 'bio')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('2FA', {
            'fields': ('two_factor_enabled', 'two_factor_secret')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'timezone', 'notification_preferences')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """API Key admin."""
    
    list_display = (
        'name',
        'user',
        'is_active_badge',
        'expired_status',
        'created_at',
        'expires_at',
        'last_used_at'
    )
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('name', 'user__email', 'user__username', 'key')
    readonly_fields = ('id', 'key', 'created_at', 'last_used_at', 'expired_status')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'key', 'is_active')
        }),
        ('Expiration', {
            'fields': ('expires_at', 'expired_status')
        }),
        ('Rate Limiting', {
            'fields': ('rate_limit_per_minute',)
        }),
        ('Usage', {
            'fields': ('last_used_at', 'created_at')
        }),
        ('Metadata', {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_keys', 'deactivate_keys', 'regenerate_keys']
    
    def is_active_badge(self, obj):
        """Display active status as badge."""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; '
                'padding: 3px 8px; border-radius: 4px;">Active</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; '
            'padding: 3px 8px; border-radius: 4px;">Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    is_active_badge.admin_order_field = 'is_active'
    
    def expired_status(self, obj):
        """Display expiration status."""
        if obj.is_expired():
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">Expired</span>'
            )
        if obj.expires_at:
            return format_html(
                '<span style="color: #28a745;">Valid</span>'
            )
        return format_html('<span style="color: #6c757d;">No expiration</span>')
    expired_status.short_description = 'Expiration'
    
    def activate_keys(self, request, queryset):
        """Activate selected API keys."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} API key(s) activated.')
    activate_keys.short_description = 'Activate selected keys'
    
    def deactivate_keys(self, request, queryset):
        """Deactivate selected API keys."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} API key(s) deactivated.')
    deactivate_keys.short_description = 'Deactivate selected keys'
    
    def regenerate_keys(self, request, queryset):
        """Regenerate selected API keys (placeholder)."""
        self.message_user(
            request,
            f'Regeneration functionality for {queryset.count()} key(s) - to be implemented via API.'
        )
    regenerate_keys.short_description = 'Regenerate selected keys (API)'
