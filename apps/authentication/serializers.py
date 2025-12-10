"""
Serializers for authentication app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import APIKey

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
            'is_active', 'two_factor_enabled', 'preferred_language', 'timezone',
            'date_joined', 'last_login', 'notification_preferences'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'avatar_url', 'initials', 'full_name']
    
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
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class APIKeySerializer(serializers.ModelSerializer):
    """API Key serializer."""
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'user', 'name', 'key', 'is_active', 'created_at',
            'expires_at', 'last_used_at', 'rate_limit_per_minute'
        ]
        read_only_fields = ['id', 'key', 'created_at', 'last_used_at']
