"""
Serializers for authentication app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import APIKey

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'role',
            'is_active', 'two_factor_enabled', 'preferred_language', 'timezone',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


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
