"""
User and authentication models for HishamOS.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with email as username.
    
    Note: The role field uses dynamic roles from apps.core.services.roles.RoleService.
    For backward compatibility, ROLE_CHOICES is still available but validation
    should use RoleService.is_valid_role() instead.
    """
    
    # Backward compatibility - kept for migrations and admin interface
    # But actual validation should use RoleService
    @classmethod
    def get_role_choices(cls):
        """Get role choices dynamically from RoleService."""
        try:
            from apps.core.services.roles import RoleService
            return [(role, info['label']) for role, info in RoleService.SYSTEM_ROLES.items()]
        except ImportError:
            # Fallback for migrations
            return [
                ('admin', 'Administrator'),
                ('manager', 'Project Manager'),
                ('developer', 'Developer'),
                ('viewer', 'Viewer'),
            ]
    
    # Keep ROLE_CHOICES for backward compatibility
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Project Manager'),
        ('developer', 'Developer'),
        ('viewer', 'Viewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Organization relationship (for SaaS multi-tenancy)
    # Users belong to an organization, but super admins can access all organizations
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        db_index=True,
        help_text='Primary organization this user belongs to. Super admins can access all organizations.'
    )
    
    # Role field - validation should use RoleService.is_valid_role()
    # Note: 'admin' role is deprecated. Use 'org_admin' for organization admins or is_superuser for super admins
    role = models.CharField(max_length=50, default='viewer', help_text='System-level role. Use RoleService for validation.')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # User tracking (for user creation/updates by admins)
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        verbose_name='Created By',
        help_text='Admin user who created this user account'
    )
    updated_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_users',
        verbose_name='Updated By',
        help_text='User who last updated this account'
    )
    
    # Additional profile fields
    avatar = models.CharField(max_length=500, blank=True)
    bio = models.TextField(blank=True)
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    # 2FA fields
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    
    # Preferences
    preferred_language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['is_active', 'role']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the user's full name."""
        return f'{self.first_name} {self.last_name}'.strip()
    
    def get_short_name(self):
        """Return the user's short name."""
        return self.first_name
    
    def get_avatar_url(self):
        """Get avatar URL with fallback."""
        if self.avatar:
            # If avatar is a full URL, return it
            if self.avatar.startswith('http://') or self.avatar.startswith('https://'):
                return self.avatar
            # If avatar is a relative path, construct full URL
            from django.conf import settings
            try:
                from django.contrib.staticfiles.storage import staticfiles_storage
                return staticfiles_storage.url(self.avatar)
            except:
                return self.avatar
        return None
    
    def get_initials(self):
        """Generate user initials for avatar fallback."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[0].upper()
        elif self.last_name:
            return self.last_name[0].upper()
        elif self.username:
            return self.username[0].upper()
        elif self.email:
            return self.email[0].upper()
        return "?"
    
    def get_avatar_color(self):
        """Generate a consistent color for the user based on their ID."""
        import hashlib
        hash_obj = hashlib.md5(str(self.id).encode())
        hash_int = int(hash_obj.hexdigest()[:8], 16)
        # Generate a color in the range of nice colors (avoid too dark/light)
        hue = hash_int % 360
        saturation = 60 + (hash_int % 20)  # 60-80%
        lightness = 45 + (hash_int % 15)  # 45-60%
        return f"hsl({hue}, {saturation}%, {lightness}%)"


class APIKey(models.Model):
    """API keys for programmatic access."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=200)
    key = models.CharField(max_length=64, unique=True, db_index=True)
    
    is_active = models.BooleanField(default=True)
    
    # User tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_api_keys',
        verbose_name='Created By'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_api_keys',
        verbose_name='Updated By'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    # Rate limiting
    rate_limit_per_minute = models.IntegerField(default=60)
    
    class Meta:
        db_table = 'api_keys'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.email}"
    
    def is_expired(self):
        """Check if API key has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def update_last_used(self):
        """Update last used timestamp."""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])
