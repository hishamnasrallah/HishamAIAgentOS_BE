"""
Serializers for core app.
"""

from rest_framework import serializers
from .models import SystemSettings, FeatureFlag


class SystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer for system settings."""
    
    typed_value = serializers.SerializerMethodField()
    updated_by_email = serializers.EmailField(source='updated_by.email', read_only=True, allow_null=True)
    
    class Meta:
        model = SystemSettings
        fields = [
            'id', 'key', 'value', 'typed_value', 'value_type', 'category',
            'description', 'is_public', 'created_at', 'updated_at',
            'updated_by', 'updated_by_email'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'updated_by']
    
    def get_typed_value(self, obj):
        """Return typed value."""
        return obj.get_typed_value()
    
    def validate(self, attrs):
        """Validate value based on value_type."""
        value_type = attrs.get('value_type', self.instance.value_type if self.instance else 'string')
        value = attrs.get('value', '')
        
        if value_type == 'integer':
            try:
                int(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError({'value': 'Value must be a valid integer'})
        elif value_type == 'float':
            try:
                float(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError({'value': 'Value must be a valid float'})
        elif value_type == 'boolean':
            if value.lower() not in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off'):
                raise serializers.ValidationError({'value': 'Value must be a valid boolean'})
        elif value_type == 'json':
            import json
            try:
                json.loads(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError({'value': 'Value must be valid JSON'})
        
        return attrs
    
    def update(self, instance, validated_data):
        """Update instance and set typed value."""
        # Handle typed value if provided
        typed_value = self.initial_data.get('typed_value')
        if typed_value is not None:
            instance.set_typed_value(typed_value)
            validated_data.pop('value', None)
        
        # Set updated_by
        validated_data['updated_by'] = self.context['request'].user
        
        return super().update(instance, validated_data)
    
    def create(self, validated_data):
        """Create instance and set typed value."""
        # Handle typed value if provided
        typed_value = self.initial_data.get('typed_value')
        if typed_value is not None:
            validated_data['value'] = ''
            instance = SystemSettings(**validated_data)
            instance.set_typed_value(typed_value)
        else:
            instance = SystemSettings(**validated_data)
        
        # Set updated_by
        instance.updated_by = self.context['request'].user
        instance.save()
        return instance


class FeatureFlagSerializer(serializers.ModelSerializer):
    """Serializer for feature flags."""
    
    updated_by_email = serializers.EmailField(source='updated_by.email', read_only=True, allow_null=True)
    
    class Meta:
        model = FeatureFlag
        fields = [
            'id', 'key', 'name', 'description', 'is_enabled',
            'enabled_for_roles', 'enabled_for_users',
            'created_at', 'updated_at', 'updated_by', 'updated_by_email'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'updated_by']
    
    def update(self, instance, validated_data):
        """Update instance."""
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)
    
    def create(self, validated_data):
        """Create instance."""
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)

