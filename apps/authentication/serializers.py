"""
Serializers for authentication app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import APIKey
from apps.core.services.roles import RoleService

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""
    
    avatar_url = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'avatar', 'avatar_url', 'initials', 'bio',
            'is_active', 'is_superuser', 'two_factor_enabled', 'preferred_language', 'timezone',
            'date_joined', 'last_login', 'notification_preferences', 'organization'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'avatar_url', 'initials', 'full_name', 'is_superuser']
    
    def validate_role(self, value):
        """Validate role using RoleService."""
        if not RoleService.is_valid_role(value):
            valid_roles = RoleService.get_all_system_roles()
            raise serializers.ValidationError(
                f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        return value
    
    def get_avatar_url(self, obj):
        """Get avatar URL with fallback to initials."""
        if obj.avatar:
            # If avatar is a full URL, return it
            if obj.avatar.startswith('http://') or obj.avatar.startswith('https://'):
                return obj.avatar
            # If avatar is a relative path, construct full URL
            from django.conf import settings
            from django.contrib.staticfiles.storage import staticfiles_storage
            try:
                return staticfiles_storage.url(obj.avatar)
            except:
                return obj.avatar
        return None
    
    def get_initials(self, obj):
        """Generate user initials for avatar fallback."""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name[0]}{obj.last_name[0]}".upper()
        elif obj.first_name:
            return obj.first_name[0].upper()
        elif obj.last_name:
            return obj.last_name[0].upper()
        elif obj.username:
            return obj.username[0].upper()
        elif obj.email:
            return obj.email[0].upper()
        return "?"
    
    def get_full_name(self, obj):
        """Get user's full name."""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.first_name:
            return obj.first_name
        elif obj.last_name:
            return obj.last_name
        return obj.username or obj.email


class UserCreateSerializer(serializers.ModelSerializer):
    """User creation serializer."""
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 'password', 'password_confirm',
            'role', 'preferred_language', 'timezone'
        ]
    
    def validate_role(self, value):
        """Validate role using RoleService."""
        if not RoleService.is_valid_role(value):
            valid_roles = RoleService.get_all_system_roles()
            raise serializers.ValidationError(
                f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        
        # Additional validation for org_admin restrictions
        request = self.context.get('request')
        if request and request.user:
            # Check if current user is org_admin (not super_admin)
            is_super_admin = RoleService.is_super_admin(request.user)
            is_org_admin = RoleService.is_org_admin(request.user) and not is_super_admin
            
            if is_org_admin:
                # Org admins cannot create superusers
                # Note: is_superuser is not in fields, but check anyway
                if 'is_superuser' in attrs and attrs.get('is_superuser'):
                    raise serializers.ValidationError({
                        'is_superuser': 'Organization admins cannot create superusers.'
                    })
                
                # Org admins can only assign users to their organization
                # Organization will be set automatically from request context
                pass  # Organization assignment is handled in create() method
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        # Enforce org_admin restrictions
        request = self.context.get('request')
        organization = validated_data.get('organization')
        
        if request and request.user:
            is_super_admin = RoleService.is_super_admin(request.user)
            is_org_admin = RoleService.is_org_admin(request.user) and not is_super_admin
            
            if is_org_admin:
                # Org admins cannot create superusers
                validated_data.pop('is_superuser', None)
                
                # Org admins must assign users to their organization
                user_orgs = RoleService.get_user_organizations(request.user)
                if user_orgs:
                    # Use the first organization (org_admin typically has one org)
                    organization = user_orgs[0]
                    validated_data['organization'] = organization
        
        # Validate organization limits (backup check - main validation is in perform_create)
        # Super admins can bypass all checks
        if organization:
            # Get user from context to check super admin status
            user = self.context.get('request').user if self.context.get('request') else None
            is_super_admin = RoleService.is_super_admin(user) if user else False
            
            if not is_super_admin:
                # Check if organization is active
                if not organization.is_active():
                    raise serializers.ValidationError({
                        'organization': f'Cannot create user. Organization "{organization.name}" is {organization.get_status_display()}.'
                    })
                
                # Check if organization subscription is active
                if not organization.is_subscription_active():
                    raise serializers.ValidationError({
                        'organization': 'Cannot create user. Organization subscription has expired.'
                    })
                
                # Check user limit
                if not organization.can_add_user():
                    current_count = organization.get_member_count()
                    raise serializers.ValidationError({
                        'organization': f'Cannot create user. Organization has reached the maximum number of users ({organization.max_users}). Current: {current_count}'
                    })
        
        user = User.objects.create_user(**validated_data)
        
        # Add user to OrganizationMember if organization is set
        if organization:
            from apps.organizations.models import OrganizationMember
            # Check if member already exists (shouldn't happen, but safety check)
            if not OrganizationMember.objects.filter(organization=organization, user=user).exists():
                OrganizationMember.objects.create(
                    organization=organization,
                    user=user,
                    role='org_member',
                    invited_by=request.user if request and request.user else None
                )
        
        return user


class APIKeySerializer(serializers.ModelSerializer):
    """API Key serializer."""
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'user', 'name', 'key', 'is_active', 'created_at',
            'expires_at', 'last_used_at', 'rate_limit_per_minute'
        ]
        read_only_fields = ['id', 'user', 'key', 'created_at', 'last_used_at']
