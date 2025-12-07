"""
API Key Encryption Utility for HishamOS.

Uses Fernet (symmetric encryption) from the cryptography library to encrypt
API keys at rest. The encryption key is derived from Django's SECRET_KEY.
"""

import base64
import hashlib
import logging
from typing import Optional

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

# Cache for the Fernet instance
_fernet_instance: Optional[Fernet] = None


def get_encryption_key() -> bytes:
    """
    Generate encryption key from Django SECRET_KEY.
    
    Uses SHA256 hash of SECRET_KEY to create a 32-byte key,
    then base64 encodes it for Fernet compatibility.
    
    Returns:
        bytes: 32-byte encryption key suitable for Fernet
        
    Raises:
        ImproperlyConfigured: If SECRET_KEY is not set or is the default dev key
    """
    secret_key = settings.SECRET_KEY
    
    # Warn if using default dev key in production
    if secret_key == 'django-insecure-dev-key-CHANGE-IN-PRODUCTION':
        logger.warning(
            "Using default SECRET_KEY for encryption! "
            "This is insecure for production. Set DJANGO_SECRET_KEY environment variable."
        )
    
    # Generate deterministic key from SECRET_KEY
    # Use SHA256 to get 32 bytes, then base64 encode for Fernet
    key_material = hashlib.sha256(secret_key.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_material)
    
    return fernet_key


def get_fernet() -> Fernet:
    """
    Get or create Fernet instance for encryption/decryption.
    
    Returns:
        Fernet: Configured Fernet instance
    """
    global _fernet_instance
    
    if _fernet_instance is None:
        encryption_key = get_encryption_key()
        _fernet_instance = Fernet(encryption_key)
    
    return _fernet_instance


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for storage.
    
    Args:
        api_key: Plain text API key to encrypt
        
    Returns:
        str: Encrypted API key (base64 encoded)
        
    Raises:
        ValueError: If api_key is empty or None
    """
    if not api_key:
        raise ValueError("API key cannot be empty")
    
    try:
        fernet = get_fernet()
        encrypted_bytes = fernet.encrypt(api_key.encode())
        # Return as string for database storage
        return encrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to encrypt API key: {str(e)}")
        raise ValueError(f"Encryption failed: {str(e)}")


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an API key for use.
    
    Args:
        encrypted_key: Encrypted API key (from database)
        
    Returns:
        str: Decrypted plain text API key
        
    Raises:
        ValueError: If decryption fails or key is invalid
    """
    if not encrypted_key:
        return ""
    
    # Check if key is already plain text (for migration compatibility)
    # Plain text keys typically don't start with 'gAAAAAB' (Fernet prefix)
    if not encrypted_key.startswith('gAAAAAB'):
        # Likely plain text, return as-is (for backward compatibility during migration)
        logger.warning("Decrypting what appears to be plain text key - migration may be needed")
        return encrypted_key
    
    try:
        fernet = get_fernet()
        decrypted_bytes = fernet.decrypt(encrypted_key.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to decrypt API key: {str(e)}")
        # If decryption fails, try returning as-is (might be plain text)
        logger.warning("Decryption failed, returning key as-is (may be plain text)")
        return encrypted_key


def is_encrypted(api_key: str) -> bool:
    """
    Check if an API key is encrypted.
    
    Args:
        api_key: API key to check
        
    Returns:
        bool: True if key appears to be encrypted
    """
    if not api_key:
        return False
    
    # Fernet encrypted strings start with 'gAAAAAB'
    return api_key.startswith('gAAAAAB')

