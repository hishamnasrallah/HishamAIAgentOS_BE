"""
Rate throttling for API keys and users.
"""
from rest_framework.throttling import UserRateThrottle
from django.core.cache import cache
from django.utils import timezone
from .models import APIKey


class APIKeyRateThrottle(UserRateThrottle):
    """
    Custom throttle for API key authentication.
    Uses the rate_limit_per_minute field from APIKey model.
    """
    scope = 'api_key'
    
    def get_rate(self):
        """
        Get rate limit from API key if available, otherwise use default.
        """
        request = getattr(self, 'request', None)
        if request and hasattr(request, 'auth') and isinstance(request.auth, APIKey):
            api_key = request.auth
            # Return rate in format "num/period" (e.g., "60/min")
            return f"{api_key.rate_limit_per_minute}/min"
        # Default rate if no API key
        return '60/min'
    
    def get_cache_key(self, request, view):
        """
        Generate cache key based on API key or user.
        """
        if request.user and request.user.is_authenticated:
            # Use user-based throttling
            ident = request.user.pk
        elif hasattr(request, 'auth') and isinstance(request.auth, APIKey):
            # Use API key-based throttling
            ident = f"apikey_{request.auth.key}"
        else:
            # Anonymous user
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
    
    def throttle_failure(self):
        """
        Called when rate limit is exceeded.
        """
        request = getattr(self, 'request', None)
        if request and hasattr(request, 'auth') and isinstance(request.auth, APIKey):
            api_key = request.auth
            rate_limit = api_key.rate_limit_per_minute
            return f"Rate limit exceeded: {rate_limit} requests per minute"
        return "Rate limit exceeded"


class StrictAPIKeyThrottle(APIKeyRateThrottle):
    """
    Stricter throttle for sensitive endpoints.
    """
    scope = 'strict_api_key'
    
    def get_rate(self):
        """
        Use stricter rate limits for sensitive operations.
        """
        request = getattr(self, 'request', None)
        if request and hasattr(request, 'auth') and isinstance(request.auth, APIKey):
            api_key = request.auth
            # Use 50% of normal rate for sensitive operations
            strict_rate = max(1, api_key.rate_limit_per_minute // 2)
            return f"{strict_rate}/min"
        return '30/min'  # Default strict rate

