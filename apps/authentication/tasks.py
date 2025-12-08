"""
Celery tasks for authentication app.
"""

import logging
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
    
    @shared_task
    def cleanup_expired_tokens():
        """Clean up expired JWT refresh tokens."""
        try:
            from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
            
            # Find expired tokens
            expired_tokens = OutstandingToken.objects.filter(
                expires_at__lt=timezone.now()
            )
            
            count = expired_tokens.count()
            expired_tokens.delete()
            
            logger.info(f"Cleaned up {count} expired tokens")
            return count
        except ImportError:
            logger.warning("JWT token blacklist not configured")
            return 0
        except Exception as e:
            logger.error(f"Error cleaning up tokens: {e}")
            return 0
except ImportError:
    logger.warning("Celery not available for authentication tasks")

