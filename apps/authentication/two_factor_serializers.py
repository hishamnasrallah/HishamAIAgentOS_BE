"""
Serializers for Two-Factor Authentication.
"""

from rest_framework import serializers


class TwoFactorSetupSerializer(serializers.Serializer):
    """Serializer for 2FA setup response."""
    
    secret = serializers.CharField(read_only=True)
    qr_code = serializers.CharField(read_only=True)
    backup_codes = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )
    message = serializers.CharField(read_only=True)


class TwoFactorVerifySerializer(serializers.Serializer):
    """Serializer for verifying 2FA token during setup."""
    
    secret = serializers.CharField(required=True, help_text="TOTP secret from setup")
    token = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        help_text="6-digit TOTP token from authenticator app"
    )
    backup_codes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Backup codes from setup"
    )


class TwoFactorEnableSerializer(serializers.Serializer):
    """Serializer for enabling 2FA."""
    
    secret = serializers.CharField(required=True)
    token = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        help_text="6-digit TOTP token to verify setup"
    )
    backup_codes = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class TwoFactorDisableSerializer(serializers.Serializer):
    """Serializer for disabling 2FA."""
    
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="User password for confirmation"
    )


class TwoFactorLoginVerifySerializer(serializers.Serializer):
    """Serializer for verifying 2FA during login."""
    
    token = serializers.CharField(
        required=True,
        min_length=6,
        max_length=8,  # Allow backup codes (8 chars) or TOTP (6 chars)
        help_text="6-digit TOTP token or 8-character backup code"
    )
    user_id = serializers.UUIDField(required=True)

