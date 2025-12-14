"""
Custom exception handler and exceptions for HishamOS.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that provides consistent error responses.
    Ensures CORS headers are included even on error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the exception (use warning for validation errors, error for others)
    from rest_framework.exceptions import ValidationError as DRFValidationError
    if isinstance(exc, DRFValidationError) and response and response.status_code == 400:
        # Validation errors are expected - log at warning level
        logger.warning(f"Validation error: {exc}", extra={'context': context})
    else:
        # Other errors should be logged at error level
        logger.error(f"Exception occurred: {exc}", exc_info=True, extra={'context': context})
    
    if response is not None:
        # Extract clean error message from ValidationError
        error_message = str(exc)
        
        # For ValidationError, extract the actual message from ErrorDetail objects
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, list) and len(exc.detail) > 0:
                # Get the first error detail's string
                first_detail = exc.detail[0]
                if hasattr(first_detail, 'string'):
                    error_message = first_detail.string
                elif isinstance(first_detail, str):
                    error_message = first_detail
            elif isinstance(exc.detail, dict):
                # Get first error message from dict
                first_key = next(iter(exc.detail.keys()), None)
                if first_key:
                    first_value = exc.detail[first_key]
                    if isinstance(first_value, list) and len(first_value) > 0:
                        if hasattr(first_value[0], 'string'):
                            error_message = first_value[0].string
                        elif isinstance(first_value[0], str):
                            error_message = first_value[0]
                    elif isinstance(first_value, str):
                        error_message = first_value
        
        # Customize the response format
        custom_response_data = {
            'error': True,
            'message': error_message,
            'details': response.data,
            'status_code': response.status_code
        }
        response.data = custom_response_data
        
        # Ensure CORS headers are added
        _add_cors_headers(response)
    else:
        # Handle Django ValidationError
        if isinstance(exc, DjangoValidationError):
            custom_response_data = {
                'error': True,
                'message': 'Validation error',
                'details': exc.message_dict if hasattr(exc, 'message_dict') else exc.messages,
                'status_code': status.HTTP_400_BAD_REQUEST
            }
            response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
            _add_cors_headers(response)
        else:
            # Handle unhandled exceptions (500 errors)
            custom_response_data = {
                'error': True,
                'message': 'Internal server error',
                'details': str(exc) if settings.DEBUG else 'An unexpected error occurred',
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            _add_cors_headers(response)
    
    return response


def _add_cors_headers(response):
    """
    Add CORS headers to response to ensure they're present even on error responses.
    """
    # Get allowed origins from settings
    allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
    
    # Add CORS headers
    if allowed_origins:
        # In development, allow the common origins
        response['Access-Control-Allow-Origin'] = allowed_origins[0] if len(allowed_origins) == 1 else '*'
    else:
        # Fallback: allow all origins in development
        if settings.DEBUG:
            response['Access-Control-Allow-Origin'] = '*'
    
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'


class AIServiceError(Exception):
    """Base exception for AI service errors."""
    pass


class AgentExecutionError(AIServiceError):
    """Exception raised when agent execution fails."""
    pass


class WorkflowExecutionError(AIServiceError):
    """Exception raised when workflow execution fails."""
    pass


class RateLimitExceededError(AIServiceError):
    """Exception raised when rate limit is exceeded."""
    pass


class InvalidAgentConfigurationError(AIServiceError):
    """Exception raised when agent configuration is invalid."""
    pass


class PlatformUnavailableError(AIServiceError):
    """Exception raised when AI platform is unavailable."""
    pass
