"""
Organization services for status and subscription management.

This module provides reusable services for checking organization status,
subscription validity, and tier-based feature access.
Super admins can bypass all checks.
"""

from django.utils import timezone
from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from typing import Optional, Dict, List, Any
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
    """Service for checking subscription tier-based features and limits.
    
    NOTE: This service now uses FeatureService for all feature checks.
    All hardcoded tier limits have been removed in favor of database-driven features.
    """
    
    # Mapping from usage_type (used in OrganizationUsage) to feature_code (used in Feature table)
    # This maps the internal usage tracking type to the actual feature code in the database
    USAGE_TYPE_TO_FEATURE_CODE = {
        'agent_executions': 'ai.agent_executions',
        'workflow_executions': 'ai.workflow_executions',
        'chat_messages': 'ai.chat',
        'command_executions': 'ai.command_executions',
    }
    
    @classmethod
    def get_tier_limits(cls, tier: str) -> Dict:
        """
        Get all feature limits for a specific tier.
        
        DEPRECATED: This method is kept for backward compatibility but now uses FeatureService.
        Consider using FeatureService.get_features_for_tier() directly.
        
        Args:
            tier: Subscription tier (trial, basic, professional, enterprise)
            
        Returns:
            Dict mapping feature codes to their values
        """
        # Use FeatureService to get features dynamically from database
        return FeatureService.get_features_for_tier(tier)
    
    @classmethod
    def get_limit_for_feature(cls, tier: str, feature_code: str) -> Optional[int]:
        """
        Get the limit for a specific feature in a tier.
        
        DEPRECATED: Use FeatureService.get_feature_limit(organization, feature_code) instead.
        This method is kept for backward compatibility.
        
        Args:
            tier: Subscription tier (trial, basic, professional, enterprise)
            feature_code: Feature code (e.g., 'ai.agent_executions', 'users.max_count')
            
        Returns:
            int or None: Limit value, or None for unlimited
        """
        # Use FeatureService to get feature value dynamically
        features = FeatureService.get_features_for_tier(tier)
        if feature_code not in features:
            return None
        
        feature_data = features[feature_code]
        value = feature_data['value']
        
        # Return None for unlimited, int for limits
        if value is None:
            return None
        
        return int(value) if isinstance(value, (int, str)) else None
    
    @classmethod
    def is_unlimited(cls, tier: str, feature_code: str) -> bool:
        """Check if a feature is unlimited for a tier."""
        limit = cls.get_limit_for_feature(tier, feature_code)
        return limit is None
    
    @classmethod
    def allows_feature(cls, tier: str, feature_code: str) -> bool:
        """
        Check if a tier allows a specific feature.
        
        DEPRECATED: Use FeatureService.is_feature_available(organization, feature_code) instead.
        This method is kept for backward compatibility.
        
        Args:
            tier: Subscription tier
            feature_code: Feature code (e.g., 'ai.custom_agents', 'projects.templates')
            
        Returns:
            bool: True if feature is allowed (enabled)
        """
        # Use FeatureService to check feature availability
        features = FeatureService.get_features_for_tier(tier)
        if feature_code not in features:
            return False
        
        feature_data = features[feature_code]
        
        # For boolean features, check if value is True
        if feature_data['type'] == 'boolean':
            return feature_data['value'] is True
        
        # For count/usage features, feature exists means it's available
        # (limits checked separately)
        return True
    
    @classmethod
    def check_tier_feature(cls, organization, feature_code: str, user=None, raise_exception=True):
        """
        Check if organization's tier allows a specific feature.
        Super admins can bypass this check.
        
        DEPRECATED: Use FeatureService.is_feature_available(organization, feature_code, user, raise_exception) instead.
        This method is kept for backward compatibility.
        
        Args:
            organization: Organization instance
            feature_code: Feature code (e.g., 'ai.custom_agents', 'projects.templates')
            user: Optional user instance to check for super admin status
            raise_exception: If True, raise ValidationError if not allowed
            
        Returns:
            bool: True if feature is allowed or user is super admin, False otherwise
            
        Raises:
            ValidationError: If feature is not allowed and raise_exception=True
        """
        # Delegate to FeatureService
        return FeatureService.is_feature_available(organization, feature_code, user=user, raise_exception=raise_exception)
    
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
            usage_type: Type of usage ('agent_executions', 'workflow_executions', 'chat_messages', 'command_executions')
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
        
        # Map usage_type to actual feature_code using the mapping
        feature_code = cls.USAGE_TYPE_TO_FEATURE_CODE.get(usage_type)
        if not feature_code:
            # If no mapping exists, log warning and allow (for backward compatibility)
            logger.warning(
                f"[SubscriptionService] No feature code mapping for usage_type: {usage_type}. "
                f"Please add mapping to USAGE_TYPE_TO_FEATURE_CODE."
            )
            if raise_exception:
                raise ValidationError(
                    f'Usage tracking for "{usage_type}" is not configured. Please contact support.'
                )
            return False
        
        # Get limit from FeatureService using the actual feature code
        limit = FeatureService.get_feature_limit(organization, feature_code)
        
        # If limit is None, it's unlimited
        if limit is None:
            return True
        
        # Get current usage count
        current_usage = cls.get_usage_count(organization, usage_type)
        
        # Check if limit is reached
        if current_usage >= limit:
            if raise_exception:
                # Get feature name for better error message
                tier_code = organization.subscription_tier or 'trial'
                features = FeatureService.get_features_for_tier(tier_code)
                feature_name = features.get(feature_code, {}).get('name', usage_type.replace('_', ' ').title())
                
                raise ValidationError(
                    f'You have reached your monthly limit of {limit} {feature_name.lower()}. '
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


class FeatureService:
    """Service for managing features and tier-to-feature mappings."""
    
    CACHE_KEY_PREFIX = 'feature_matrix'
    CACHE_TTL = 300  # 5 minutes
    
    @classmethod
    def get_features_for_tier(cls, tier_code: str) -> Dict[str, Any]:
        """
        Get all features and their values for a tier.
        Uses caching for performance.
        
        Args:
            tier_code: Subscription tier code
            
        Returns:
            Dict mapping feature_code to feature_data
        """
        cache_key = f"{cls.CACHE_KEY_PREFIX}:tier:{tier_code}"
        
        # Try cache first
        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug(f"[FeatureService] Cache hit for tier: {tier_code}")
            return cached
        
        # Query database
        try:
            from apps.organizations.models import TierFeature, Feature
            
            tier_features = TierFeature.objects.filter(
                tier_code=tier_code,
                is_enabled=True
            ).select_related('feature').filter(
                feature__is_active=True,
                feature__is_deprecated=False
            )
            
            features_dict = {}
            for tf in tier_features:
                features_dict[tf.feature.code] = {
                    'value': tf.value,
                    'type': tf.feature.feature_type,
                    'name': tf.feature.name,
                    'category': tf.feature.category,
                    'description': tf.feature.description,
                }
            
            # Log projects.max_count value for debugging
            if 'projects.max_count' in features_dict:
                logger.info(f"[FeatureService] projects.max_count for tier {tier_code}: {features_dict['projects.max_count']['value']} (from DB)")
            
            # Cache result
            cache.set(cache_key, features_dict, cls.CACHE_TTL)
            logger.debug(f"[FeatureService] Cached features for tier: {tier_code}, count: {len(features_dict)}")
            
            return features_dict
        except Exception as e:
            logger.error(f"[FeatureService] Error getting features for tier {tier_code}: {e}", exc_info=True)
            # Fallback to hardcoded limits if database not available
            return {}
    
    @classmethod
    def is_feature_available(cls, organization, feature_code: str, user=None, raise_exception=False) -> bool:
        """
        Check if a feature is available for an organization.
        
        Args:
            organization: Organization instance
            feature_code: Feature code to check
            user: Optional user instance to check for super admin status
            raise_exception: If True, raise ValidationError if not available
            
        Returns:
            bool: True if feature is available or user is super admin, False otherwise
            
        Raises:
            ValidationError: If feature is not available and raise_exception=True
        """
        # Super admins can bypass all checks
        if user:
            from apps.core.services.roles import RoleService
            if RoleService.is_super_admin(user):
                return True
        
        if not organization:
            if raise_exception:
                from django.core.exceptions import ValidationError
                raise ValidationError('Organization is required.')
            return False
        
        # Get organization's tier
        tier_code = organization.subscription_tier or 'trial'
        
        # Get features for tier
        features = cls.get_features_for_tier(tier_code)
        
        # Check if feature exists and is enabled
        if feature_code not in features:
            if raise_exception:
                from django.core.exceptions import ValidationError
                tier_display = tier_code.title()
                raise ValidationError(
                    f'This feature ({feature_code}) is not available in the {tier_display} tier. '
                    f'Please upgrade your subscription.'
                )
            return False
        
        feature_data = features[feature_code]
        
        # For boolean features, check value
        is_available = False
        if feature_data['type'] == 'boolean':
            is_available = feature_data['value'] is True
        else:
            # For count/usage features, feature exists means it's available
            is_available = True
        
        if not is_available and raise_exception:
            from django.core.exceptions import ValidationError
            tier_display = tier_code.title()
            raise ValidationError(
                f'This feature ({feature_code}) is not available in the {tier_display} tier. '
                f'Please upgrade your subscription.'
            )
        
        return is_available
    
    @classmethod
    def get_feature_limit(cls, organization, feature_code: str) -> Optional[int]:
        """
        Get the limit value for a feature.
        
        Args:
            organization: Organization instance
            feature_code: Feature code
            
        Returns:
            int: Limit value, or None for unlimited
        """
        if not organization:
            return None
        
        tier_code = organization.subscription_tier or 'trial'
        features = cls.get_features_for_tier(tier_code)
        
        if feature_code not in features:
            return None
        
        feature_data = features[feature_code]
        value = feature_data['value']
        
        # Return None for unlimited, int for limits
        if value is None:
            return None
        
        return int(value) if isinstance(value, (int, str)) else None
    
    @classmethod
    def get_feature_value(cls, organization, feature_code: str, default: Any = None) -> Any:
        """
        Get the value for a feature.
        This is an alias for get_feature_limit() for consistency with SubscriptionService usage.
        
        Args:
            organization: Organization instance
            feature_code: Feature code
            default: Default value to return if feature not found or has no value
            
        Returns:
            Feature value (int for limits, bool for boolean features, None for unlimited)
        """
        if not organization:
            return default
        
        tier_code = organization.subscription_tier or 'trial'
        features = cls.get_features_for_tier(tier_code)
        
        if feature_code not in features:
            return default
        
        feature_data = features[feature_code]
        value = feature_data['value']
        
        # Return value, or default if None and default provided
        if value is None:
            return default if default is not None else None
        
        # For numeric features, return as int
        if feature_data['type'] in ['count', 'usage']:
            return int(value) if isinstance(value, (int, str)) else default
        
        # For boolean features, return as bool
        if feature_data['type'] == 'boolean':
            return bool(value)
        
        return value
    
    @classmethod
    def get_features_by_category(cls, tier_code: str, category: str) -> List[Dict]:
        """
        Get features for a tier filtered by category.
        
        Args:
            tier_code: Subscription tier code
            category: Feature category
            
        Returns:
            List of feature dictionaries
        """
        all_features = cls.get_features_for_tier(tier_code)
        
        return [
            {**data, 'code': code}
            for code, data in all_features.items()
            if data['category'] == category
        ]
    
    @classmethod
    def invalidate_cache(cls, tier_code: Optional[str] = None):
        """
        Invalidate feature cache for a tier or all tiers.
        
        Args:
            tier_code: Specific tier to invalidate, or None for all
        """
        if tier_code:
            cache_key = f"{cls.CACHE_KEY_PREFIX}:tier:{tier_code}"
            cache.delete(cache_key)
            logger.debug(f"[FeatureService] Invalidated cache for tier: {tier_code}")
        else:
            # Invalidate all tier caches
            tiers = ['trial', 'basic', 'professional', 'enterprise']
            for tier in tiers:
                cache_key = f"{cls.CACHE_KEY_PREFIX}:tier:{tier}"
                cache.delete(cache_key)
            logger.debug(f"[FeatureService] Invalidated cache for all tiers")
    
    @classmethod
    def check_feature_availability(cls, organization, feature_code: str, user=None, raise_exception=True):
        """
        Check if organization's tier allows a specific feature.
        Super admins can bypass this check.
        
        Args:
            organization: Organization instance
            feature_code: Feature code to check
            user: Optional user instance to check for super admin status
            raise_exception: If True, raise ValidationError if not allowed
            
        Returns:
            bool: True if feature is available or user is super admin, False otherwise
            
        Raises:
            ValidationError: If feature is not available and raise_exception=True
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
        
        if not cls.is_feature_available(organization, feature_code):
            if raise_exception:
                tier_display = (organization.subscription_tier or 'trial').title()
                feature_name = feature_code.replace('_', ' ').title()
                raise ValidationError(
                    f'Feature "{feature_name}" is not available in the {tier_display} tier. '
                    f'Please upgrade your subscription to access this feature.'
                )
            return False
        
        return True

