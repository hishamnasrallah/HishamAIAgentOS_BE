"""
Core base models and mixins for HishamOS.
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class TimestampedModel(models.Model):
    """
    Abstract base model with created_at and updated_at timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    
    class Meta:
        abstract = True


class TrackedModel(TimestampedModel):
    """
    Abstract base model with created_by, updated_by, created_at, and updated_at.
    Automatically tracks who created and updated records.
    """
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name='Created By',
        help_text='User who created this record'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name='Updated By',
        help_text='User who last updated this record'
    )
    
    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract base model with UUID primary key.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True


class BaseModel(UUIDModel, TrackedModel):
    """
    Complete base model with UUID, timestamps, and user tracking.
    Use this for all new models that need full tracking.
    """
    class Meta:
        abstract = True


class SystemSettings(models.Model):
    """System-wide configuration settings."""
    
    SETTING_CATEGORY_CHOICES = [
        ('general', 'General'),
        ('security', 'Security'),
        ('performance', 'Performance'),
        ('notifications', 'Notifications'),
        ('integrations', 'Integrations'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField(blank=True)
    value_type = models.CharField(
        max_length=20,
        choices=[
            ('string', 'String'),
            ('integer', 'Integer'),
            ('float', 'Float'),
            ('boolean', 'Boolean'),
            ('json', 'JSON'),
        ],
        default='string'
    )
    category = models.CharField(max_length=50, choices=SETTING_CATEGORY_CHOICES, default='general')
    description = models.TextField(blank=True)
    is_public = models.BooleanField(
        default=False,
        help_text="If True, this setting can be accessed by non-admin users"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_settings'
    )
    
    class Meta:
        db_table = 'system_settings'
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.key} = {self.value}"
    
    def get_typed_value(self):
        """Return value converted to appropriate type."""
        if self.value_type == 'integer':
            try:
                return int(self.value)
            except (ValueError, TypeError):
                return 0
        elif self.value_type == 'float':
            try:
                return float(self.value)
            except (ValueError, TypeError):
                return 0.0
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.value_type == 'json':
            import json
            try:
                return json.loads(self.value)
            except (ValueError, TypeError):
                return {}
        return self.value
    
    def set_typed_value(self, value):
        """Set value with automatic type conversion."""
        if self.value_type == 'boolean':
            self.value = 'true' if value else 'false'
        elif self.value_type == 'json':
            import json
            self.value = json.dumps(value)
        else:
            self.value = str(value)


class FeatureFlag(models.Model):
    """Feature flags for enabling/disabling features."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_enabled = models.BooleanField(default=False)
    enabled_for_roles = models.JSONField(
        default=list,
        blank=True,
        help_text="List of roles that have access (empty = all roles)"
    )
    enabled_for_users = models.JSONField(
        default=list,
        blank=True,
        help_text="List of user IDs that have access (empty = all users)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_feature_flags'
    )
    
    class Meta:
        db_table = 'feature_flags'
        verbose_name = 'Feature Flag'
        verbose_name_plural = 'Feature Flags'
        ordering = ['key']
    
    def __str__(self):
        return f"{self.name} ({'Enabled' if self.is_enabled else 'Disabled'})"
    
    def is_accessible_by_user(self, user):
        """Check if feature is accessible by a specific user."""
        if not self.is_enabled:
            return False
        
        # Check role-based access
        if self.enabled_for_roles:
            if user.role not in self.enabled_for_roles:
                return False
        
        # Check user-specific access
        if self.enabled_for_users:
            if str(user.id) not in self.enabled_for_users:
                return False
        
        return True
