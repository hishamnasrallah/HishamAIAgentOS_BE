"""
Custom CSRF middleware to disable CSRF for API endpoints.
API endpoints use JWT/API key authentication, so CSRF is not needed.
"""

from django.middleware.csrf import CsrfViewMiddleware
from django.utils.deprecation import MiddlewareMixin


class DisableCSRFForAPI(MiddlewareMixin):
    """
    Disable CSRF protection for API endpoints.
    API endpoints use JWT tokens or API keys for authentication,
    so CSRF protection is not necessary.
    """
    
    def process_request(self, request):
        # Skip CSRF for API endpoints
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None


