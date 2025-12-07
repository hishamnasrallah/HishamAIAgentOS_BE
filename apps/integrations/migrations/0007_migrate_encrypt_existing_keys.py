"""
Data migration to encrypt existing API keys.

This migration encrypts all existing plain text API keys in the database.
"""

from django.db import migrations
from apps.integrations.utils.encryption import encrypt_api_key, is_encrypted


def encrypt_existing_keys(apps, schema_editor):
    """Encrypt all existing API keys that are not already encrypted."""
    AIPlatform = apps.get_model('integrations', 'AIPlatform')
    
    platforms = AIPlatform.objects.exclude(api_key='')
    encrypted_count = 0
    skipped_count = 0
    error_count = 0
    
    for platform in platforms:
        if not platform.api_key:
            continue
        
        # Check if already encrypted
        if is_encrypted(platform.api_key):
            skipped_count += 1
            continue
        
        try:
            # Encrypt the plain text key
            encrypted_key = encrypt_api_key(platform.api_key)
            platform.api_key = encrypted_key
            platform.save(update_fields=['api_key'])
            encrypted_count += 1
        except Exception as e:
            # Log error but don't fail migration
            print(f"Warning: Failed to encrypt API key for platform {platform.platform_name}: {str(e)}")
            error_count += 1
    
    print(f"Migration complete: {encrypted_count} encrypted, {skipped_count} already encrypted, {error_count} errors")


def reverse_encryption(apps, schema_editor):
    """
    Reverse migration - decrypt keys back to plain text.
    
    WARNING: This will expose API keys in plain text. Only use for testing/rollback.
    """
    from apps.integrations.utils.encryption import decrypt_api_key
    
    AIPlatform = apps.get_model('integrations', 'AIPlatform')
    
    platforms = AIPlatform.objects.exclude(api_key='')
    decrypted_count = 0
    
    for platform in platforms:
        if not platform.api_key:
            continue
        
        try:
            # Decrypt the key
            decrypted_key = decrypt_api_key(platform.api_key)
            platform.api_key = decrypted_key
            platform.save(update_fields=['api_key'])
            decrypted_count += 1
        except Exception:
            # If decryption fails, assume it's already plain text
            pass
    
    print(f"Reversed: {decrypted_count} keys decrypted")


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0006_encrypt_api_keys'),
    ]

    operations = [
        migrations.RunPython(encrypt_existing_keys, reverse_encryption),
    ]

