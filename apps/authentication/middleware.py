"""
Custom authentication middleware for API key authentication and logging.
"""

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import APIKey
from apps.core.services.roles import RoleService
from apps.organizations.services import FeatureService
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class APIKeyAuthentication(BaseAuthentication):
    """
    API Key authentication for external integrations.
    Usage: Add 'X-API-Key: your-api-key' header to requests
    """
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            return None
        
        try:
            key_obj = APIKey.objects.select_related('user').get(
                key=api_key,
                is_active=True
            )
            
            # Check if key is expired
            if key_obj.is_expired():
                raise exceptions.AuthenticationFailed('API key has expired.')
            
            # Check if API access is enabled for the organization
            user = key_obj.user
            organization = RoleService.get_user_organization(user)
            
            if organization:
                # Super admins bypass this check
                if not RoleService.is_super_admin(user):
                    if not FeatureService.is_feature_available(
                        organization, 
                        'ai.api_access', 
                        user=user, 
                        raise_exception=False
                    ):
                        raise exceptions.AuthenticationFailed(
                            'API access is not available for your subscription tier. '
                            'Please upgrade your subscription to use API keys.'
                        )
            
            # Update last used timestamp
            key_obj.update_last_used()
            
            # Return user and key object
            return (key_obj.user, key_obj)
            
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API key.')
    
    def authenticate_header(self, request):
        return 'X-API-Key'


class AuthenticationLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log authentication attempts and API usage.
    """
    
    def process_request(self, request):
        # Log API requests for monitoring
        if request.path.startswith('/api/'):
            user = getattr(request, 'user', None)
            if user and user.is_authenticated:
                logger.info(
                    f"API Request: {request.method} {request.path} "
                    f"by {user.email} (Role: {user.role})"
                )
        
        return None
    
    def process_response(self, request, response):
        # Log failed authentication attempts
        if response.status_code == 401:
            logger.warning(
                f"Unauthorized access attempt: {request.method} {request.path} "
                f"from IP: {self.get_client_ip(request)}"
            )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
