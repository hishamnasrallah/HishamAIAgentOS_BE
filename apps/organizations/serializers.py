"""
Serializers for organizations app.
"""

from rest_framework import serializers
from .models import Organization, OrganizationMember
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
        read_only_fields = ['id', 'created_at', 'updated_at', 'member_count', 'project_count']
    
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


