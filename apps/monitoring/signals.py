"""
Django signals for automatic audit logging on model changes.
Automatically logs create, update, and delete operations for all models.
"""

import logging
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .audit import audit_logger

logger = logging.getLogger(__name__)
User = get_user_model()

# Store old values for change tracking
_model_old_values = {}

# Models to exclude from automatic auditing (system models, etc.)
EXCLUDED_MODELS = [
    'Session',
    'LogEntry',  # Django admin log
    'ContentType',
    'Permission',
    'Group',
    'AuditLog',  # Don't audit audit logs themselves
    'AuditConfiguration',  # Don't audit audit configurations
    'SystemMetric',
    'HealthCheck',
]


def get_model_name(model_instance) -> str:
    """Get a clean model name for audit logging."""
    # Get the model's app label and model name
    content_type = ContentType.objects.get_for_model(model_instance.__class__)
    model_name = content_type.model
    
    # Convert to a more readable format
    # e.g., 'user' instead of 'authentication.user'
    return model_name


@receiver(pre_save)
def set_tracking_fields(sender, instance, **kwargs):
    """
    Automatically set created_by and updated_by fields before save.
    Also captures old values for change tracking.
    """
    try:
        # Skip excluded models
        model_name = get_model_name(instance)
        if model_name.lower() in [m.lower() for m in EXCLUDED_MODELS]:
            return
        
        # Skip if this is a migration or fixture load
        if kwargs.get('raw', False):
            return
        
        # Get current user from thread-local storage (set by middleware or admin)
        current_user = None
        try:
            from apps.monitoring.middleware import _thread_locals
            if hasattr(_thread_locals, 'user'):
                current_user = getattr(_thread_locals, 'user', None)
        except Exception:
            pass
        
        # Set created_by and updated_by if model has these fields
        if hasattr(instance, 'created_by') or hasattr(instance, 'updated_by'):
            # Only proceed if current_user is authenticated (not AnonymousUser)
            if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                is_new = not (hasattr(instance, 'pk') and instance.pk)
                
                # Set created_by for new instances
                if is_new and hasattr(instance, 'created_by'):
                    if instance.created_by is None:  # Only set if not already set
                        instance.created_by = current_user
                
                # Set updated_by for all saves (new and existing)
                if hasattr(instance, 'updated_by'):
                    instance.updated_by = current_user
        
        # Capture old values for updates (for audit logging)
        if hasattr(instance, 'pk') and instance.pk:
            try:
                # Get the old instance from database
                old_instance = sender.objects.get(pk=instance.pk)
                old_values = {}
                
                # Capture all field values
                for field in instance._meta.fields:
                    if field.name not in ['id', 'pk']:
                        try:
                            value = getattr(old_instance, field.name)
                            # Convert to serializable format
                            if hasattr(value, 'isoformat'):  # DateTime
                                value = value.isoformat()
                            elif hasattr(value, '__str__'):
                                value = str(value)
                            old_values[field.name] = value
                        except Exception:
                            pass
                
                # Store old values with instance ID as key
                key = f"{model_name}_{instance.pk}"
                _model_old_values[key] = old_values
            except sender.DoesNotExist:
                # New instance, no old values
                pass
    except Exception as e:
        logger.debug(f"Error in set_tracking_fields: {e}")


@receiver(post_save)
def audit_model_save(sender, instance, created, **kwargs):
    """
    Automatically log model create/update operations.
    """
    try:
        # Skip excluded models
        model_name = get_model_name(instance)
        if model_name.lower() in [m.lower() for m in EXCLUDED_MODELS]:
            return
        
        # Skip if this is a migration or fixture load
        if kwargs.get('raw', False):
            return
        
        # Skip if middleware already logged this (for non-model API operations)
        # Model operations should ALWAYS be logged by signals for better change tracking
        # The middleware only logs non-model operations (custom endpoints, actions, etc.)
        try:
            from apps.monitoring.middleware import _thread_locals
            if hasattr(_thread_locals, 'audit_logged_by_middleware') and _thread_locals.audit_logged_by_middleware:
                # Middleware logged a non-model operation, skip signal logging
                # This flag is only set for non-model operations, so if it's set, skip
                return
        except Exception:
            pass
        
        # Determine action
        action = 'create' if created else 'update'
        
        # Get resource ID
        resource_id = str(instance.pk) if hasattr(instance, 'pk') else 'unknown'
        
        # Try to get user, IP, and user agent from thread local (set by middleware or mixin)
        user = None
        request_ip = None
        request_user_agent = None
        try:
            from apps.monitoring.middleware import _thread_locals
            if hasattr(_thread_locals, 'user'):
                user = getattr(_thread_locals, 'user', None)
                # Check if user is anonymous or not authenticated
                if user and (not hasattr(user, 'is_authenticated') or not user.is_authenticated):
                    user = None
            if hasattr(_thread_locals, 'request_ip'):
                request_ip = getattr(_thread_locals, 'request_ip', None)
            if hasattr(_thread_locals, 'request_user_agent'):
                request_user_agent = getattr(_thread_locals, 'request_user_agent', None)
            
            # Debug: Log if IP/user agent are missing
            if not request_ip or not request_user_agent:
                logger.debug(f"Missing IP/UA in signal - IP: {request_ip}, UA: {request_user_agent}, Has IP attr: {hasattr(_thread_locals, 'request_ip')}, Has UA attr: {hasattr(_thread_locals, 'request_user_agent')}")
        except Exception as e:
            logger.error(f"Error getting thread-local values: {e}", exc_info=True)
        
        # Build description
        description = f"{action.capitalize()} {model_name}"
        if hasattr(instance, '__str__'):
            try:
                description += f": {str(instance)}"
            except Exception:
                pass
        
        # Extract changes for updates
        changes = {}
        old_values_dict = {}
        new_values_dict = {}
        
        if not created:
            # Get old values that were captured in pre_save
            key = f"{model_name}_{instance.pk}"
            old_values = _model_old_values.get(key, {})
            
            if old_values:
                # Build old_values and new_values dicts
                old_values_dict = old_values.copy()
                
                # Compare old values with current values
                for field in instance._meta.fields:
                    if field.name not in ['id', 'pk']:
                        try:
                            current_value = getattr(instance, field.name)
                            
                            # Convert current value to serializable format
                            if hasattr(current_value, 'isoformat'):  # DateTime
                                current_value = current_value.isoformat()
                            elif hasattr(current_value, '__str__'):
                                current_value = str(current_value)
                            
                            # Add to new_values
                            new_values_dict[field.name] = current_value
                            
                            # Compare and record if changed
                            if field.name in old_values:
                                old_value = old_values[field.name]
                                if str(old_value) != str(current_value):
                                    changes[field.name] = {
                                        'before': old_value,
                                        'after': current_value
                                    }
                        except Exception as e:
                            logger.debug(f"Error processing field {field.name}: {e}")
                
                # Clean up old values
                if key in _model_old_values:
                    del _model_old_values[key]
        else:
            # For creates, capture all initial values as new_values
            for field in instance._meta.fields:
                if field.name not in ['id', 'pk']:
                    try:
                        value = getattr(instance, field.name)
                        if hasattr(value, 'isoformat'):  # DateTime
                            value = value.isoformat()
                        elif hasattr(value, '__str__'):
                            value = str(value)
                        new_values_dict[field.name] = value
                    except Exception:
                        pass
        
        # Prepare changes dict - separate field changes from full state
        clean_changes = {}
        for field_name, change_data in changes.items():
            if isinstance(change_data, dict) and 'before' in change_data and 'after' in change_data:
                clean_changes[field_name] = change_data
        
        # Log the action with old_values, new_values, and changes
        # Ensure IP and user agent are passed correctly
        audit_logger.log_action(
            action=action,
            resource_type=model_name,
            resource_id=resource_id,
            description=description,
            user=user,
            request=None,  # Signals don't have request context
            ip_address=request_ip if request_ip else None,
            user_agent=request_user_agent if request_user_agent else '',
            changes={
                **clean_changes,
                '_old_values': old_values_dict,
                '_new_values': new_values_dict,
            } if (clean_changes or old_values_dict or new_values_dict) else None,
        )
        
    except Exception as e:
        # Don't break the save operation if audit logging fails
        logger.error(f"Error in audit_model_save signal: {e}", exc_info=True)


@receiver(pre_delete)
def audit_model_delete(sender, instance, **kwargs):
    """
    Automatically log model delete operations.
    """
    try:
        # Skip excluded models
        model_name = get_model_name(instance)
        if model_name.lower() in [m.lower() for m in EXCLUDED_MODELS]:
            return
        
        # Skip if this is a migration or fixture load
        if kwargs.get('raw', False):
            return
        
        # Get resource ID
        resource_id = str(instance.pk) if hasattr(instance, 'pk') else 'unknown'
        
        # Try to get user, IP, and user agent from thread local (set by middleware or mixin)
        user = None
        request_ip = None
        request_user_agent = None
        try:
            from apps.monitoring.middleware import _thread_locals
            if hasattr(_thread_locals, 'user'):
                user = getattr(_thread_locals, 'user', None)
                # Check if user is anonymous or not authenticated
                if user and (not hasattr(user, 'is_authenticated') or not user.is_authenticated):
                    user = None
            if hasattr(_thread_locals, 'request_ip'):
                request_ip = getattr(_thread_locals, 'request_ip', None)
            if hasattr(_thread_locals, 'request_user_agent'):
                request_user_agent = getattr(_thread_locals, 'request_user_agent', None)
        except Exception as e:
            logger.error(f"Error getting thread-local values in delete signal: {e}", exc_info=True)
        
        # Build description
        description = f"Delete {model_name}"
        if hasattr(instance, '__str__'):
            try:
                description += f": {str(instance)}"
            except Exception:
                pass
        
        # Get instance data before deletion (for old_values)
        old_values_dict = {}
        if hasattr(instance, '_meta'):
            for field in instance._meta.fields:
                if field.name not in ['id', 'pk']:
                    try:
                        value = getattr(instance, field.name)
                        # Convert to serializable format
                        if hasattr(value, 'isoformat'):  # DateTime
                            value = value.isoformat()
                        elif hasattr(value, '__str__'):
                            value = str(value)
                        
                        # Store all values in old_values (complete state before deletion)
                        old_values_dict[field.name] = value
                    except Exception:
                        pass
        
        # For delete operations, changes should show what was deleted (non-sensitive fields only)
        # Store the complete state as old_values (new_values will be empty)
        changes = {}
        for field_name, value in old_values_dict.items():
            # Filter out sensitive fields from changes display
            if field_name not in ['password', 'secret', 'token', 'key', 'api_key', 'two_factor_secret']:
                changes[field_name] = value
        
        # Log the action with old_values (complete state before deletion)
        audit_logger.log_action(
            action='delete',
            resource_type=model_name,
            resource_id=resource_id,
            description=description,
            user=user,
            request=None,
            ip_address=request_ip if request_ip else None,
            user_agent=request_user_agent if request_user_agent else '',
            changes={
                '_old_values': old_values_dict,
                '_new_values': {},  # Empty for delete operations
            } if old_values_dict else None,
        )
        
    except Exception as e:
        # Don't break the delete operation if audit logging fails
        logger.error(f"Error in audit_model_delete signal: {e}", exc_info=True)

