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
        help_text="Auto-generated from first message or user-set"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    
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
    created_at = models.DateTimeField(auto_now_add=True)
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
