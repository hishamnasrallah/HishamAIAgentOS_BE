"""
Two-Factor Authentication (2FA) utilities for HishamOS.

Implements TOTP (Time-based One-Time Password) using pyotp and QR code generation.
"""

import pyotp
import qrcode
import io
import base64
import secrets
import logging
from typing import Tuple, List, Optional
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()


def generate_totp_secret() -> str:
    """
    Generate a new TOTP secret for a user.
    
    Returns:
        str: Base32-encoded secret key
    """
    return pyotp.random_base32()


def get_totp_uri(user: User, secret: Optional[str] = None) -> str:
    """
    Generate TOTP URI for QR code generation.
    
    Args:
        user: User instance
        secret: TOTP secret (uses user's secret if not provided)
        
    Returns:
        str: TOTP URI (otpauth://totp/...)
    """
    if secret is None:
        secret = user.two_factor_secret
    
    if not secret:
        raise ValueError("TOTP secret is required")
    
    # Get issuer name from settings or use default
    issuer_name = getattr(settings, 'TWO_FACTOR_ISSUER_NAME', 'HishamOS')
    
    # Use email as account name
    account_name = user.email
    
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=account_name,
        issuer_name=issuer_name
    )


def generate_qr_code(uri: str) -> str:
    """
    Generate QR code image as base64-encoded string.
    
    Args:
        uri: TOTP URI to encode in QR code
        
    Returns:
        str: Base64-encoded PNG image data (data:image/png;base64,...)
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{image_base64}"


def verify_totp_token(secret: str, token: str, window: int = 1) -> bool:
    """
    Verify a TOTP token against a secret.
    
    Args:
        secret: TOTP secret key
        token: 6-digit token to verify
        window: Time window for verification (default: 1, allows ±30 seconds)
        
    Returns:
        bool: True if token is valid
    """
    if not secret or not token:
        return False
    
    try:
        totp = pyotp.TOTP(secret)
        # Verify with a time window (default ±30 seconds)
        return totp.verify(token, valid_window=window)
    except Exception as e:
        logger.error(f"TOTP verification error: {str(e)}")
        return False


def generate_backup_codes(count: int = 10) -> List[str]:
    """
    Generate backup codes for 2FA.
    
    Backup codes are single-use codes that can be used instead of TOTP.
    Format: 8-digit codes, hyphenated (e.g., "1234-5678")
    
    Args:
        count: Number of backup codes to generate
        
    Returns:
        List[str]: List of backup codes
    """
    codes = []
    for _ in range(count):
        # Generate 8 random digits
        code = ''.join([str(secrets.randbelow(10)) for _ in range(8)])
        # Hyphenate: XXXX-XXXX
        formatted_code = f"{code[:4]}-{code[4:]}"
        codes.append(formatted_code)
    
    return codes


def setup_two_factor(user: User) -> Tuple[str, str, List[str]]:
    """
    Set up 2FA for a user.
    
    This generates a new secret, creates a QR code, and generates backup codes.
    The secret is NOT saved to the user model - that should be done after verification.
    
    Args:
        user: User instance to set up 2FA for
        
    Returns:
        Tuple[str, str, List[str]]: (secret, qr_code_base64, backup_codes)
    """
    # Generate new secret
    secret = generate_totp_secret()
    
    # Generate TOTP URI
    uri = get_totp_uri(user, secret)
    
    # Generate QR code
    qr_code = generate_qr_code(uri)
    
    # Generate backup codes
    backup_codes = generate_backup_codes()
    
    return secret, qr_code, backup_codes


def enable_two_factor(user: User, secret: str, backup_codes: List[str]) -> None:
    """
    Enable 2FA for a user.
    
    Args:
        user: User instance
        secret: TOTP secret key
        backup_codes: List of backup codes (stored as JSON)
    """
    user.two_factor_secret = secret
    user.two_factor_enabled = True
    
    # Store backup codes in notification_preferences or create a separate field
    # For now, we'll store them in notification_preferences
    if not user.notification_preferences:
        user.notification_preferences = {}
    user.notification_preferences['backup_codes'] = backup_codes
    
    user.save(update_fields=['two_factor_secret', 'two_factor_enabled', 'notification_preferences'])
    logger.info(f"2FA enabled for user {user.email}")


def disable_two_factor(user: User) -> None:
    """
    Disable 2FA for a user.
    
    Args:
        user: User instance
    """
    user.two_factor_enabled = False
    user.two_factor_secret = ''
    
    # Clear backup codes
    if user.notification_preferences:
        user.notification_preferences.pop('backup_codes', None)
    
    user.save(update_fields=['two_factor_enabled', 'two_factor_secret', 'notification_preferences'])
    logger.info(f"2FA disabled for user {user.email}")


def verify_two_factor(user: User, token: str) -> bool:
    """
    Verify 2FA token for a user.
    
    Checks both TOTP token and backup codes.
    
    Args:
        user: User instance
        token: 6-digit TOTP token or backup code
        
    Returns:
        bool: True if token is valid
    """
    if not user.two_factor_enabled or not user.two_factor_secret:
        return False
    
    # Check if it's a backup code
    backup_codes = user.notification_preferences.get('backup_codes', []) if user.notification_preferences else []
    
    if token in backup_codes:
        # Remove used backup code
        backup_codes.remove(token)
        if not user.notification_preferences:
            user.notification_preferences = {}
        user.notification_preferences['backup_codes'] = backup_codes
        user.save(update_fields=['notification_preferences'])
        logger.info(f"Backup code used for user {user.email}")
        return True
    
    # Verify TOTP token
    return verify_totp_token(user.two_factor_secret, token)


def get_backup_codes(user: User) -> List[str]:
    """
    Get remaining backup codes for a user.
    
    Args:
        user: User instance
        
    Returns:
        List[str]: List of remaining backup codes
    """
    if not user.notification_preferences:
        return []
    return user.notification_preferences.get('backup_codes', [])

