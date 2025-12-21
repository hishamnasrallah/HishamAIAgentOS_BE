"""
Authentication serializers for login, registration, password reset, etc.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with 2FA support."""
    
    two_factor_token = serializers.CharField(
        required=False,
        write_only=True,
        help_text="6-digit TOTP token or backup code (required if 2FA is enabled)"
    )
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        token['role'] = user.role
        
        return token
    
    def validate(self, attrs):
        # First validate email/password (parent validation)
        data = super().validate(attrs)
        
        user = self.user
        
        # Check if 2FA is enabled
        if user.two_factor_enabled:
            two_factor_token = attrs.get('two_factor_token')
            
            if not two_factor_token:
                # 2FA is required but token not provided
                from .two_factor import verify_two_factor
                raise serializers.ValidationError({
                    'two_factor_required': True,
                    'message': '2FA token is required.',
                    'user_id': str(user.id)
                })
            
            # Verify 2FA token
            from .two_factor import verify_two_factor
            if not verify_two_factor(user, two_factor_token):
                raise serializers.ValidationError({
                    'two_factor_token': 'Invalid 2FA token.'
                })
        
        # 2FA verified (or not enabled) - proceed with normal token generation
        # Add extra responses
        data['user'] = {
            'id': str(user.id),
            'email': user.email,
            'username': user.username,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'two_factor_enabled': user.two_factor_enabled,
            'is_superuser': user.is_superuser,
        }
        
        # Add user to online presence
        try:
            from apps.core.presence_views import _online_users
            from django.utils import timezone
            user_id = str(user.id)
            request = self.context.get('request') if hasattr(self, 'context') else None
            _online_users[user_id] = {
                'last_seen': timezone.now(),
                'current_page': request.path if request else '/',
                'status': 'online',
            }
        except Exception as e:
            # Don't break login if presence update fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to add user presence on login: {e}", exc_info=True)
        
        # Audit successful login
        try:
            from apps.monitoring.audit import audit_logger
            # Get request from context if available
            request = self.context.get('request') if hasattr(self, 'context') else None
            audit_logger.log_authentication(
                action='login',
                user=user,
                request=request,
                success=True,
            )
        except Exception as e:
            # Don't break login if audit logging fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to audit login: {e}", exc_info=True)
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer with automatic organization creation."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    username = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Username (auto-generated from email if not provided)'
    )
    full_name = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text='Full name (will be split into first_name and last_name)'
    )
    organization_name = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=200,
        help_text='Name of the organization to create. If not provided, will be generated from user name.'
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'full_name', 'first_name', 'last_name', 'preferred_language', 'timezone',
            'organization_name'
        ]
    
    def validate_organization_name(self, value):
        """Validate organization name uniqueness."""
        if value:
            from apps.organizations.models import Organization
            # Check if organization with this name already exists (case-insensitive)
            if Organization.objects.filter(name__iexact=value.strip()).exists():
                raise serializers.ValidationError(
                    "An organization with this name already exists. "
                    "Please ask your organization admin to create an account for you, or choose a different organization name."
                )
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        
        # Handle full_name - split into first_name and last_name if provided
        full_name = attrs.pop('full_name', None)
        if full_name and not attrs.get('first_name') and not attrs.get('last_name'):
            name_parts = full_name.strip().split(' ', 1)
            attrs['first_name'] = name_parts[0] if len(name_parts) > 0 else ''
            attrs['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
        
        # Generate username from email if not provided
        if not attrs.get('username'):
            email = attrs.get('email', '')
            if email:
                base_username = email.split('@')[0]
                # Ensure username is unique
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                attrs['username'] = username
        
        return attrs
    
    def create(self, validated_data):
        """Create user, organization, and trial subscription."""
        from django.utils import timezone
        from django.utils.text import slugify
        from datetime import timedelta
        from apps.organizations.models import Organization, OrganizationMember, Subscription, SubscriptionPlan
        
        organization_name = validated_data.pop('organization_name', None)
        password_confirm = validated_data.pop('password_confirm', None)
        
        # Create user
        try:
            user = User.objects.create_user(**validated_data)
        except Exception as e:
            # If username conflict occurs (shouldn't happen due to validation, but safety check)
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating user: {e}")
            # Try to fix username and retry
            if 'username' in str(e).lower():
                base_username = validated_data.get('username', validated_data.get('email', '').split('@')[0])
                counter = 1
                while User.objects.filter(username=f"{base_username}{counter}").exists():
                    counter += 1
                validated_data['username'] = f"{base_username}{counter}"
                user = User.objects.create_user(**validated_data)
            else:
                raise
        
        # Generate organization name if not provided
        if not organization_name:
            user_display_name = user.get_full_name() or user.username or user.email.split('@')[0]
            organization_name = f"{user_display_name}'s Organization"
        
        # Generate unique slug
        base_slug = slugify(organization_name)
        org_slug = base_slug
        counter = 1
        while Organization.objects.filter(slug=org_slug).exists():
            org_slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Get trial subscription plan - this should always exist if seed_subscriptions was run
        # If it doesn't exist, we raise an error as this is a system configuration issue
        try:
            trial_plan = SubscriptionPlan.objects.get(tier_code='trial', is_active=True)
        except SubscriptionPlan.DoesNotExist:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(
                "CRITICAL: Trial subscription plan not found. "
                "Please run 'python manage.py seed_subscriptions' to create subscription plans."
            )
            # Still create organization but log error - admin can fix subscription later
            trial_plan = None
        
        # Create organization
        organization = Organization.objects.create(
            name=organization_name,
            slug=org_slug,
            description=f"Organization for {user.get_full_name() or user.email}",
            owner=user,
            created_by=user,
            status='trial',
            subscription_tier='trial',
        )
        
        # Link user to organization
        user.organization = organization
        # Set user role to org_admin since they are creating the organization
        # The first user who creates an organization should be org_admin - there's no one else to assign this role
        # This aligns with OrganizationMember.role='org_admin' and RoleService.is_org_admin() checks
        # Note: We explicitly set this because User model defaults to 'viewer', but the organization creator should be 'org_admin'
        user.role = 'org_admin'
        user.save(update_fields=['organization', 'role'])
        
        # Create OrganizationMember with org_admin role
        # This is the organization-specific role (User.role is system-level, OrganizationMember.role is org-specific)
        OrganizationMember.objects.create(
            organization=organization,
            user=user,
            role='org_admin',
            invited_by=user
        )
        
        # Store organization ID in serializer for response (as string)
        self.organization_id = str(organization.id)
        
        # Create trial subscription if plan exists
        if trial_plan:
            now = timezone.now()
            period_start_date = now.date()
            period_end_date = period_start_date + timedelta(days=14)  # 14-day trial
            
            # Convert dates to timezone-aware datetimes for DateTimeField compatibility
            # Set time to start of day (00:00:00) for period_start and end of day (23:59:59) for period_end
            from datetime import datetime, time
            period_start_dt = timezone.make_aware(datetime.combine(period_start_date, time.min))
            period_end_dt = timezone.make_aware(datetime.combine(period_end_date, time.max.replace(microsecond=0)))
            
            subscription = Subscription.objects.create(
                organization=organization,
                plan=trial_plan,
                tier_code='trial',
                status='active',
                billing_cycle='monthly',
                started_at=period_start_dt,
                current_period_start=period_start_dt,
                current_period_end=period_end_dt,
            )
            
            # Link organization to subscription
            organization.active_subscription = subscription
            organization.subscription_start_date = period_start_date
            organization.subscription_end_date = period_end_date
            
            # Set max_users and max_projects from tier features
            from apps.organizations.services import FeatureService
            max_users = FeatureService.get_feature_value(organization, 'users.max_count', default=None)
            max_projects = FeatureService.get_feature_value(organization, 'projects.max_count', default=None)
            # Only set if we got a valid value from feature service
            # Use feature service value, not hardcoded defaults
            if max_users is not None:
                organization.max_users = max_users
            if max_projects is not None:
                organization.max_projects = max_projects
            
            organization.save(update_fields=['active_subscription', 'subscription_start_date', 'subscription_end_date', 'max_users', 'max_projects'])
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer."""
    
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Password reset request serializer."""
    
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Password reset confirmation serializer."""
    
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer for viewing/editing profile."""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'avatar', 'bio', 'preferred_language', 'timezone',
            'notification_preferences', 'two_factor_enabled', 'is_superuser',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'email', 'role', 'two_factor_enabled', 'is_superuser', 'date_joined', 'last_login']
