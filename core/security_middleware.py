"""
Security middleware for adding security headers and additional protections.
ASGI-compatible middleware.
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from asgiref.sync import sync_to_async, iscoroutinefunction

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses.
    ASGI-compatible middleware.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Check if get_response is async
        self._is_async = iscoroutinefunction(get_response)
        super().__init__(get_response)
    
    def __call__(self, request):
        if self._is_async:
            return self._async_call(request)
        else:
            return self._sync_call(request)
    
    def _sync_call(self, request):
        """Synchronous middleware call."""
        response = self.get_response(request)
        return self._add_security_headers(response)
    
    async def _async_call(self, request):
        """Asynchronous middleware call."""
        response = await self.get_response(request)
        return self._add_security_headers(response)
    
    def _add_security_headers(self, response):
        """
        Add security headers to response.
        Works with both sync and async responses.
        """
        # Ensure we have a response object, not a coroutine
        if hasattr(response, 'headers'):
            # Content Security Policy
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Allow inline scripts for React
                "style-src 'self' 'unsafe-inline'; "  # Allow inline styles
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https://api.openai.com https://api.anthropic.com https://generativelanguage.googleapis.com; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "upgrade-insecure-requests;"
            )
            
            # X-Content-Type-Options
            response['X-Content-Type-Options'] = 'nosniff'
            
            # X-Frame-Options
            response['X-Frame-Options'] = 'DENY'
            
            # X-XSS-Protection
            response['X-XSS-Protection'] = '1; mode=block'
            
            # Referrer Policy
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Permissions Policy (formerly Feature Policy)
            response['Permissions-Policy'] = (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=()"
            )
            
            # Remove server header (if not already removed)
            if 'Server' in response:
                del response['Server']
        
        return response
    
    def process_response(self, request, response):
        """Legacy sync method for compatibility."""
        return self._add_security_headers(response)


class RequestThrottlingMiddleware(MiddlewareMixin):
    """
    Basic request throttling middleware to prevent abuse.
    Uses Redis cache for distributed rate limiting.
    ASGI-compatible middleware.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 100  # requests per minute
        self.window = 60  # seconds
        # Check if get_response is async
        self._is_async = iscoroutinefunction(get_response)
        super().__init__(get_response)
    
    def __call__(self, request):
        if self._is_async:
            return self._async_call(request)
        else:
            return self._sync_call(request)
    
    def _sync_call(self, request):
        """Synchronous middleware call."""
        # Check throttling
        throttle_response = self._check_throttle(request)
        if throttle_response:
            return throttle_response
        return self.get_response(request)
    
    async def _async_call(self, request):
        """Asynchronous middleware call."""
        # Check throttling
        throttle_response = await self._check_throttle_async(request)
        if throttle_response:
            return throttle_response
        return await self.get_response(request)
    
    def _check_throttle(self, request):
        """
        Check if request should be throttled (sync).
        """
        # Skip throttling for health checks and static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
        
        if request.path == '/api/v1/monitoring/health/':
            return None
        
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Check rate limit using cache
        try:
            from django.core.cache import cache
            cache_key = f"throttle:{ip}"
            request_count = cache.get(cache_key, 0)
            
            if request_count >= self.rate_limit:
                from django.http import HttpResponse
                response = HttpResponse(
                    "Rate limit exceeded. Please try again later.",
                    status=429
                )
                response['Retry-After'] = str(self.window)
                return response
            
            # Increment counter
            cache.set(cache_key, request_count + 1, self.window)
        except Exception as e:
            logger.warning(f"Error in request throttling: {e}")
            # Continue if cache is unavailable
        
        return None
    
    async def _check_throttle_async(self, request):
        """
        Check if request should be throttled (async).
        """
        # Skip throttling for health checks and static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
        
        if request.path == '/api/v1/monitoring/health/':
            return None
        
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Check rate limit using cache (async)
        try:
            from django.core.cache import cache
            cache_key = f"throttle:{ip}"
            # Use sync_to_async for cache operations
            request_count = await sync_to_async(cache.get)(cache_key, 0)
            
            if request_count >= self.rate_limit:
                from django.http import HttpResponse
                response = HttpResponse(
                    "Rate limit exceeded. Please try again later.",
                    status=429
                )
                response['Retry-After'] = str(self.window)
                return response
            
            # Increment counter (async)
            await sync_to_async(cache.set)(cache_key, request_count + 1, self.window)
        except Exception as e:
            logger.warning(f"Error in request throttling: {e}")
            # Continue if cache is unavailable
        
        return None
    
    def process_request(self, request):
        """Legacy sync method for compatibility."""
        return self._check_throttle(request)
    
    def get_client_ip(self, request):
        """
        Get client IP address from request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

