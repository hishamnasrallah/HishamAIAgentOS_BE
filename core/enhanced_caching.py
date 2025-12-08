"""
Enhanced Multi-Layer Caching Strategy
Memory + Redis + Database caching with smart invalidation.
"""
import logging
import hashlib
import json
from typing import Any, Optional, Callable
from functools import wraps
from django.core.cache import cache
from django.core.cache.backends.base import BaseCache
from django.conf import settings

logger = logging.getLogger(__name__)

# In-memory cache (process-local)
_memory_cache = {}


class MultiLayerCache:
    """
    Multi-layer caching system:
    1. Memory (fastest, process-local)
    2. Redis (shared across processes)
    3. Database (persistent fallback)
    """
    
    def __init__(self):
        self.memory_ttl = getattr(settings, 'MEMORY_CACHE_TTL', 60)  # 1 minute
        self.redis_ttl = getattr(settings, 'REDIS_CACHE_TTL', 300)  # 5 minutes
        self.db_ttl = getattr(settings, 'DB_CACHE_TTL', 3600)  # 1 hour
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get from cache (memory -> Redis -> DB)."""
        # Try memory first
        if key in _memory_cache:
            data, expiry = _memory_cache[key]
            if expiry is None or expiry > self._now():
                logger.debug(f"Cache HIT (memory): {key}")
                return data
            else:
                # Expired, remove
                del _memory_cache[key]
        
        # Try Redis
        try:
            data = cache.get(key)
            if data is not None:
                logger.debug(f"Cache HIT (Redis): {key}")
                # Also store in memory for faster access
                self._set_memory(key, data, self.memory_ttl)
                return data
        except Exception as e:
            logger.warning(f"Redis cache error for {key}: {e}")
        
        # Try database (if implemented)
        # For now, return default
        logger.debug(f"Cache MISS: {key}")
        return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set in all cache layers."""
        ttl = ttl or self.redis_ttl
        
        # Set in memory
        self._set_memory(key, value, min(ttl, self.memory_ttl))
        
        # Set in Redis
        try:
            cache.set(key, value, ttl)
        except Exception as e:
            logger.warning(f"Failed to set Redis cache for {key}: {e}")
    
    def delete(self, key: str):
        """Delete from all cache layers."""
        # Delete from memory
        _memory_cache.pop(key, None)
        
        # Delete from Redis
        try:
            cache.delete(key)
        except Exception as e:
            logger.warning(f"Failed to delete Redis cache for {key}: {e}")
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        # Clear memory cache matching pattern
        keys_to_delete = [k for k in _memory_cache.keys() if pattern in k]
        for key in keys_to_delete:
            del _memory_cache[key]
        
        # Clear Redis cache matching pattern
        # Note: Redis doesn't support pattern deletion directly
        # Would need to use SCAN or maintain a key registry
        logger.warning("Pattern-based cache clearing not fully implemented for Redis")
    
    def _set_memory(self, key: str, value: Any, ttl: int):
        """Set in memory cache."""
        expiry = self._now() + ttl if ttl else None
        _memory_cache[key] = (value, expiry)
    
    def _now(self) -> int:
        """Get current timestamp."""
        import time
        return int(time.time())


# Global instance
_cache = MultiLayerCache()


def get_cache() -> MultiLayerCache:
    """Get the global cache instance."""
    return _cache


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_parts = []
    for arg in args:
        key_parts.append(str(arg))
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results.
    
    Usage:
        @cached(ttl=600)
        def expensive_function(arg1, arg2):
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key_str = key_func(*args, **kwargs)
            else:
                cache_key_str = f"{func.__module__}.{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = _cache.get(cache_key_str)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            _cache.set(cache_key_str, result, ttl)
            
            return result
        return wrapper
    return decorator


def ai_response_cache(ttl: int = 3600):
    """
    Specialized cache for AI responses.
    Uses content-based hashing for cache keys.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from prompt/content
            prompt = kwargs.get('prompt') or (args[0] if args else '')
            cache_key_str = f"ai_response:{hashlib.sha256(str(prompt).encode()).hexdigest()}"
            
            # Try cache
            cached_result = _cache.get(cache_key_str)
            if cached_result is not None:
                logger.info("AI response cache HIT")
                return cached_result
            
            # Execute
            result = func(*args, **kwargs)
            
            # Cache result
            _cache.set(cache_key_str, result, ttl)
            logger.info("AI response cached")
            
            return result
        return wrapper
    return decorator


class CacheInvalidationStrategy:
    """Cache invalidation strategies."""
    
    @staticmethod
    def invalidate_on_update(model_class, field_name: str = None):
        """Invalidate cache when model is updated."""
        from django.db.models.signals import post_save, post_delete
        
        def invalidate(sender, instance, **kwargs):
            # Generate cache keys to invalidate
            cache_keys = [
                f"{model_class.__name__}:{instance.id}",
                f"{model_class.__name__}:list",
            ]
            
            if field_name:
                cache_keys.append(f"{model_class.__name__}:{field_name}:{getattr(instance, field_name)}")
            
            for key in cache_keys:
                _cache.delete(key)
                logger.info(f"Cache invalidated: {key}")
        
        post_save.connect(invalidate, sender=model_class)
        post_delete.connect(invalidate, sender=model_class)
    
    @staticmethod
    def invalidate_pattern(pattern: str):
        """Invalidate all keys matching pattern."""
        _cache.clear_pattern(pattern)
        logger.info(f"Cache pattern invalidated: {pattern}")

