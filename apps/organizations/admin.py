"""
Django admin configuration for organizations app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Organization, OrganizationMember


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Organization admin."""
    
    list_display = (
        'name',
        'slug',
        'status_badge',
        'owner',
        'subscription_tier',
        'member_count_display',
        'project_count_display',
        'created_at'
    )
    list_filter = ('status', 'subscription_tier', 'created_at')
    search_fields = ('name', 'slug', 'owner__email', 'owner__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'status')
        }),
        ('Owner', {
            'fields': ('owner',)
        }),
        ('Subscription', {
            'fields': (
                'subscription_tier',
                'max_users',
                'max_projects',
                'subscription_start_date',
                'subscription_end_date',
            )
        }),
        ('Branding', {
            'fields': ('logo', 'primary_color', 'secondary_color')
        }),
        ('Settings', {
            'fields': ('settings',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'active': '#28a745',
            'suspended': '#dc3545',
            'trial': '#ffc107',
            'cancelled': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def member_count_display(self, obj):
        """Display member count."""
        count = obj.get_member_count()
        max_count = obj.max_users
        return f'{count} / {max_count}'
    member_count_display.short_description = 'Members'
    
    def project_count_display(self, obj):
        """Display project count."""
        count = obj.get_project_count()
        max_count = obj.max_projects
        return f'{count} / {max_count}'
    project_count_display.short_description = 'Projects'


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    """OrganizationMember admin."""
    
    list_display = ('user', 'organization', 'role_badge', 'invited_by', 'joined_at')
    list_filter = ('organization', 'role', 'joined_at')
    search_fields = ('user__email', 'user__username', 'organization__name')
    readonly_fields = ('id', 'joined_at')
    ordering = ('-joined_at',)
    
    def role_badge(self, obj):
        """Display role as colored badge."""
        colors = {
            'org_admin': '#dc3545',
            'org_member': '#007bff',
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.role.replace('_', ' ').title()
        )
    role_badge.short_description = 'Role'

