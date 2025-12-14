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
    """User registration serializer."""
    
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
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'preferred_language', 'timezone'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
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
