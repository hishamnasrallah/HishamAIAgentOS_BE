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
        help_text='Subscription tier: trial, basic, professional, enterprise'
    )
    max_users = models.IntegerField(default=10, help_text='Maximum number of users allowed')
    max_projects = models.IntegerField(default=5, help_text='Maximum number of projects allowed')
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
        return self.status == 'active'
    
    def can_add_user(self):
        """Check if organization can add more users."""
        return self.get_member_count() < self.max_users
    
    def can_add_project(self):
        """Check if organization can add more projects."""
        return self.get_project_count() < self.max_projects
    
    def is_subscription_active(self):
        """Check if subscription is currently active."""
        if not self.subscription_end_date:
            return True
        return timezone.now().date() <= self.subscription_end_date


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
        ]
    
    def __str__(self):
        return f'{self.organization.name} - {self.get_usage_type_display()} - {self.year}-{self.month:02d}: {self.count}'


