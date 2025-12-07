"""
Serializers for chat models.
"""

from rest_framework import serializers
from .models import Conversation, Message
from apps.agents.models import Agent


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    
    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'role',
            'content',
            'attachments',
            'created_at',
            'tokens_used'
        ]
        read_only_fields = ['id', 'created_at', 'tokens_used']


class ConversationListSerializer(serializers.ModelSerializer):
    """Serializer for conversation list view."""
    
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id',
            'agent',
            'agent_name',
            'title',
            'created_at',
            'updated_at',
            'is_archived',
            'message_count',
            'last_message'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'role': last_msg.role,
                'content': last_msg.content[:100] + '...' if len(last_msg.content) > 100 else last_msg.content,
                'created_at': last_msg.created_at
            }
        return None


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Serializer for conversation detail view with messages."""
    
    messages = MessageSerializer(many=True, read_only=True)
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id',
            'user',
            'user_email',
            'agent',
            'agent_name',
            'title',
            'created_at',
            'updated_at',
            'is_archived',
            'messages'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating conversations."""
    
    initial_message = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Optional first message to start the conversation"
    )
    
    class Meta:
        model = Conversation
        fields = ['agent', 'title', 'initial_message']
    
    def create(self, validated_data):
        initial_message = validated_data.pop('initial_message', None)
        
        # Set user from request context
        validated_data['user'] = self.context['request'].user
        
        # Auto-generate title from first message if not provided
        if not validated_data.get('title') and initial_message:
            validated_data['title'] = initial_message[:50] + '...' if len(initial_message) > 50 else initial_message
        elif not validated_data.get('title'):
            agent = validated_data['agent']
            validated_data['title'] = f"Chat with {agent.name}"
        
        conversation = Conversation.objects.create(**validated_data)
        
        # Create initial message if provided
        if initial_message:
            Message.objects.create(
                conversation=conversation,
                role='user',
                content=initial_message
            )
        
        return conversation


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending a message."""
    
    content = serializers.CharField()
    attachments = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
