"""
Audit logging middleware for automatic audit trail.
Intercepts all API requests and logs them based on audit configurations.
"""

import logging
import threading
from typing import Optional, Tuple
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from rest_framework.request import Request as DRFRequest
from .audit import audit_logger

logger = logging.getLogger(__name__)
User = get_user_model()

# Thread-local storage for user context and audit flags (used by signals)
_thread_locals = threading.local()


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log API requests for audit trail.
    Works with DRF and regular Django views.
    """
    
    def process_request(self, request):
        """Store user, IP, and user agent in thread-local for signals to access."""
        try:
            # Store IP and user agent immediately (always available)
            _thread_locals.request_ip = AuditLoggingMiddleware.get_client_ip(request)
            _thread_locals.request_user_agent = AuditLoggingMiddleware.get_user_agent(request)
            
            # Try to get user - but DRF authentication happens in views, not middleware
            # So we'll update it in process_response as well
            user = None
            if hasattr(request, 'user'):
                # Check if it's an AnonymousUser or actual user
                if hasattr(request.user, 'is_authenticated') and request.user.is_authenticated:
                    user = request.user
                elif hasattr(request.user, 'id'):  # Might be a user object but not authenticated yet
                    user = request.user
            
            # Store user in thread-local (will be updated in process_response if authentication happened)
            _thread_locals.user = user
            
            # For API write operations, determine if this is a model operation
            # Model operations are handled by signals, non-model operations by middleware
            if request.method.upper() in ['POST', 'PUT', 'PATCH', 'DELETE']:
                if request.path.startswith('/api/'):
                    # Dynamically check if this looks like a model endpoint
                    # Model endpoints typically have: /api/v1/app_name/resource_name/id/
                    path = request.path.replace('/api/v1/', '').replace('/api/', '')
                    parts = [p for p in path.split('/') if p]
                    
                    # Check if this is a model operation
                    # Model operations have patterns like:
                    # - /api/v1/resource/id/ (2 parts: resource, id)
                    # - /api/v1/app/resource/id/ (3 parts: app, resource, id)
                    # - /api/v1/auth/users/id/ (3 parts: auth, users, id)
                    is_model_operation = False
                    action_endpoints = ['activate', 'deactivate', 'export', 'import', 'activity', 'me', 'bulk_activate', 'bulk_deactivate', 'login', 'logout', 'register']
                    
                    if len(parts) >= 2:
                        # Check the last part (could be ID) or second-to-last if last is empty
                        # For paths like /api/v1/auth/users/id/, parts = ['auth', 'users', 'id']
                        # For paths like /api/v1/users/id/, parts = ['users', 'id']
                        
                        # Check if any part after the first looks like an ID
                        for i in range(1, len(parts)):
                            potential_id = parts[i]
                            # Remove trailing slash if present
                            if potential_id.endswith('/'):
                                potential_id = potential_id[:-1]
                            
                            # Skip if it's a known action endpoint
                            if potential_id in action_endpoints:
                                continue
                            
                            # Check if it looks like an ID (UUID has dashes, or it's numeric, or long string)
                            looks_like_id = (
                                '-' in potential_id or  # UUID format
                                potential_id.isdigit() or  # Numeric ID
                                len(potential_id) > 10  # Long string (likely UUID without dashes)
                            )
                            
                            if looks_like_id:
                                is_model_operation = True
                                break
                    
                    if not is_model_operation:
                        # Non-model operation (custom endpoints, actions, etc.) - middleware will log it
                        _thread_locals.audit_logged_by_middleware = True
        except Exception:
            _thread_locals.user = None
            _thread_locals.request_ip = None
            _thread_locals.request_user_agent = None
        
        return None
    
    def process_response(self, request, response):
        """
        Process response and log audit events for write operations.
        Only logs successful operations (2xx status codes).
        """
        # Only log write operations
        if request.method.upper() not in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Clear thread-local for non-write operations (but keep IP/user agent for signals)
            # Don't clear IP and user agent - they might be needed for other operations
            try:
                if hasattr(_thread_locals, 'user'):
                    delattr(_thread_locals, 'user')
                if hasattr(_thread_locals, 'audit_logged_by_middleware'):
                    delattr(_thread_locals, 'audit_logged_by_middleware')
            except AttributeError:
                pass
            return response
        
        # Only log successful operations
        if not (200 <= response.status_code < 300):
            return response
        
        # Skip certain paths (static files, admin login, etc.)
        skip_paths = [
            '/admin/login/',
            '/admin/logout/',
            '/api-auth/',
            '/static/',
            '/media/',
            '/api/schema/',
            '/api/docs/',
            '/api/redoc/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return response
        
        try:
            # Update user in thread-local (authentication happens in middleware chain)
            # This ensures signals have the correct user
            user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            elif hasattr(request, 'auth') and request.auth:
                # Try to get user from JWT token
                if hasattr(request.auth, 'user_id'):
                    try:
                        user = User.objects.get(id=request.auth.user_id)
                    except User.DoesNotExist:
                        pass
            
            # Update thread-local user (in case it wasn't set in process_request)
            if user:
                _thread_locals.user = user
            
            # Check if this is a model operation - if so, signals will handle it
            # Don't log here to avoid duplicates and get better change tracking from signals
            if hasattr(_thread_locals, 'audit_logged_by_middleware'):
                # This is a non-model operation that middleware should log
                # Determine resource type and ID from URL and response
                resource_type, resource_id = self._extract_resource_info(request, response)
                
                if not resource_type:
                    # Can't determine resource, skip
                    return response
                
                # Determine action from HTTP method
                action = self._get_action_from_method(request.method)
                
                # Get request data for changes (if available)
                changes = self._extract_changes(request, response)
                
                # Add metadata to changes dict
                if changes:
                    changes['_metadata'] = {
                        'path': request.path,
                        'method': request.method,
                        'status_code': response.status_code,
                    }
                else:
                    changes = {
                        '_metadata': {
                            'path': request.path,
                            'method': request.method,
                            'status_code': response.status_code,
                        }
                    }
                
                # Log the action (for non-model operations only)
                audit_logger.log_action(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id or 'unknown',
                    description=f"{request.method} {request.path}",
                    user=user,
                    request=request,
                    changes=changes,
                )
            else:
                # This is a model operation - signals will handle it with better description and changes
                # Skip middleware logging to avoid duplicates
                # Signals will log with:
                # - Better description: "Update user: email@example.com"
                # - Field-by-field changes: {"first_name": {"before": "old", "after": "new"}}
                # - Complete old_values and new_values
                return response
            
        except Exception as e:
            # Don't break the request if audit logging fails
            logger.error(f"Error in audit logging middleware: {e}", exc_info=True)
        finally:
            # Don't clear thread-local values here - signals might still need them
            # Signals fire during view processing (before process_response completes)
            # Only clear the middleware flag
            # Keep IP, user agent, and user for signals to use
            try:
                if hasattr(_thread_locals, 'audit_logged_by_middleware'):
                    delattr(_thread_locals, 'audit_logged_by_middleware')
                # DO NOT clear request_ip, request_user_agent, or user here
                # They're needed by signals and will be cleared at request end
            except AttributeError:
                pass
        
        return response
    
    def _extract_resource_info(self, request, response=None) -> Tuple[Optional[str], Optional[str]]:
        """
        Dynamically extract resource type and ID from request path or response.
        Works for any model endpoint without hardcoding model names.
        
        Examples:
        - /api/v1/auth/users/123/ -> ('user', '123')
        - /api/v1/projects/abc-123/ -> ('project', 'abc-123')
        - /api/v1/agents/ -> ('agent', None)
        """
        path = request.path
        
        # Remove API prefix
        if path.startswith('/api/v1/'):
            path = path.replace('/api/v1/', '')
        elif path.startswith('/api/'):
            path = path.replace('/api/', '')
        
        # Split path into parts
        parts = [p for p in path.split('/') if p]
        
        if not parts:
            return None, None
        
        # Skip common prefixes that aren't resource types
        skip_prefixes = ['auth', 'monitoring', 'api', 'v1']
        
        # Find the resource type (first non-skipped part that's not an action)
        resource_type = None
        resource_id = None
        resource_index = -1
        
        # Known action endpoints (not resource types)
        action_endpoints = ['activate', 'deactivate', 'export', 'import', 'activity', 'me', 'bulk_activate', 'bulk_deactivate', 'login', 'logout', 'register', 'token', 'refresh']
        
        # Find the resource type - it's typically the last meaningful part before an ID
        for i, part in enumerate(parts):
            if part not in skip_prefixes and part not in action_endpoints:
                # This could be a resource type
                # Check if next part looks like an ID
                if i + 1 < len(parts):
                    next_part = parts[i + 1]
                    if next_part.endswith('/'):
                        next_part = next_part[:-1]
                    
                    # If next part looks like an ID, current part is resource type
                    if '-' in next_part or next_part.isdigit() or len(next_part) > 10:
                        resource_type = part.rstrip('s')  # Remove plural 's' (users -> user)
                        resource_id = next_part
                        resource_index = i
                        break
                else:
                    # Last part, might be resource type for list endpoints
                    resource_type = part.rstrip('s')
                    resource_index = i
                    break
        
        # If we found resource type but no ID, try to get ID from response
        if resource_type and not resource_id:
            if response and hasattr(response, 'data') and isinstance(response.data, dict):
                # Check if response has an 'id' field (common in DRF responses)
                if 'id' in response.data:
                    resource_id = str(response.data['id'])
        
        return resource_type, resource_id
    
    def _get_action_from_method(self, method: str) -> str:
        """Map HTTP method to audit action."""
        method = method.upper()
        mapping = {
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
        }
        return mapping.get(method, 'execute')
    
    def _extract_changes(self, request, response) -> dict:
        """
        Extract changes from request/response for audit log.
        """
        changes = {}
        
        try:
            # Try to get request data
            if hasattr(request, 'data'):
                # DRF request
                request_data = request.data
                if isinstance(request_data, dict):
                    # Filter out sensitive fields
                    sensitive_fields = ['password', 'token', 'secret', 'key', 'api_key']
                    changes['request_data'] = {
                        k: v for k, v in request_data.items()
                        if k not in sensitive_fields
                    }
            elif hasattr(request, 'POST'):
                # Regular Django request
                post_data = dict(request.POST)
                sensitive_fields = ['password', 'token', 'secret', 'key', 'api_key']
                changes['request_data'] = {
                    k: v for k, v in post_data.items()
                    if k not in sensitive_fields
                }
            
            # Try to get response data
            if hasattr(response, 'data'):
                # DRF response
                response_data = response.data
                if isinstance(response_data, dict):
                    changes['response_data'] = response_data
            
        except Exception as e:
            logger.debug(f"Could not extract changes: {e}")
        
        return changes
    
    @staticmethod
    def get_client_ip(request) -> Optional[str]:
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_user_agent(request) -> str:
        """Get user agent from request."""
        return request.META.get('HTTP_USER_AGENT', '')

