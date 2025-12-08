"""
Secrets Management Service
Supports HashiCorp Vault and local encryption fallback.
"""
import os
import logging
from typing import Optional, Dict, Any
from django.conf import settings
from cryptography.fernet import Fernet
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Try to import hvac (HashiCorp Vault client)
try:
    import hvac
    HVAC_AVAILABLE = True
except ImportError:
    HVAC_AVAILABLE = False
    logger.warning("hvac not installed. HashiCorp Vault integration disabled.")


class SecretsManager:
    """
    Unified secrets management service.
    Supports HashiCorp Vault (primary) and local encryption (fallback).
    """
    
    def __init__(self):
        self.vault_enabled = getattr(settings, 'VAULT_ENABLED', False)
        self.vault_url = getattr(settings, 'VAULT_ADDR', os.getenv('VAULT_ADDR', ''))
        self.vault_token = getattr(settings, 'VAULT_TOKEN', os.getenv('VAULT_TOKEN', ''))
        self.vault_mount_point = getattr(settings, 'VAULT_MOUNT_POINT', 'secret')
        self.use_local_encryption = getattr(settings, 'USE_LOCAL_ENCRYPTION', True)
        
        # Initialize Vault client if enabled
        self.vault_client = None
        if self.vault_enabled and HVAC_AVAILABLE and self.vault_url:
            try:
                self.vault_client = hvac.Client(url=self.vault_url, token=self.vault_token)
                # Verify connection
                if not self.vault_client.is_authenticated():
                    logger.error("Vault authentication failed. Falling back to local encryption.")
                    self.vault_client = None
                    self.vault_enabled = False
                else:
                    logger.info("HashiCorp Vault connection established.")
            except Exception as e:
                logger.error(f"Failed to initialize Vault client: {e}. Falling back to local encryption.")
                self.vault_client = None
                self.vault_enabled = False
        
        # Initialize local encryption if needed
        self.fernet = None
        if not self.vault_enabled and self.use_local_encryption:
            encryption_key = getattr(settings, 'SECRETS_ENCRYPTION_KEY', None)
            if not encryption_key:
                # Generate key from SECRET_KEY if available
                from django.core.management.utils import get_random_secret_key
                encryption_key = Fernet.generate_key()
                logger.warning(
                    "SECRETS_ENCRYPTION_KEY not set. Generated new key. "
                    "Set this in settings for production!"
                )
            else:
                # Ensure key is bytes
                if isinstance(encryption_key, str):
                    encryption_key = encryption_key.encode()
            self.fernet = Fernet(encryption_key)
            logger.info("Local encryption initialized.")
    
    def store_secret(self, path: str, secret: Dict[str, Any], metadata: Optional[Dict] = None) -> bool:
        """
        Store a secret.
        
        Args:
            path: Secret path (e.g., 'api-keys/openai')
            secret: Secret data dictionary
            metadata: Optional metadata
        
        Returns:
            True if successful
        """
        try:
            if self.vault_enabled and self.vault_client:
                # Store in Vault
                vault_path = f"{self.vault_mount_point}/data/{path}"
                self.vault_client.secrets.kv.v2.create_or_update_secret(
                    path=vault_path,
                    secret=secret,
                    mount_point=self.vault_mount_point
                )
                logger.info(f"Secret stored in Vault: {path}")
                return True
            elif self.use_local_encryption and self.fernet:
                # Store encrypted in cache/database
                encrypted_data = self._encrypt_dict(secret)
                cache_key = f"secret:{path}"
                cache.set(cache_key, encrypted_data, timeout=None)  # Permanent
                logger.info(f"Secret stored locally (encrypted): {path}")
                return True
            else:
                logger.error("No secrets storage method available.")
                return False
        except Exception as e:
            logger.error(f"Failed to store secret {path}: {e}")
            return False
    
    def get_secret(self, path: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a secret.
        
        Args:
            path: Secret path
        
        Returns:
            Secret data dictionary or None
        """
        try:
            if self.vault_enabled and self.vault_client:
                # Get from Vault
                vault_path = f"{self.vault_mount_point}/data/{path}"
                response = self.vault_client.secrets.kv.v2.read_secret_version(
                    path=vault_path,
                    mount_point=self.vault_mount_point
                )
                if response and 'data' in response:
                    return response['data'].get('data', {})
                return None
            elif self.use_local_encryption and self.fernet:
                # Get from cache
                cache_key = f"secret:{path}"
                encrypted_data = cache.get(cache_key)
                if encrypted_data:
                    return self._decrypt_dict(encrypted_data)
                return None
            else:
                logger.error("No secrets retrieval method available.")
                return None
        except Exception as e:
            logger.error(f"Failed to retrieve secret {path}: {e}")
            return None
    
    def delete_secret(self, path: str) -> bool:
        """
        Delete a secret.
        
        Args:
            path: Secret path
        
        Returns:
            True if successful
        """
        try:
            if self.vault_enabled and self.vault_client:
                # Delete from Vault
                vault_path = f"{self.vault_mount_point}/data/{path}"
                self.vault_client.secrets.kv.v2.delete_metadata_and_all_versions(
                    path=vault_path,
                    mount_point=self.vault_mount_point
                )
                logger.info(f"Secret deleted from Vault: {path}")
                return True
            elif self.use_local_encryption and self.fernet:
                # Delete from cache
                cache_key = f"secret:{path}"
                cache.delete(cache_key)
                logger.info(f"Secret deleted locally: {path}")
                return True
            else:
                logger.error("No secrets deletion method available.")
                return False
        except Exception as e:
            logger.error(f"Failed to delete secret {path}: {e}")
            return False
    
    def rotate_secret(self, path: str, new_secret: Dict[str, Any]) -> bool:
        """
        Rotate a secret (store new version).
        
        Args:
            path: Secret path
            new_secret: New secret data
        
        Returns:
            True if successful
        """
        try:
            # Store new version
            if self.store_secret(path, new_secret):
                logger.info(f"Secret rotated: {path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to rotate secret {path}: {e}")
            return False
    
    def list_secrets(self, prefix: str = '') -> list:
        """
        List all secrets with given prefix.
        
        Args:
            prefix: Path prefix
        
        Returns:
            List of secret paths
        """
        try:
            if self.vault_enabled and self.vault_client:
                # List from Vault
                vault_path = f"{self.vault_mount_point}/metadata/{prefix}"
                response = self.vault_client.secrets.kv.v2.list_secrets(
                    path=vault_path,
                    mount_point=self.vault_mount_point
                )
                if response and 'data' in response:
                    return response['data'].get('keys', [])
                return []
            else:
                # For local encryption, we'd need to track paths in database
                # For now, return empty list
                logger.warning("List secrets not fully supported for local encryption.")
                return []
        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    def _encrypt_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt a dictionary."""
        if not self.fernet:
            raise ValueError("Fernet not initialized")
        
        encrypted = {}
        for key, value in data.items():
            if isinstance(value, str):
                encrypted[key] = self.fernet.encrypt(value.encode()).decode()
            elif isinstance(value, (int, float, bool)):
                encrypted[key] = value
            else:
                # For complex types, JSON encode then encrypt
                import json
                json_str = json.dumps(value)
                encrypted[key] = self.fernet.encrypt(json_str.encode()).decode()
        return encrypted
    
    def _decrypt_dict(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt a dictionary."""
        if not self.fernet:
            raise ValueError("Fernet not initialized")
        
        decrypted = {}
        for key, value in encrypted_data.items():
            if isinstance(value, str):
                try:
                    decrypted[key] = self.fernet.decrypt(value.encode()).decode()
                except Exception:
                    # Try to decode as JSON
                    try:
                        import json
                        decrypted_bytes = self.fernet.decrypt(value.encode())
                        decrypted[key] = json.loads(decrypted_bytes.decode())
                    except Exception:
                        decrypted[key] = value
            else:
                decrypted[key] = value
        return decrypted


# Global instance
_secrets_manager = None


def get_secrets_manager() -> SecretsManager:
    """Get or create the global secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager

