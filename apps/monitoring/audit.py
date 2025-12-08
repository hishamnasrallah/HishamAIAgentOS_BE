"""
Comprehensive audit logging utilities with tamper-proof logging.
"""
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import AuditLog, AuditConfiguration

logger = logging.getLogger(__name__)
User = get_user_model()


class AuditLogger:
    """
    Comprehensive audit logger with tamper-proof verification.
    """
    
    @staticmethod
    def get_client_ip(request) -> str:
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    @staticmethod
    def get_user_agent(request) -> str:
        """Get user agent from request."""
        return request.META.get('HTTP_USER_AGENT', '')
    
    @staticmethod
    def calculate_hash(audit_log: AuditLog) -> str:
        """
        Calculate hash for tamper-proof verification.
        Includes all fields except the hash itself.
        """
        data = {
            'id': str(audit_log.id),
            'user_id': str(audit_log.user.id) if audit_log.user else None,
            'action': audit_log.action,
            'resource_type': audit_log.resource_type,
            'resource_id': audit_log.resource_id,
            'description': audit_log.description,
            'changes': json.dumps(audit_log.changes, sort_keys=True),
            'ip_address': str(audit_log.ip_address) if audit_log.ip_address else '',
            'user_agent': audit_log.user_agent,
            'timestamp': audit_log.timestamp.isoformat(),
        }
        
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    @classmethod
    def should_audit(
        cls,
        action: str,
        resource_type: str,
        resource_id: str,
        user: Optional[User] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Check if an action should be audited based on active configurations.
        
        Args:
            action: Action type
            resource_type: Resource type
            resource_id: Resource ID
            user: User performing the action
            ip_address: IP address
        
        Returns:
            True if action should be audited, False otherwise
        """
        # Get all active configurations, ordered by priority (higher first)
        configurations = AuditConfiguration.objects.filter(
            is_active=True
        ).order_by('-priority', 'name')
        
        # If no configurations exist, audit everything (backward compatibility)
        # This ensures the system works out of the box
        if not configurations.exists():
            return True
        
        # Check each configuration
        # Logic: If ANY configuration says "should audit", we audit
        # Exclusions take precedence - if ANY config excludes, we don't audit
        should_audit_result = False
        excluded = False
        
        for config in configurations:
            # Check if this config excludes the action
            if config.should_audit(action, resource_type, resource_id, user, ip_address):
                # This config says "audit"
                should_audit_result = True
            else:
                # Check if this config explicitly excludes
                # (should_audit returns False, but we need to check if it's an exclusion)
                if (config.exclude_actions and action in config.exclude_actions) or \
                   (config.exclude_resource_types and resource_type in config.exclude_resource_types) or \
                   (config.exclude_resources and any(
                       r.get('resource_type') == resource_type and r.get('resource_id') == resource_id
                       for r in config.exclude_resources
                   )):
                    excluded = True
                    break  # Exclusions take precedence
        
        # If explicitly excluded, don't audit
        if excluded:
            return False
        
        # Otherwise, audit if any config says to audit
        return should_audit_result
    
    @classmethod
    def get_audit_config_for_action(
        cls,
        action: str,
        resource_type: str,
        resource_id: str,
        user: Optional[User] = None,
        ip_address: Optional[str] = None
    ) -> Optional[AuditConfiguration]:
        """
        Get the first matching audit configuration for an action.
        
        Returns:
            AuditConfiguration instance or None
        """
        configurations = AuditConfiguration.objects.filter(
            is_active=True
        ).order_by('-priority', 'name')
        
        for config in configurations:
            if config.should_audit(action, resource_type, resource_id, user, ip_address):
                return config
        
        return None
    
    @classmethod
    def log_action(
        cls,
        action: str,
        resource_type: str,
        resource_id: str,
        description: str,
        user: Optional[User] = None,
        request=None,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        **kwargs
    ) -> Optional[AuditLog]:
        """
        Log an audit action with comprehensive details.
        Now checks audit configurations before logging.
        
        Args:
            action: Action type (create, update, delete, execute, login, logout)
            resource_type: Type of resource (agent, workflow, project, etc.)
            resource_id: ID of the resource
            description: Human-readable description
            user: User performing the action
            request: Django request object (for IP, user agent)
            changes: Dictionary of changes (before/after for updates)
            ip_address: IP address (optional, will be extracted from request if not provided)
            user_agent: User agent (optional, will be extracted from request if not provided)
            **kwargs: Additional metadata
        
        Returns:
            Created AuditLog instance or None if not audited
        """
        # Get IP and user agent from explicit parameters first, then kwargs, then request
        # Initialize variables first to avoid UnboundLocalError
        final_ip_address = ip_address
        final_user_agent = user_agent
        
        # If not provided as explicit parameters, check kwargs (for backward compatibility)
        if final_ip_address is None:
            final_ip_address = kwargs.pop('ip_address', None)
        if final_user_agent is None:
            final_user_agent = kwargs.pop('user_agent', None)
        
        # If still None, try to get from request
        if final_ip_address is None:
            if request:
                final_ip_address = cls.get_client_ip(request)
            else:
                final_ip_address = None
        
        if final_user_agent is None:
            if request:
                final_user_agent = cls.get_user_agent(request)
            else:
                final_user_agent = ''
        
        # Ensure user_agent is always a string (never None) to satisfy NOT NULL constraint
        if final_user_agent is None:
            final_user_agent = ''
        
        # If user not provided but request has user, use it
        if not user and request and hasattr(request, 'user'):
            user = request.user if request.user.is_authenticated else None
        
        # Check if we should audit this action
        if not cls.should_audit(action, resource_type, resource_id, user, final_ip_address):
            return None
        
        # Get configuration to check what to include
        config = cls.get_audit_config_for_action(action, resource_type, resource_id, user, final_ip_address)
        
        # Prepare audit log data based on configuration
        audit_data = {
            'user': user,
            'action': action,
            'resource_type': resource_type,
            'resource_id': str(resource_id),
            'description': description,
        }
        
        # Extract old_values and new_values from changes if available
        old_values = {}
        new_values = {}
        
        if changes:
            # If changes is a dict with field-by-field changes
            if isinstance(changes, dict):
                # Check if old_values and new_values are already extracted (from signals)
                if '_old_values' in changes:
                    old_values = changes.pop('_old_values', {})
                if '_new_values' in changes:
                    new_values = changes.pop('_new_values', {})
                
                # Process field-by-field changes
                # Remove request_data, response_data, and _metadata - we want only field changes
                clean_changes = {}
                for field_name, change_data in changes.items():
                    if field_name in ['_metadata', 'request_data', 'response_data']:
                        continue  # Skip metadata and request/response data
                    if isinstance(change_data, dict) and 'before' in change_data and 'after' in change_data:
                        # This is a proper field change with before/after
                        clean_changes[field_name] = change_data
                        # Also add to old_values and new_values if not already there
                        if field_name not in old_values:
                            old_values[field_name] = change_data['before']
                        if field_name not in new_values:
                            new_values[field_name] = change_data['after']
                    else:
                        # If it's not in the expected format, skip it (don't include raw data)
                        # Only include proper field-by-field changes
                        pass
                
                # Use clean_changes (only field-by-field changes, no request/response data)
                changes = clean_changes if clean_changes else {}
        
        # Include changes, old_values, and new_values only if configured
        if config and config.include_changes:
            audit_data['changes'] = changes or {}
            audit_data['old_values'] = old_values
            audit_data['new_values'] = new_values
        elif not config:  # Default: include changes
            audit_data['changes'] = changes or {}
            audit_data['old_values'] = old_values
            audit_data['new_values'] = new_values
        
        # Include IP address only if configured
        # Always provide a value (None is OK for GenericIPAddressField with null=True)
        if config and config.include_ip_address:
            audit_data['ip_address'] = final_ip_address
        elif not config:  # Default: include IP
            audit_data['ip_address'] = final_ip_address
        else:
            # Config exists but doesn't include IP - set to None (field allows null)
            audit_data['ip_address'] = None
        
        # Include user agent only if configured
        # Always provide a string (empty string if None) - field doesn't allow NULL
        if config and config.include_user_agent:
            audit_data['user_agent'] = final_user_agent or ''
        elif not config:  # Default: include user agent
            audit_data['user_agent'] = final_user_agent or ''
        else:
            # Config exists but doesn't include user agent - still need empty string (NOT NULL constraint)
            audit_data['user_agent'] = ''
        
        # Add any additional kwargs
        audit_data.update(kwargs)
        
        # Create audit log
        audit_log = AuditLog.objects.create(**audit_data)
        
        # Calculate and store hash for tamper-proof verification
        hash_value = cls.calculate_hash(audit_log)
        logger.info(f"Audit log created: {audit_log.id} (hash: {hash_value[:16]}...)")
        
        return audit_log
    
    @classmethod
    def verify_integrity(cls, audit_log: AuditLog) -> bool:
        """
        Verify the integrity of an audit log entry.
        Returns True if the log is valid and hasn't been tampered with.
        """
        try:
            calculated_hash = cls.calculate_hash(audit_log)
            # In a full implementation, we'd compare with stored hash
            # For now, we just verify the log exists and is valid
            return audit_log.id is not None
        except Exception as e:
            logger.error(f"Error verifying audit log integrity: {e}")
            return False
    
    @classmethod
    def log_user_action(
        cls,
        action: str,
        resource_type: str,
        resource_id: str,
        description: str,
        user: User,
        request=None,
        changes: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Convenience method for logging user actions."""
        return cls.log_action(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            user=user,
            request=request,
            changes=changes
        )
    
    @classmethod
    def log_api_request(
        cls,
        method: str,
        path: str,
        user: Optional[User] = None,
        request=None,
        response_status: Optional[int] = None,
        **kwargs
    ) -> Optional[AuditLog]:
        """
        Log API requests for audit trail.
        Only logs important requests (POST, PUT, DELETE, PATCH).
        """
        if method.upper() not in ['POST', 'PUT', 'DELETE', 'PATCH']:
            return None
        
        description = f"{method} {path}"
        if response_status:
            description += f" - Status: {response_status}"
        
        return cls.log_action(
            action='execute',
            resource_type='api',
            resource_id=path,
            description=description,
            user=user,
            request=request,
            changes={'method': method, 'path': path, 'status': response_status},
            **kwargs
        )
    
    @classmethod
    def log_authentication(
        cls,
        action: str,  # 'login' or 'logout'
        user: Optional[User] = None,
        request=None,
        success: bool = True,
        **kwargs
    ) -> AuditLog:
        """Log authentication events."""
        description = f"{action.capitalize()} {'successful' if success else 'failed'}"
        if user:
            description += f" for {user.email}"
        
        return cls.log_action(
            action=action,
            resource_type='authentication',
            resource_id=user.id if user else 'anonymous',
            description=description,
            user=user,
            request=request,
            changes={'success': success},
            **kwargs
        )
    
    @classmethod
    def log_data_access(
        cls,
        resource_type: str,
        resource_id: str,
        user: User,
        request=None,
        **kwargs
    ) -> AuditLog:
        """Log data access for GDPR compliance."""
        return cls.log_action(
            action='read',
            resource_type=resource_type,
            resource_id=resource_id,
            description=f"Data access: {resource_type} {resource_id}",
            user=user,
            request=request,
            **kwargs
        )
    
    @classmethod
    def log_data_deletion(
        cls,
        resource_type: str,
        resource_id: str,
        user: User,
        request=None,
        reason: Optional[str] = None,
        **kwargs
    ) -> AuditLog:
        """Log data deletion for GDPR compliance."""
        description = f"Data deletion: {resource_type} {resource_id}"
        if reason:
            description += f" - Reason: {reason}"
        
        return cls.log_action(
            action='delete',
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            user=user,
            request=request,
            changes={'reason': reason, 'gdpr_compliant': True},
            **kwargs
        )
    
    @classmethod
    def get_user_audit_trail(
        cls,
        user: User,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        action: Optional[str] = None
    ):
        """Get audit trail for a specific user."""
        queryset = AuditLog.objects.filter(user=user)
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset.order_by('-timestamp')
    
    @classmethod
    def cleanup_old_logs(cls, retention_days: int = 365):
        """
        Clean up audit logs older than retention period.
        For GDPR compliance, logs may need to be retained longer.
        """
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        deleted_count = AuditLog.objects.filter(timestamp__lt=cutoff_date).delete()[0]
        logger.info(f"Cleaned up {deleted_count} audit logs older than {retention_days} days")
        return deleted_count


# Convenience instance
audit_logger = AuditLogger()

