"""
Serializers for commands app.
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import CommandCategory, CommandTemplate


class CommandCategorySerializer(serializers.ModelSerializer):
    """Command category serializer."""
    
    command_count = serializers.SerializerMethodField()
    active_command_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CommandCategory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    @extend_schema_field(serializers.IntegerField)
    def get_command_count(self, obj) -> int:
        return obj.commands.count()
    
    @extend_schema_field(serializers.IntegerField)
    def get_active_command_count(self, obj) -> int:
        return obj.commands.filter(is_active=True).count()


class CommandTemplateSerializer(serializers.ModelSerializer):
    """Command template serializer with all fields."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    recommended_agent_name = serializers.CharField(source='recommended_agent.name', read_only=True, allow_null=True)
    
    class Meta:
        model = CommandTemplate
        fields = '__all__'
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'usage_count',
            'avg_execution_time', 'success_rate', 'total_successes', 'total_failures'
        ]


class CommandTemplateListSerializer(serializers.ModelSerializer):
    """Command template list serializer with minimal fields."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = CommandTemplate
        fields = [
            'id', 'name', 'slug', 'description', 'category_name', 
            'tags', 'usage_count', 'success_rate', 'estimated_cost', 'is_active'
        ]


class CommandExecutionRequestSerializer(serializers.Serializer):
    """Serializer for command execution requests."""
    
    parameters = serializers.JSONField(
        help_text="Parameters to pass to the command template"
    )
    agent_id = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Optional: Override the recommended agent"
    )
    
    def validate_parameters(self, value):
        """Validate parameters is a dict."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Parameters must be a dictionary")
        return value


class CommandExecutionResponseSerializer(serializers.Serializer):
    """Serializer for command execution responses."""
    
    success = serializers.BooleanField()
    output = serializers.CharField()
    execution_time = serializers.FloatField(help_text="Execution time in seconds")
    cost = serializers.DecimalField(max_digits=10, decimal_places=6, help_text="Cost in USD")
    token_usage = serializers.DictField(required=False)
    agent_used = serializers.CharField()
    error = serializers.CharField(required=False, allow_null=True)


class CommandPreviewRequestSerializer(serializers.Serializer):
    """Serializer for command preview requests."""
    
    parameters = serializers.JSONField(
        help_text="Parameters to preview in the template"
    )


class CommandPreviewResponseSerializer(serializers.Serializer):
    """Serializer for command preview responses."""
    
    rendered_template = serializers.CharField(help_text="Template with parameters substituted")
    validation_errors = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of validation errors if any"
    )
