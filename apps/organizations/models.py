"""
Organization models for SaaS multi-tenancy support.

Organizations represent tenants in the SaaS system. Each organization:
- Has its own users, projects, and data
- Has organization-level admins
- Is isolated from other organizations
- Can have custom settings and configurations
"""

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid


class Organization(models.Model):
    """
    Organization (tenant) model for SaaS multi-tenancy.
    
    Each organization is a separate tenant with:
    - Its own users
    - Its own projects
    - Its own settings
    - Organization-level admins
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('trial', 'Trial'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic Information
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, db_index=True, 
                           validators=[RegexValidator(
                               regex=r'^[a-z0-9-]+$',
                               message='Slug can only contain lowercase letters, numbers, and hyphens'
                           )])
    description = models.TextField(blank=True, default='')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial', db_index=True)
    
    # Organization Owner (the user who created/manages the organization)
    # This is different from super admin - org owner is admin of their org
    owner = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_organizations',
        verbose_name='Organization Owner'
    )
    
    # Subscription & Billing
    subscription_tier = models.CharField(
        max_length=50,
        default='trial',
        help_text='Subscription tier: trial, basic, professional, enterprise (denormalized from active subscription)'
    )
    active_subscription = models.ForeignKey(
        'Subscription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_for_organization',
        help_text='Currently active subscription'
    )
    max_users = models.IntegerField(default=10, help_text='Maximum number of users allowed (denormalized from subscription)')
    max_projects = models.IntegerField(default=5, help_text='Maximum number of projects allowed (denormalized from subscription)')
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)
    
    # Settings
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text='Organization-specific settings and configurations'
    )
    
    # Branding
    logo = models.CharField(max_length=500, blank=True, help_text='URL or path to organization logo')
    primary_color = models.CharField(max_length=7, blank=True, default='#007bff', help_text='Primary brand color (hex)')
    secondary_color = models.CharField(max_length=7, blank=True, default='#6c757d', help_text='Secondary brand color (hex)')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_organizations',
        verbose_name='Created By'
    )
    
    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['owner']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_member_count(self):
        """Get total number of users in this organization."""
        return self.members.count()
    
    def get_project_count(self):
        """Get total number of projects in this organization."""
        return self.projects.count()
    
    def is_active(self):
        """Check if organization is active."""
        # Trial and active organizations are considered active
        # Suspended and cancelled are not active
        return self.status in ['active', 'trial']
    
    def can_add_user(self):
        """
        Check if organization can add more users.
        
        Uses FeatureService for real-time feature value checking.
        Falls back to denormalized max_users field if FeatureService fails.
        """
        from apps.organizations.services import FeatureService
        try:
            max_users = FeatureService.get_feature_value(self, 'users.max_count', default=None)
            if max_users is None:
                return True  # Unlimited
            return self.get_member_count() < max_users
        except Exception:
            # Fallback to denormalized field if FeatureService fails
            if self.max_users is None or self.max_users <= 0:
                return True  # Unlimited
            return self.get_member_count() < self.max_users
    
    def can_add_project(self):
        """
        Check if organization can add more projects.
        
        Uses FeatureService for real-time feature value checking.
        Falls back to denormalized max_projects field if FeatureService fails.
        """
        from apps.organizations.services import FeatureService
        try:
            max_projects = FeatureService.get_feature_value(self, 'projects.max_count', default=None)
            if max_projects is None:
                return True  # Unlimited
            return self.get_project_count() < max_projects
        except Exception:
            # Fallback to denormalized field if FeatureService fails
            if self.max_projects is None or self.max_projects <= 0:
                return True  # Unlimited
            return self.get_project_count() < self.max_projects
    
    def is_subscription_active(self):
        """Check if subscription is currently active."""
        # First check active_subscription if available
        if self.active_subscription:
            return self.active_subscription.is_active()
        # Fallback to subscription_end_date for backward compatibility
        if not self.subscription_end_date:
            return True
        return timezone.now().date() <= self.subscription_end_date
    
    def get_active_subscription(self):
        """Get the currently active subscription, if any."""
        if self.active_subscription and self.active_subscription.is_active():
            return self.active_subscription
        # Try to find active subscription
        return self.subscriptions.filter(status='active').first()
    
    def refresh_limits_from_features(self):
        """
        Refresh max_users and max_projects from FeatureService.
        Should be called when subscription changes.
        """
        from apps.organizations.services import FeatureService
        try:
            max_users = FeatureService.get_feature_value(self, 'users.max_count', default=None)
            max_projects = FeatureService.get_feature_value(self, 'projects.max_count', default=None)
            
            # Only update if we got valid values (not None for unlimited)
            if max_users is not None:
                self.max_users = max_users
            if max_projects is not None:
                self.max_projects = max_projects
            
            # Save only the fields that changed
            update_fields = []
            if max_users is not None:
                update_fields.append('max_users')
            if max_projects is not None:
                update_fields.append('max_projects')
            
            if update_fields:
                self.save(update_fields=update_fields)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to refresh limits from features for org {self.id}: {e}")


class OrganizationMember(models.Model):
    """
    Organization membership with roles.
    
    Tracks which users belong to which organizations and their roles within the organization.
    This is separate from project-specific roles (ProjectMember).
    """
    
    # Organization-level roles
    ORG_ROLES = [
        'org_admin',      # Organization administrator
        'org_member',     # Regular organization member
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members',
        db_index=True
    )
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='organization_memberships',
        db_index=True
    )
    role = models.CharField(
        max_length=50,
        default='org_member',
        help_text='Role in the organization: org_admin or org_member'
    )
    
    # Metadata
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_organization_members',
        verbose_name='Invited By'
    )
    
    class Meta:
        db_table = 'organization_members'
        verbose_name = 'Organization Member'
        verbose_name_plural = 'Organization Members'
        unique_together = [['organization', 'user']]
        indexes = [
            models.Index(fields=['organization', 'user']),
            models.Index(fields=['organization']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f'{self.user.email} in {self.organization.name} ({self.role})'
    
    def is_org_admin(self):
        """Check if member is organization admin."""
        return self.role == 'org_admin'


class OrganizationUsage(models.Model):
    """
    Track monthly usage of organization resources.
    
    Used to enforce subscription tier limits on features like:
    - Agent executions
    - Workflow executions
    - Chat messages
    - Command executions
    """
    
    USAGE_TYPE_CHOICES = [
        ('agent_executions', 'Agent Executions'),
        ('workflow_executions', 'Workflow Executions'),
        ('chat_messages', 'Chat Messages'),
        ('command_executions', 'Command Executions'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='usage_records',
        db_index=True
    )
    usage_type = models.CharField(max_length=50, choices=USAGE_TYPE_CHOICES, db_index=True)
    month = models.IntegerField(help_text='Month (1-12)')
    year = models.IntegerField(help_text='Year (e.g., 2025)')
    count = models.IntegerField(default=0, help_text='Usage count for this month')
    limit_value = models.IntegerField(
        null=True,
        blank=True,
        help_text='Limit value for this month (denormalized from subscription tier)'
    )
    warning_threshold = models.IntegerField(
        null=True,
        blank=True,
        help_text='Warning threshold (typically 80% of limit)'
    )
    warning_sent = models.BooleanField(
        default=False,
        help_text='Whether usage warning email has been sent'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organization_usage'
        verbose_name = 'Organization Usage'
        verbose_name_plural = 'Organization Usage Records'
        unique_together = [['organization', 'usage_type', 'month', 'year']]
        indexes = [
            models.Index(fields=['organization', 'usage_type', 'month', 'year']),
            models.Index(fields=['organization', 'usage_type']),
            models.Index(fields=['month', 'year']),
            models.Index(fields=['organization', 'usage_type', 'warning_sent']),
        ]
    
    def __str__(self):
        return f'{self.organization.name} - {self.get_usage_type_display()} - {self.year}-{self.month:02d}: {self.count}'


class SubscriptionPlan(models.Model):
    """
    Subscription plan definitions.
    
    Defines available subscription tiers and their pricing.
    """
    
    TIER_CHOICES = [
        ('trial', 'Trial'),
        ('basic', 'Basic'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tier_code = models.CharField(
        max_length=50,
        unique=True,
        choices=TIER_CHOICES,
        db_index=True,
        help_text='Subscription tier code'
    )
    tier_name = models.CharField(max_length=100, help_text='Display name for the tier')
    description = models.TextField(blank=True, default='')
    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Monthly subscription price in USD'
    )
    annual_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Annual subscription price in USD'
    )
    is_active = models.BooleanField(default=True, db_index=True, help_text='Whether this plan is currently available')
    display_order = models.IntegerField(default=0, help_text='Order for display in UI')
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional plan metadata'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscription_plans'
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['display_order', 'tier_code']
        indexes = [
            models.Index(fields=['tier_code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['display_order']),
        ]
    
    def __str__(self):
        return f'{self.tier_name} ({self.tier_code})'


class Feature(models.Model):
    """
    Feature definitions.
    
    Defines all available features in the system that can be gated by subscription tier.
    """
    
    FEATURE_TYPE_CHOICES = [
        ('boolean', 'Boolean'),
        ('count', 'Count Limit'),
        ('usage', 'Usage Limit'),
        ('unlimited', 'Unlimited'),
    ]
    
    CATEGORY_CHOICES = [
        ('users', 'User Management'),
        ('projects', 'Project Management'),
        ('ai', 'AI & Automation'),
        ('integrations', 'Integrations'),
        ('analytics', 'Analytics & Reporting'),
        ('support', 'Support & Collaboration'),
        ('security', 'Security & Compliance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text='Unique feature code (e.g., "ai.custom_agents")'
    )
    name = models.CharField(max_length=200, help_text='Display name for the feature')
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        db_index=True,
        help_text='Feature category'
    )
    description = models.TextField(blank=True, default='')
    feature_type = models.CharField(
        max_length=20,
        choices=FEATURE_TYPE_CHOICES,
        help_text='Type of feature: boolean, count, usage, or unlimited'
    )
    default_value = models.JSONField(
        default=dict,
        blank=True,
        help_text='Default value for this feature'
    )
    is_active = models.BooleanField(default=True, db_index=True)
    is_deprecated = models.BooleanField(default=False, help_text='Whether this feature is deprecated')
    deprecated_at = models.DateTimeField(null=True, blank=True, help_text='When feature was deprecated')
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional feature metadata'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'features'
        verbose_name = 'Feature'
        verbose_name_plural = 'Features'
        ordering = ['category', 'code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['feature_type']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.code})'


class TierFeature(models.Model):
    """
    Tier-to-feature mapping.
    
    Maps features to subscription tiers with their specific values.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tier_code = models.CharField(
        max_length=50,
        db_index=True,
        help_text='Subscription tier code'
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name='tier_mappings',
        db_index=True
    )
    value = models.JSONField(
        null=True,
        blank=True,
        help_text='Feature value for this tier (boolean, number, or null for unlimited)'
    )
    is_enabled = models.BooleanField(default=True, help_text='Whether this feature is enabled for this tier')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tier_features'
        verbose_name = 'Tier Feature'
        verbose_name_plural = 'Tier Features'
        unique_together = [['tier_code', 'feature']]
        indexes = [
            models.Index(fields=['tier_code', 'feature']),
            models.Index(fields=['tier_code']),
            models.Index(fields=['feature']),
        ]
    
    def __str__(self):
        return f'{self.tier_code} - {self.feature.code}'


class Subscription(models.Model):
    """
    Active subscriptions for organizations.
    
    Tracks the current subscription status and billing information for each organization.
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        db_index=True
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        help_text='Subscription plan'
    )
    tier_code = models.CharField(
        max_length=50,
        db_index=True,
        help_text='Current tier code (denormalized from plan)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,
        help_text='Subscription status'
    )
    billing_cycle = models.CharField(
        max_length=20,
        choices=BILLING_CYCLE_CHOICES,
        default='monthly',
        help_text='Billing cycle'
    )
    started_at = models.DateTimeField(help_text='When subscription started')
    current_period_start = models.DateTimeField(help_text='Current billing period start')
    current_period_end = models.DateTimeField(help_text='Current billing period end')
    cancelled_at = models.DateTimeField(null=True, blank=True, help_text='When subscription was cancelled')
    cancel_at_period_end = models.BooleanField(
        default=False,
        help_text='Whether to cancel at period end'
    )
    stripe_subscription_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        help_text='Stripe subscription ID'
    )
    stripe_customer_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text='Stripe customer ID'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional subscription metadata'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['tier_code']),
            models.Index(fields=['stripe_subscription_id']),
            models.Index(fields=['current_period_end']),
        ]
    
    def __str__(self):
        return f'{self.organization.name} - {self.tier_code} ({self.status})'
    
    def is_active(self):
        """Check if subscription is currently active."""
        return self.status == 'active' and timezone.now() <= self.current_period_end
    
    def is_expired(self):
        """Check if subscription has expired."""
        return self.current_period_end < timezone.now()


class BillingRecord(models.Model):
    """
    Billing and payment records.
    
    Tracks all billing transactions and payment history.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    BILLING_TYPE_CHOICES = [
        ('subscription', 'Subscription'),
        ('upgrade', 'Upgrade'),
        ('downgrade', 'Downgrade'),
        ('refund', 'Refund'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='billing_records',
        db_index=True
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='billing_records',
        db_index=True
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Billing amount'
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text='Currency code'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text='Payment status'
    )
    billing_type = models.CharField(
        max_length=20,
        choices=BILLING_TYPE_CHOICES,
        help_text='Type of billing transaction'
    )
    stripe_invoice_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        help_text='Stripe invoice ID'
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text='Stripe payment intent ID'
    )
    paid_at = models.DateTimeField(null=True, blank=True, help_text='When payment was completed')
    due_date = models.DateTimeField(null=True, blank=True, help_text='Payment due date')
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional billing metadata'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'billing_records'
        verbose_name = 'Billing Record'
        verbose_name_plural = 'Billing Records'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subscription', 'status']),
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['stripe_invoice_id']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f'{self.organization.name} - {self.amount} {self.currency} ({self.status})'


