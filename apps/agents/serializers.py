"""
Serializers for agents app.
"""

from rest_framework import serializers
from .models import Agent, AgentExecution


class AgentSerializer(serializers.ModelSerializer):
    """Agent serializer."""
    
    class Meta:
        model = Agent
        fields = '__all__'
        read_only_fields = [
            'id', 'total_invocations', 'total_tokens_used', 'total_cost',
            'average_response_time', 'success_rate', 'created_at', 'updated_at',
            'last_invoked_at'
        ]


class AgentListSerializer(serializers.ModelSerializer):
    """Agent list serializer with minimal fields."""
    
    class Meta:
        model = Agent
        fields = [
            'id', 'agent_id', 'name', 'status', 'capabilities',
            'total_invocations', 'success_rate', 'created_at'
        ]


class AgentExecutionSerializer(serializers.ModelSerializer):
    """Agent execution serializer."""
    
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = AgentExecution
        fields = '__all__'
        read_only_fields = [
            'id', 'created_at', 'started_at', 'completed_at',
            'output_data', 'error_message', 'tokens_used', 'cost', 'execution_time'
        ]


class AgentExecutionCreateSerializer(serializers.ModelSerializer):
    """Agent execution creation serializer."""
    
    class Meta:
        model = AgentExecution
        fields = ['agent', 'input_data', 'context']


class AgentExecutionInputSerializer(serializers.Serializer):
    """Serializer for agent execution input."""
    
    input_data = serializers.JSONField(
        help_text="Input data for the agent (e.g., task description, message, etc.)"
    )
    context = serializers.JSONField(
        required=False,
        help_text="Optional execution context (e.g., conversation history, metadata)"
    )


class AgentExecutionOutputSerializer(serializers.Serializer):
    """Serializer for agent execution output."""
    
    success = serializers.BooleanField()
    output = serializers.JSONField()
    error = serializers.CharField(required=False, allow_null=True)
    execution_id = serializers.UUIDField()
    tokens_used = serializers.IntegerField()
    cost = serializers.FloatField()
    execution_time = serializers.FloatField()
    platform_used = serializers.CharField()
    model_used = serializers.CharField()
    metadata = serializers.JSONField()
