"""
Serializers for integrations app.
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import AIPlatform, PlatformUsage


class AIPlatformSerializer(serializers.ModelSerializer):
    """Serializer for AI platforms with all configuration fields."""
    
    health_status = serializers.SerializerMethodField()
    api_key = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        help_text="API key (will be encrypted before storage). Leave blank to keep existing key."
    )
    has_api_key = serializers.SerializerMethodField(
        help_text="Whether an API key is configured (without exposing the key)"
    )
    
    class Meta:
        model = AIPlatform
        fields = [
            'id', 'platform_name', 'display_name', 'api_type', 'default_model',
            'api_key', 'has_api_key', 'api_url', 'organization_id', 'timeout', 'max_tokens',
            'supports_vision', 'supports_json_mode', 'supports_image_generation',
            'rate_limit_per_minute', 'rate_limit_per_day',
            'status', 'is_default', 'priority', 'is_enabled',
            'conversation_strategy', 'conversation_id_field', 'returns_conversation_id', 
            'conversation_id_path', 'api_stateful', 'sdk_session_support',
            'supported_identifiers', 'metadata_fields', 'identifier_extraction_paths',
            'provider_notes', 'cost_optimization_notes',
            'total_requests', 'failed_requests', 'total_tokens', 'total_cost',
            'last_health_check', 'is_healthy', 'health_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_requests', 'failed_requests', 'total_tokens',
            'total_cost', 'last_health_check', 'is_healthy', 'created_at', 'updated_at'
        ]
    
    @extend_schema_field(serializers.CharField)
    def get_health_status(self, obj) -> str:
        return 'healthy' if obj.is_healthy else 'unhealthy'
    
    @extend_schema_field(serializers.BooleanField)
    def get_has_api_key(self, obj) -> bool:
        """Return whether API key is configured without exposing it."""
        return obj.has_api_key()
    
    def update(self, instance, validated_data):
        """Update instance with encrypted API key handling."""
        # Handle API key separately - encrypt if provided
        api_key = validated_data.pop('api_key', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Handle API key: only update if a new value is provided
        if api_key is not None:
            if api_key:
                # New key provided - encrypt and store
                instance.set_api_key(api_key)
            else:
                # Empty string provided - clear the key
                instance.api_key = ""
        
        instance.save()
        return instance
    
    def create(self, validated_data):
        """Create instance with encrypted API key."""
        api_key = validated_data.pop('api_key', '')
        
        instance = AIPlatform.objects.create(**validated_data)
        
        # Set API key if provided
        if api_key:
            instance.set_api_key(api_key)
            instance.save()
        
        return instance


class PlatformUsageSerializer(serializers.ModelSerializer):
    """Platform usage serializer."""
    
    platform_name = serializers.CharField(source='platform.display_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True, allow_null=True)
    
    class Meta:
        model = PlatformUsage
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']
