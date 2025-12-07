"""
Rate limiter for AI platform requests.

Implements token bucket algorithm using Redis for distributed rate limiting.
"""

from typing import Optional
import time
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter using token bucket algorithm.
    
    Can use Redis for distributed rate limiting or in-memory for single instance.
    """
    
    def __init__(self, redis_client=None):
        """
        Initialize rate limiter.
        
        Args:
            redis_client: Optional Redis client for distributed limiting
        """
        self.redis = redis_client
        self.local_buckets = {}  # Fallback to in-memory if no Redis
    
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 60
    ) -> tuple[bool, int]:
        """
        Check if request is within rate limit.
        
        Args:
            key: Unique identifier for the limit (e.g., 'platform:openai:user:123')
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (allowed: bool, remaining: int)
        """
        if self.redis:
            return await self._check_redis_limit(key, max_requests, window_seconds)
        else:
            return await self._check_local_limit(key, max_requests, window_seconds)
    
    async def _check_redis_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """Check rate limit using Redis."""
        try:
            from asgiref.sync import sync_to_async
            
            current_time = int(time.time())
            window_start = current_time - window_seconds
            
            # Redis key for this limit
            redis_key = f"ratelimit:{key}"
            
            # Remove old entries
            await sync_to_async(self.redis.zremrangebyscore)(
                redis_key, 0, window_start
            )
            
            # Count current requests
            current_count = await sync_to_async(self.redis.zcard)(redis_key)
            
            if current_count >= max_requests:
                return False, 0
            
            # Add new request
            await sync_to_async(self.redis.zadd)(
                redis_key, {str(current_time): current_time}
            )
            
            # Set expiry
            await sync_to_async(self.redis.expire)(redis_key, window_seconds)
            
            remaining = max_requests - (current_count + 1)
            return True, remaining
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {str(e)}")
            # Fallback to allowing request
            return True, max_requests
    
    async def _check_local_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """Check rate limit using local memory (not distributed)."""
        current_time = time.time()
        window_start = current_time - window_seconds
        
        # Get or create bucket
        if key not in self.local_buckets:
            self.local_buckets[key] = []
        
        # Remove old timestamps
        self.local_buckets[key] = [
            ts for ts in self.local_buckets[key]
            if ts > window_start
        ]
        
        current_count = len(self.local_buckets[key])
        
        if current_count >= max_requests:
            return False, 0
        
        # Add new timestamp
        self.local_buckets[key].append(current_time)
        
        remaining = max_requests - (current_count + 1)
        return True, remaining
    
    async def check_platform_limit(
        self,
        platform_name: str,
        user_id: Optional[str] = None
    ) -> tuple[bool, int]:
        """
        Check rate limit for a specific platform.
        
        Args:
            platform_name: Name of the platform
            user_id: Optional user ID for per-user limits
            
        Returns:
            Tuple of (allowed: bool, remaining: int)
        """
        from apps.integrations.models import AIPlatform
        from asgiref.sync import sync_to_async
        
        try:
            platform = await sync_to_async(
                AIPlatform.objects.get
            )(platform_name=platform_name)
            
            # Build rate limit key
            if user_id:
                key = f"platform:{platform_name}:user:{user_id}"
            else:
                key = f"platform:{platform_name}:global"
            
            # Check limit
            return await self.check_rate_limit(
                key,
                platform.rate_limit_per_minute,
                60  # 1 minute window
            )
            
        except Exception as e:
            logger.error(f"Platform rate limit check failed: {str(e)}")
            # Fallback to allowing request
            return True, 999


# Global limiter instance (will use Redis if available)
try:
    from django.core.cache import cache
    redis_client = cache._cache.get_client() if hasattr(cache, '_cache') else None
    limiter = RateLimiter(redis_client)
except Exception:
    # Fallback to local limiter
    limiter = RateLimiter(None)
    logger.warning("Redis not available, using local rate limiter")
