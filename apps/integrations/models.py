"""
AI Platform Integration models for HishamOS.
"""

import uuid
import logging

from django.db import models
from django.core.exceptions import ValidationError

from .utils.encryption import encrypt_api_key, decrypt_api_key, is_encrypted

logger = logging.getLogger(__name__)


class AIPlatform(models.Model):
    """AI Platform configuration with adapter-level capabilities."""

    PLATFORM_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic Claude'),
        ('google', 'Google Gemini'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # -------------------------------
    # BASIC INFO
    # -------------------------------
    platform_name = models.CharField(
        max_length=50,
        choices=PLATFORM_CHOICES,
        unique=True
    )
    display_name = models.CharField(max_length=100)

    # -------------------------------
    # API CONFIGURATION
    # -------------------------------
    # api_key is stored encrypted in the database
    # Use get_api_key() and set_api_key() methods to access
    api_key = models.CharField(max_length=500, blank=True, help_text="Encrypted API key")
    api_url = models.URLField(blank=True)
    organization_id = models.CharField(max_length=255, blank=True)

    api_type = models.CharField(
        max_length=50,
        default="openai",
        help_text="Type of API structure used by this provider (openai/anthropic/google)."
    )

    default_model = models.CharField(
        max_length=100,
        default="gpt-4.1",
        help_text="Default model name used by this platform."
    )

    timeout = models.IntegerField(
        default=30,
        help_text="Default timeout (seconds)."
    )

    max_tokens = models.IntegerField(
        default=32000,
        help_text="Maximum tokens the model supports for input + output."
    )

    # -------------------------------
    # CAPABILITIES
    # -------------------------------
    supports_vision = models.BooleanField(default=False)
    supports_json_mode = models.BooleanField(default=False)
    supports_image_generation = models.BooleanField(default=False)

    # -------------------------------
    # RATE LIMITING
    # -------------------------------
    rate_limit_per_minute = models.IntegerField(default=60)
    rate_limit_per_day = models.IntegerField(default=10000)

    # -------------------------------
    # STATUS & FLAGS
    # -------------------------------
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_default = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    is_enabled = models.BooleanField(default=True)

    # -------------------------------
    # METRICS
    # -------------------------------
    total_requests = models.BigIntegerField(default=0)
    failed_requests = models.BigIntegerField(default=0)
    total_tokens = models.BigIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)

    # -------------------------------
    # HEALTH
    # -------------------------------
    last_health_check = models.DateTimeField(null=True, blank=True)
    is_healthy = models.BooleanField(default=True)

    # -------------------------------
    # TIMESTAMPS
    # -------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_platforms'
        verbose_name = 'AI Platform'
        verbose_name_plural = 'AI Platforms'
        ordering = ['-priority']

    def __str__(self):
        return self.display_name
    
    def get_api_key(self) -> str:
        """
        Get decrypted API key.
        
        Returns:
            str: Decrypted API key (plain text)
        """
        if not self.api_key:
            return ""
        
        try:
            return decrypt_api_key(self.api_key)
        except Exception as e:
            logger.error(f"Failed to decrypt API key for platform {self.platform_name}: {str(e)}")
            # Return empty string if decryption fails
            return ""
    
    def set_api_key(self, plain_key: str):
        """
        Set and encrypt API key.
        
        Args:
            plain_key: Plain text API key to encrypt and store
        """
        if not plain_key:
            self.api_key = ""
            return
        
        try:
            self.api_key = encrypt_api_key(plain_key)
        except Exception as e:
            logger.error(f"Failed to encrypt API key for platform {self.platform_name}: {str(e)}")
            raise ValidationError(f"Failed to encrypt API key: {str(e)}")
    
    def has_api_key(self) -> bool:
        """
        Check if platform has an API key set.
        
        Returns:
            bool: True if API key exists (encrypted or plain)
        """
        return bool(self.api_key)
    
    def is_api_key_encrypted(self) -> bool:
        """
        Check if the stored API key is encrypted.
        
        Returns:
            bool: True if key is encrypted, False if plain text
        """
        if not self.api_key:
            return False
        return is_encrypted(self.api_key)


class PlatformUsage(models.Model):
    """Platform usage tracking."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform = models.ForeignKey(AIPlatform, on_delete=models.CASCADE, related_name='usage_logs')
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Request details
    model = models.CharField(max_length=100)
    tokens_used = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    
    # Response
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    response_time = models.FloatField(default=0)  # in seconds
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'platform_usage'
        verbose_name = 'Platform Usage'
        verbose_name_plural = 'Platform Usage'
        indexes = [
            models.Index(fields=['platform', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.platform.platform_name} - {self.timestamp}'
