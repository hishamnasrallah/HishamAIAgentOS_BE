"""
DRF mixins for audit logging.
"""

from rest_framework.viewsets import ViewSetMixin


class AuditLoggingMixin(ViewSetMixin):
    """
    Mixin to ensure user is set in thread-local for audit logging signals.
    This runs after DRF authentication but before the view action.
    """
    
    def initial(self, request, *args, **kwargs):
        """Set user in thread-local after authentication."""
        super().initial(request, *args, **kwargs)
        
        # Set user in thread-local for signals
        try:
            from apps.monitoring.middleware import _thread_locals
            
            # Update user if authenticated
            if hasattr(request, 'user') and request.user.is_authenticated:
                _thread_locals.user = request.user
            
            # Always update IP and user agent (ensure they're set for signals)
            from apps.monitoring.middleware import AuditLoggingMiddleware
            _thread_locals.request_ip = AuditLoggingMiddleware.get_client_ip(request)
            _thread_locals.request_user_agent = AuditLoggingMiddleware.get_user_agent(request)
        except Exception:
            pass

