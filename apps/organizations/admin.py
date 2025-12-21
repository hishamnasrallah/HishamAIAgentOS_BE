"""
Django admin configuration for organizations app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Organization, 
    OrganizationMember, 
    OrganizationUsage,
    SubscriptionPlan,
    Feature,
    TierFeature,
    Subscription,
    BillingRecord
)


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


@admin.register(OrganizationUsage)
class OrganizationUsageAdmin(admin.ModelAdmin):
    """OrganizationUsage admin."""
    
    list_display = ('organization', 'usage_type', 'month', 'year', 'count', 'limit_value', 'warning_sent', 'created_at')
    list_filter = ('usage_type', 'year', 'month', 'warning_sent')
    search_fields = ('organization__name',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-year', '-month', 'organization')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organization')


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """SubscriptionPlan admin."""
    
    list_display = ('tier_name', 'tier_code', 'monthly_price', 'annual_price', 'is_active', 'display_order', 'created_at')
    list_filter = ('is_active', 'tier_code')
    search_fields = ('tier_name', 'tier_code', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('display_order', 'tier_code')


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    """Feature admin."""
    
    list_display = ('name', 'code', 'category', 'feature_type', 'is_active', 'is_deprecated', 'created_at')
    list_filter = ('category', 'feature_type', 'is_active', 'is_deprecated')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('category', 'code')


@admin.register(TierFeature)
class TierFeatureAdmin(admin.ModelAdmin):
    """TierFeature admin."""
    
    list_display = ('tier_code', 'feature', 'value_display', 'is_enabled', 'created_at')
    list_filter = ('tier_code', 'is_enabled', 'feature__category')
    search_fields = ('tier_code', 'feature__name', 'feature__code')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('tier_code', 'feature__category', 'feature__code')
    
    def value_display(self, obj):
        """Display value in readable format."""
        if obj.value is None:
            return 'Unlimited'
        return str(obj.value)
    value_display.short_description = 'Value'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Subscription admin."""
    
    list_display = (
        'organization', 
        'tier_code', 
        'status_badge', 
        'billing_cycle',
        'current_period_start',
        'current_period_end',
        'created_at'
    )
    list_filter = ('status', 'tier_code', 'billing_cycle')
    search_fields = ('organization__name', 'stripe_subscription_id', 'stripe_customer_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Organization', {
            'fields': ('organization', 'plan', 'tier_code')
        }),
        ('Status', {
            'fields': ('status', 'billing_cycle')
        }),
        ('Billing Period', {
            'fields': ('started_at', 'current_period_start', 'current_period_end')
        }),
        ('Cancellation', {
            'fields': ('cancelled_at', 'cancel_at_period_end'),
            'classes': ('collapse',)
        }),
        ('Stripe', {
            'fields': ('stripe_subscription_id', 'stripe_customer_id'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'active': '#28a745',
            'suspended': '#dc3545',
            'cancelled': '#6c757d',
            'expired': '#ffc107',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(BillingRecord)
class BillingRecordAdmin(admin.ModelAdmin):
    """BillingRecord admin."""
    
    list_display = (
        'organization',
        'billing_type',
        'amount',
        'currency',
        'status_badge',
        'paid_at',
        'due_date',
        'created_at'
    )
    list_filter = ('status', 'billing_type', 'currency')
    search_fields = ('organization__name', 'stripe_invoice_id', 'stripe_payment_intent_id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'paid': '#28a745',
            'pending': '#ffc107',
            'failed': '#dc3545',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

