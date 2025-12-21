"""
Serializers for organizations app.
"""

from rest_framework import serializers
from .models import (
    Organization, 
    OrganizationMember,
    SubscriptionPlan,
    Feature,
    TierFeature,
    Subscription,
    BillingRecord,
    OrganizationUsage
)
from apps.core.services.roles import RoleService


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""
    
    member_count = serializers.SerializerMethodField()
    project_count = serializers.SerializerMethodField()
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'status',
            'owner',
            'owner_email',
            'owner_name',
            'subscription_tier',
            'max_users',
            'max_projects',
            'subscription_start_date',
            'subscription_end_date',
            'settings',
            'logo',
            'primary_color',
            'secondary_color',
            'member_count',
            'project_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at', 
            'member_count', 
            'project_count',
            'status',  # Derived from subscription, not editable by users
            'subscription_tier',  # Derived from subscription, not editable by users
            'max_users',  # Derived from subscription features, not editable by users
            'max_projects',  # Derived from subscription features, not editable by users
            'subscription_start_date',  # Set by subscription, not editable by users
            'subscription_end_date',  # Set by subscription, not editable by users
        ]
    
    def get_member_count(self, obj):
        """Get number of members in organization."""
        return obj.get_member_count()
    
    def get_project_count(self, obj):
        """Get number of projects in organization."""
        return obj.get_project_count()
    
    def get_owner_name(self, obj):
        """Get owner's full name."""
        if obj.owner:
            return obj.owner.get_full_name() or obj.owner.email
        return None


class OrganizationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating organizations."""
    
    class Meta:
        model = Organization
        fields = [
            'name',
            'slug',
            'description',
            'subscription_tier',
            'max_users',
            'max_projects',
        ]
    
    def validate_slug(self, value):
        """Validate slug is unique."""
        if Organization.objects.filter(slug=value).exists():
            raise serializers.ValidationError("An organization with this slug already exists.")
        return value
    
    def create(self, validated_data):
        """Create organization and set creator as owner and org_admin."""
        user = self.context['request'].user
        organization = Organization.objects.create(
            **validated_data,
            owner=user,
            created_by=user
        )
        
        # Create OrganizationMember with org_admin role
        OrganizationMember.objects.create(
            organization=organization,
            user=user,
            role='org_admin',
            invited_by=user
        )
        
        return organization


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationMember model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = [
            'id',
            'organization',
            'organization_name',
            'user',
            'user_email',
            'user_username',
            'user_first_name',
            'user_last_name',
            'role',
            'joined_at',
            'invited_by',
            'invited_by_email',
        ]
        read_only_fields = ['id', 'joined_at']
    
    def validate_role(self, value):
        """Validate role is a valid organization role."""
        if value not in OrganizationMember.ORG_ROLES:
            raise serializers.ValidationError(
                f"Invalid role. Must be one of: {', '.join(OrganizationMember.ORG_ROLES)}"
            )
        return value


class OrganizationMemberAddSerializer(serializers.Serializer):
    """Serializer for adding a member to an organization."""
    
    user_id = serializers.UUIDField()
    role = serializers.ChoiceField(
        choices=OrganizationMember.ORG_ROLES,
        default='org_member'
    )


class OrganizationMemberUpdateSerializer(serializers.Serializer):
    """Serializer for updating an organization member's role."""
    
    role = serializers.ChoiceField(choices=OrganizationMember.ORG_ROLES)


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for SubscriptionPlan model."""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'tier_code',
            'tier_name',
            'description',
            'monthly_price',
            'annual_price',
            'is_active',
            'display_order',
            'metadata',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeatureSerializer(serializers.ModelSerializer):
    """Serializer for Feature model."""
    
    class Meta:
        model = Feature
        fields = [
            'id',
            'code',
            'name',
            'category',
            'description',
            'feature_type',
            'default_value',
            'is_active',
            'is_deprecated',
            'deprecated_at',
            'metadata',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TierFeatureSerializer(serializers.ModelSerializer):
    """Serializer for TierFeature model."""
    
    feature = FeatureSerializer(read_only=True)
    feature_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = TierFeature
        fields = [
            'id',
            'tier_code',
            'feature',
            'feature_id',
            'value',
            'is_enabled',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model."""
    
    plan = SubscriptionPlanSerializer(read_only=True)
    plan_id = serializers.UUIDField(write_only=True, required=False)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    is_active_status = serializers.SerializerMethodField()
    is_expired_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id',
            'organization',
            'organization_name',
            'plan',
            'plan_id',
            'tier_code',
            'status',
            'billing_cycle',
            'started_at',
            'current_period_start',
            'current_period_end',
            'cancelled_at',
            'cancel_at_period_end',
            'stripe_subscription_id',
            'stripe_customer_id',
            'metadata',
            'is_active_status',
            'is_expired_status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_active_status(self, obj):
        """Check if subscription is currently active."""
        return obj.is_active()
    
    def get_is_expired_status(self, obj):
        """Check if subscription has expired."""
        return obj.is_expired()


class BillingRecordSerializer(serializers.ModelSerializer):
    """Serializer for BillingRecord model."""
    
    subscription = SubscriptionSerializer(read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = BillingRecord
        fields = [
            'id',
            'subscription',
            'organization',
            'organization_name',
            'amount',
            'currency',
            'status',
            'billing_type',
            'stripe_invoice_id',
            'stripe_payment_intent_id',
            'paid_at',
            'due_date',
            'metadata',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrganizationUsageSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationUsage model."""
    
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    usage_percentage = serializers.SerializerMethodField()
    is_over_limit = serializers.SerializerMethodField()
    
    class Meta:
        model = OrganizationUsage
        fields = [
            'id',
            'organization',
            'organization_name',
            'usage_type',
            'month',
            'year',
            'count',
            'limit_value',
            'warning_threshold',
            'warning_sent',
            'usage_percentage',
            'is_over_limit',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_usage_percentage(self, obj):
        """Calculate usage percentage if limit exists."""
        if obj.limit_value and obj.limit_value > 0:
            return min(100, int((obj.count / obj.limit_value) * 100))
        return None
    
    def get_is_over_limit(self, obj):
        """Check if usage is over limit."""
        if obj.limit_value is None:
            return False
        return obj.count > obj.limit_value


class FeatureAvailabilitySerializer(serializers.Serializer):
    """Serializer for feature availability check."""
    
    feature_code = serializers.CharField()
    is_available = serializers.BooleanField()
    limit = serializers.IntegerField(allow_null=True)
    current_usage = serializers.IntegerField(allow_null=True)
    tier_code = serializers.CharField()
    feature_name = serializers.CharField(allow_null=True)


class TierFeaturesListSerializer(serializers.Serializer):
    """Serializer for listing all features for a tier."""
    
    tier_code = serializers.CharField()
    features = serializers.DictField()


