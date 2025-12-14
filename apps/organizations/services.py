"""
Organization services for status and subscription management.

This module provides reusable services for checking organization status,
subscription validity, and tier-based feature access.
Super admins can bypass all checks.
"""

from django.utils import timezone
from rest_framework.exceptions import ValidationError
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class OrganizationStatusService:
    """Service for checking organization status and subscription validity."""
    
    @staticmethod
    def require_active_organization(organization, user=None, raise_exception=True):
        """
        Check if organization is active.
        Super admins can bypass this check.
        
        Args:
            organization: Organization instance
            user: Optional user instance to check for super admin status
            raise_exception: If True, raise ValidationError if not active
            
        Returns:
            bool: True if active or user is super admin, False otherwise
            
        Raises:
            ValidationError: If organization is not active and raise_exception=True
        """
        # Super admins can bypass all checks
        if user:
            from apps.core.services.roles import RoleService
            if RoleService.is_super_admin(user):
                return True
        
        if not organization:
            if raise_exception:
                raise ValidationError('Organization is required.')
            return False
        
        if not organization.is_active():
            if raise_exception:
                status_display = organization.get_status_display() if hasattr(organization, 'get_status_display') else organization.status
                raise ValidationError(f'Cannot perform this action. Organization "{organization.name}" is {status_display}.')
            return False
        
        return True
    
    @staticmethod
    def require_subscription_active(organization, user=None, raise_exception=True):
        """
        Check if organization subscription is active.
        Super admins can bypass this check.
        
        Args:
            organization: Organization instance
            user: Optional user instance to check for super admin status
            raise_exception: If True, raise ValidationError if subscription expired
            
        Returns:
            bool: True if subscription is active or user is super admin, False otherwise
            
        Raises:
            ValidationError: If subscription is expired and raise_exception=True
        """
        # Super admins can bypass all checks
        if user:
            from apps.core.services.roles import RoleService
            if RoleService.is_super_admin(user):
                return True
        
        if not organization:
            if raise_exception:
                raise ValidationError('Organization is required.')
            return False
        
        if not organization.is_subscription_active():
            if raise_exception:
                raise ValidationError('Cannot perform this action. Organization subscription has expired.')
            return False
        
        return True
    
    @staticmethod
    def require_active_organization_and_subscription(organization, user=None, raise_exception=True):
        """
        Check both organization status and subscription validity.
        Super admins can bypass all checks.
        
        Args:
            organization: Organization instance
            user: Optional user instance to check for super admin status
            raise_exception: If True, raise ValidationError if checks fail
            
        Returns:
            bool: True if both checks pass or user is super admin, False otherwise
            
        Raises:
            ValidationError: If any check fails and raise_exception=True
        """
        OrganizationStatusService.require_active_organization(organization, user, raise_exception)
        OrganizationStatusService.require_subscription_active(organization, user, raise_exception)
        return True


class SubscriptionService:
    """Service for checking subscription tier-based features and limits."""
    
    # Tier definitions with limits
    TIER_LIMITS = {
        'trial': {
            'max_users': 3,
            'max_projects': 1,
            'max_agent_executions_per_month': 10,
            'max_workflow_executions_per_month': 5,
            'max_chat_messages_per_month': 50,
            'max_command_executions_per_month': 20,
            'max_api_keys': 1,
            'max_integrations': 0,
            'allows_custom_agents': False,
            'allows_custom_workflows': False,
        },
        'basic': {
            'max_users': 10,
            'max_projects': 5,
            'max_agent_executions_per_month': 100,
            'max_workflow_executions_per_month': 50,
            'max_chat_messages_per_month': 500,
            'max_command_executions_per_month': 200,
            'max_api_keys': 3,
            'max_integrations': 1,
            'allows_custom_agents': False,
            'allows_custom_workflows': False,
        },
        'professional': {
            'max_users': 50,
            'max_projects': 20,
            'max_agent_executions_per_month': 1000,
            'max_workflow_executions_per_month': 500,
            'max_chat_messages_per_month': 5000,
            'max_command_executions_per_month': 2000,
            'max_api_keys': 10,
            'max_integrations': 5,
            'allows_custom_agents': True,
            'allows_custom_workflows': True,
        },
        'enterprise': {
            'max_users': None,  # Unlimited
            'max_projects': None,  # Unlimited
            'max_agent_executions_per_month': None,  # Unlimited
            'max_workflow_executions_per_month': None,  # Unlimited
            'max_chat_messages_per_month': None,  # Unlimited
            'max_command_executions_per_month': None,  # Unlimited
            'max_api_keys': None,  # Unlimited
            'max_integrations': None,  # Unlimited
            'allows_custom_agents': True,
            'allows_custom_workflows': True,
        },
    }
    
    @classmethod
    def get_tier_limits(cls, tier: str) -> Dict:
        """Get limits for a specific tier."""
        return cls.TIER_LIMITS.get(tier, cls.TIER_LIMITS['trial'])
    
    @classmethod
    def get_limit_for_feature(cls, tier: str, feature: str) -> Optional[int]:
        """
        Get the limit for a specific feature in a tier.
        
        Args:
            tier: Subscription tier (trial, basic, professional, enterprise)
            feature: Feature name (e.g., 'max_agent_executions_per_month')
            
        Returns:
            int or None: Limit value, or None for unlimited
        """
        limits = cls.get_tier_limits(tier)
        return limits.get(feature)
    
    @classmethod
    def is_unlimited(cls, tier: str, feature: str) -> bool:
        """Check if a feature is unlimited for a tier."""
        limit = cls.get_limit_for_feature(tier, feature)
        return limit is None
    
    @classmethod
    def allows_feature(cls, tier: str, feature: str) -> bool:
        """
        Check if a tier allows a specific feature.
        
        Args:
            tier: Subscription tier
            feature: Feature name (e.g., 'allows_custom_agents')
            
        Returns:
            bool: True if feature is allowed
        """
        limits = cls.get_tier_limits(tier)
        return limits.get(feature, False)
    
    @classmethod
    def check_tier_feature(cls, organization, feature: str, user=None, raise_exception=True):
        """
        Check if organization's tier allows a specific feature.
        Super admins can bypass this check.
        
        Args:
            organization: Organization instance
            feature: Feature name (e.g., 'allows_custom_agents')
            user: Optional user instance to check for super admin status
            raise_exception: If True, raise ValidationError if not allowed
            
        Returns:
            bool: True if feature is allowed or user is super admin, False otherwise
            
        Raises:
            ValidationError: If feature is not allowed and raise_exception=True
        """
        # Super admins can bypass all checks
        if user:
            from apps.core.services.roles import RoleService
            if RoleService.is_super_admin(user):
                return True
        
        if not organization:
            if raise_exception:
                raise ValidationError('Organization is required.')
            return False
        
        tier = organization.subscription_tier or 'trial'
        if not cls.allows_feature(tier, feature):
            if raise_exception:
                tier_display = tier.title()
                raise ValidationError(f'This feature is not available in the {tier_display} tier. Please upgrade to Professional or Enterprise.')
            return False
        
        return True
    
    @classmethod
    def get_usage_count(cls, organization, usage_type: str, month: Optional[int] = None, year: Optional[int] = None):
        """
        Get usage count for a specific feature in the current or specified month.
        
        Args:
            organization: Organization instance
            usage_type: Type of usage ('agent_executions', 'workflow_executions', 'chat_messages', 'command_executions')
            month: Month number (1-12), defaults to current month
            year: Year, defaults to current year
            
        Returns:
            int: Usage count for the period
        """
        from apps.organizations.models import OrganizationUsage
        
        if month is None:
            month = timezone.now().month
        if year is None:
            year = timezone.now().year
        
        try:
            usage = OrganizationUsage.objects.get(
                organization=organization,
                usage_type=usage_type,
                month=month,
                year=year
            )
            return usage.count
        except OrganizationUsage.DoesNotExist:
            return 0
    
    @classmethod
    def check_usage_limit(cls, organization, usage_type: str, user=None, raise_exception=True):
        """
        Check if organization has reached usage limit for a feature.
        Super admins can bypass this check.
        
        Args:
            organization: Organization instance
            usage_type: Type of usage ('agent_executions', 'workflow_executions', etc.)
            user: Optional user instance to check for super admin status
            raise_exception: If True, raise ValidationError if limit reached
            
        Returns:
            bool: True if under limit or user is super admin, False if limit reached
            
        Raises:
            ValidationError: If limit reached and raise_exception=True
        """
        # Super admins can bypass all checks
        if user:
            from apps.core.services.roles import RoleService
            if RoleService.is_super_admin(user):
                return True
        
        if not organization:
            if raise_exception:
                raise ValidationError('Organization is required.')
            return False
        
        tier = organization.subscription_tier or 'trial'
        feature_key = f'max_{usage_type}_per_month'
        limit = cls.get_limit_for_feature(tier, feature_key)
        
        # Enterprise tier has unlimited usage
        if limit is None:
            return True
        
        current_usage = cls.get_usage_count(organization, usage_type)
        
        if current_usage >= limit:
            if raise_exception:
                raise ValidationError(
                    f'You have reached your monthly limit of {limit} {usage_type.replace("_", " ")}. '
                    f'Current usage: {current_usage}/{limit}. Please upgrade your subscription or wait until next month.'
                )
            return False
        
        return True
    
    @classmethod
    def increment_usage(cls, organization, usage_type: str):
        """
        Increment usage count for a feature.
        
        Args:
            organization: Organization instance
            usage_type: Type of usage ('agent_executions', 'workflow_executions', etc.)
        """
        from apps.organizations.models import OrganizationUsage
        
        now = timezone.now()
        month = now.month
        year = now.year
        
        usage, created = OrganizationUsage.objects.get_or_create(
            organization=organization,
            usage_type=usage_type,
            month=month,
            year=year,
            defaults={'count': 0}
        )
        
        usage.count += 1
        usage.save(update_fields=['count'])

