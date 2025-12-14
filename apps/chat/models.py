"""
Chat models for conversation management.
"""

from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Conversation(models.Model):
    """
    Chat conversation between a user and an AI agent.
    
    Represents the top-level container for a chat session.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    agent = models.ForeignKey(
        'agents.Agent',
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    title = models.CharField(
        max_length=200,
        help_text="Auto-generated from first message or user-set. Can be edited by user."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    
    # AI Provider conversation context metadata
    # Stores provider-specific conversation IDs/threads/sessions for maintaining context
    ai_provider_context = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider-specific conversation context (thread_id, session_id, conversation_id, etc.)"
    )
    
    # ALL extracted identifiers from provider responses
    extracted_identifiers = models.JSONField(
        default=dict,
        blank=True,
        help_text="All extracted identifiers: {thread_id: '...', session_id: '...', conversation_id: '...', run_id: '...', assistant_id: '...', etc.}"
    )
    
    # Complete provider response metadata for all messages
    provider_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Complete provider response metadata: {message_id: {usage: {...}, model: '...', finish_reason: '...', etc.}}"
    )
    
    # Token usage history per message
    token_usage_history = models.JSONField(
        default=list,
        blank=True,
        help_text="Token usage per message: [{message_id: '...', input_tokens: 100, output_tokens: 50, total_tokens: 150, timestamp: '...'}]"
    )
    
    # Cost tracking
    cost_tracking = models.JSONField(
        default=dict,
        blank=True,
        help_text="Cost tracking: {total_cost: 0.05, currency: 'USD', per_message_costs: [{message_id: '...', cost: 0.01}], last_updated: '...'}"
    )
    
    # Optimization settings for stateless providers (when provider doesn't maintain context)
    max_recent_messages = models.IntegerField(
        default=20,
        help_text="Maximum recent messages to send for stateless providers (sliding window)"
    )
    
    # Conversation summarization for long conversations
    conversation_summary = models.TextField(
        blank=True,
        null=True,
        help_text="AI-generated summary of older conversation history (for maintaining context in long conversations)"
    )
    
    summary_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Summary metadata: {last_summarized_at: '...', messages_summarized_count: 10, summary_version: 1, summary_tokens: 150}"
    )
    
    # Thresholds for triggering summarization
    summarize_at_message_count = models.IntegerField(
        default=30,
        help_text="Trigger summarization when conversation reaches this many messages"
    )
    
    summarize_at_token_count = models.IntegerField(
        default=8000,
        help_text="Trigger summarization when conversation tokens exceed this count (approximate)"
    )
    
    # Code context tracking (Cursor-style features)
    referenced_files = models.JSONField(
        default=list,
        blank=True,
        help_text="List of file paths referenced in conversation (e.g., ['app/models.py', 'frontend/src/Chat.tsx'])"
    )
    
    referenced_code_blocks = models.JSONField(
        default=list,
        blank=True,
        help_text="Code blocks extracted from messages: [{message_id, language, content, tokens, extracted_at}]"
    )
    
    code_context_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Code context metadata: {total_blocks: 5, total_code_tokens: 750, last_updated: '...'}"
    )
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['agent', '-updated_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} <-> {self.agent.name}: {self.title}"


class Message(models.Model):
    """
    Individual message in a conversation.
    
    Can be from user, assistant (agent), or system.
    """
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text="List of file references/URLs"
    )
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_messages',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_messages',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of tokens used for this message"
    )
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]
    
    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.role}: {preview}"


class MemberConversation(models.Model):
    """
    Chat conversation between two organization members.
    
    Represents a direct message conversation between users in the same organization.
    This is separate from AI agent conversations.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Participants - both users are in the same organization
    participant1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='member_conversations_as_participant1'
    )
    participant2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='member_conversations_as_participant2'
    )
    
    # Organization this conversation belongs to
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='member_conversations'
    )
    
    title = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="Optional title for the conversation. Defaults to other participant's name if not set."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['participant1', '-updated_at']),
            models.Index(fields=['participant2', '-updated_at']),
            models.Index(fields=['organization', '-updated_at']),
        ]
        constraints = [
            # Unique constraint: one conversation per pair of users per organization
            models.UniqueConstraint(
                fields=['participant1', 'participant2', 'organization'],
                name='unique_member_conversation'
            ),
        ]
    
    def __str__(self):
        title_display = self.title or f"{self.participant1.email} <-> {self.participant2.email}"
        return f"{title_display} ({self.organization.name})"
    
    def get_other_participant(self, user):
        """Get the other participant in the conversation."""
        if user == self.participant1:
            return self.participant2
        elif user == self.participant2:
            return self.participant1
        return None
    
    def get_display_title(self, current_user):
        """Get display title for the conversation from current user's perspective."""
        if self.title:
            return self.title
        other = self.get_other_participant(current_user)
        if other:
            return other.username or other.email
        return "Member Chat"


class MemberMessage(models.Model):
    """
    Individual message in a member-to-member conversation.
    
    Similar to Message but for member conversations.
    """
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('system', 'System'),  # For system notifications
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        MemberConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_member_messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    content = models.TextField()
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text="List of file references/URLs"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    is_delivered = models.BooleanField(default=False, help_text="Message has been delivered to recipient")
    delivered_at = models.DateTimeField(null=True, blank=True, help_text="When message was delivered")
    is_read = models.BooleanField(default=False, help_text="Message has been read by recipient")
    read_at = models.DateTimeField(null=True, blank=True, help_text="When message was read")
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['is_read', 'created_at']),
            models.Index(fields=['is_delivered', 'created_at']),
        ]
    
    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.sender.email}: {preview}"
