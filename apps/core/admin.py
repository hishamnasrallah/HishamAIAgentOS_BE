"""
Django admin configuration for core app.
"""

from django.contrib import admin
from .models import SystemSettings, FeatureFlag


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """Admin interface for system settings."""
    
    list_display = ['key', 'value', 'value_type', 'category', 'is_public', 'updated_at']
    list_filter = ['category', 'value_type', 'is_public']
    search_fields = ['key', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('key', 'value', 'value_type', 'category', 'description')
        }),
        ('Access Control', {
            'fields': ('is_public',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'updated_by')
        }),
    )


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    """Admin interface for feature flags."""
    
    list_display = ['key', 'name', 'is_enabled', 'updated_at']
    list_filter = ['is_enabled']
    search_fields = ['key', 'name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('key', 'name', 'description', 'is_enabled')
        }),
        ('Access Control', {
            'fields': ('enabled_for_roles', 'enabled_for_users')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'updated_by')
        }),
    )

