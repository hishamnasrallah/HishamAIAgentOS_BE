"""
Serializers for chat models.
"""

from rest_framework import serializers
from django.db.models import Q
from .models import Conversation, Message, MemberConversation, MemberMessage
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
            'ai_provider_context',
            'extracted_identifiers',
            'provider_metadata',
            'token_usage_history',
            'cost_tracking',
            'max_recent_messages',
            'conversation_summary',
            'summary_metadata',
            'summarize_at_message_count',
            'summarize_at_token_count',
            'referenced_files',
            'referenced_code_blocks',
            'code_context_metadata',
            'messages'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 
                           'ai_provider_context', 'extracted_identifiers', 
                           'provider_metadata', 'token_usage_history', 'cost_tracking',
                           'conversation_summary', 'summary_metadata',
                           'referenced_files', 'referenced_code_blocks', 'code_context_metadata']
    
    def update(self, instance, validated_data):
        """Allow updating title."""
        # Only allow title updates for now
        if 'title' in validated_data:
            instance.title = validated_data['title']
            instance.save(update_fields=['title', 'updated_at'])
        return instance


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


# Member Conversation Serializers

class MemberMessageSerializer(serializers.ModelSerializer):
    """Serializer for MemberMessage model."""
    
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = MemberMessage
        fields = [
            'id',
            'conversation',
            'sender',
            'sender_email',
            'sender_username',
            'role',
            'content',
            'attachments',
            'created_at',
            'updated_at',
            'is_delivered',
            'delivered_at',
            'is_read',
            'read_at'
        ]
        read_only_fields = ['id', 'sender', 'created_at', 'updated_at', 'is_delivered', 'delivered_at', 'is_read', 'read_at']


class MemberConversationListSerializer(serializers.ModelSerializer):
    """Serializer for member conversation list view."""
    
    other_participant_email = serializers.SerializerMethodField()
    other_participant_username = serializers.SerializerMethodField()
    other_participant_id = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    display_title = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MemberConversation
        fields = [
            'id',
            'participant1',
            'participant2',
            'organization',
            'title',
            'other_participant_id',
            'other_participant_email',
            'other_participant_username',
            'display_title',
            'created_at',
            'updated_at',
            'is_archived',
            'message_count',
            'last_message',
            'unread_count'
        ]
        read_only_fields = ['id', 'participant1', 'participant2', 'organization', 'created_at', 'updated_at']
    
    def get_other_participant_email(self, obj):
        """Get the other participant's email."""
        request = self.context.get('request')
        if request and request.user:
            other = obj.get_other_participant(request.user)
            return other.email if other else None
        return None
    
    def get_other_participant_username(self, obj):
        """Get the other participant's username."""
        request = self.context.get('request')
        if request and request.user:
            other = obj.get_other_participant(request.user)
            return other.username if other else None
        return None
    
    def get_other_participant_id(self, obj):
        """Get the other participant's ID."""
        request = self.context.get('request')
        if request and request.user:
            other = obj.get_other_participant(request.user)
            return str(other.id) if other else None
        return None
    
    def get_display_title(self, obj):
        """Get display title for the conversation."""
        request = self.context.get('request')
        if request and request.user:
            return obj.get_display_title(request.user)
        return obj.title or "Member Chat"
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'sender_id': str(last_msg.sender.id),
                'sender_email': last_msg.sender.email,
                'content': last_msg.content[:100] + '...' if len(last_msg.content) > 100 else last_msg.content,
                'created_at': last_msg.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        """Get unread message count for current user."""
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class MemberConversationDetailSerializer(serializers.ModelSerializer):
    """Serializer for member conversation detail view with messages."""
    
    messages = MemberMessageSerializer(many=True, read_only=True)
    other_participant_email = serializers.SerializerMethodField()
    other_participant_username = serializers.SerializerMethodField()
    other_participant_id = serializers.SerializerMethodField()
    display_title = serializers.SerializerMethodField()
    
    class Meta:
        model = MemberConversation
        fields = [
            'id',
            'participant1',
            'participant2',
            'organization',
            'title',
            'other_participant_id',
            'other_participant_email',
            'other_participant_username',
            'display_title',
            'created_at',
            'updated_at',
            'is_archived',
            'messages'
        ]
        read_only_fields = ['id', 'participant1', 'participant2', 'organization', 'created_at', 'updated_at']
    
    def get_other_participant_email(self, obj):
        request = self.context.get('request')
        if request and request.user:
            other = obj.get_other_participant(request.user)
            return other.email if other else None
        return None
    
    def get_other_participant_username(self, obj):
        request = self.context.get('request')
        if request and request.user:
            other = obj.get_other_participant(request.user)
            return other.username if other else None
        return None
    
    def get_other_participant_id(self, obj):
        request = self.context.get('request')
        if request and request.user:
            other = obj.get_other_participant(request.user)
            return str(other.id) if other else None
        return None
    
    def get_display_title(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.get_display_title(request.user)
        return obj.title or "Member Chat"
    
    def update(self, instance, validated_data):
        """Allow updating title."""
        if 'title' in validated_data:
            instance.title = validated_data['title']
            instance.save(update_fields=['title', 'updated_at'])
        return instance


class MemberConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating member conversations."""
    
    initial_message = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Optional first message to start the conversation"
    )
    
    class Meta:
        model = MemberConversation
        fields = ['participant2', 'title', 'initial_message']
    
    def validate(self, data):
        """Validate that participants are in the same organization."""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Request context required")
        
        participant1 = request.user
        participant2 = data.get('participant2')
        
        if participant1 == participant2:
            raise serializers.ValidationError("Cannot create a conversation with yourself")
        
        # Get organizations for both participants
        from apps.core.services.roles import RoleService
        org1 = RoleService.get_user_organization(participant1)
        org2 = RoleService.get_user_organization(participant2)
        
        if not org1 or not org2:
            raise serializers.ValidationError("Both users must belong to an organization")
        
        if org1 != org2:
            raise serializers.ValidationError("Participants must be in the same organization")
        
        data['participant1'] = participant1
        data['organization'] = org1
        return data
    
    def create(self, validated_data):
        initial_message = validated_data.pop('initial_message', None)
        
        # Check if conversation already exists between these two users
        participant1 = validated_data['participant1']
        participant2 = validated_data['participant2']
        organization = validated_data['organization']
        
        # Try to find existing conversation (order doesn't matter)
        existing = MemberConversation.objects.filter(
            organization=organization
        ).filter(
            (Q(participant1=participant1, participant2=participant2) |
             Q(participant1=participant2, participant2=participant1))
        ).first()
        
        if existing:
            # Update title if provided
            if validated_data.get('title'):
                existing.title = validated_data['title']
                existing.save(update_fields=['title', 'updated_at'])
            # Create initial message if provided
            if initial_message:
                MemberMessage.objects.create(
                    conversation=existing,
                    sender=participant1,
                    role='user',
                    content=initial_message
                )
            return existing
        
        # Set default title if not provided
        if not validated_data.get('title'):
            validated_data['title'] = ''  # Will use display title based on participant
        
        conversation = MemberConversation.objects.create(**validated_data)
        
        # Create initial message if provided
        if initial_message:
            MemberMessage.objects.create(
                conversation=conversation,
                sender=participant1,
                role='user',
                content=initial_message
            )
        
        return conversation


class SendMemberMessageSerializer(serializers.Serializer):
    """Serializer for sending a message in member conversation."""
    
    content = serializers.CharField()
    attachments = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
