"""
Structured JSON logging formatters for HishamOS.

Provides JSON formatters for structured logging that can be easily parsed
by log aggregation systems like Loki, ELK, or CloudWatch.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict
import traceback


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    
    Formats log records as JSON with consistent structure including:
    - Timestamp (ISO 8601)
    - Log level
    - Logger name
    - Message
    - Module, function, line number
    - Process/thread IDs
    - Exception information (if present)
    - Extra context (if provided)
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON string representation of the log record
        """
        # Base log data
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': record.process,
            'thread_id': record.thread,
            'thread_name': record.threadName,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': self.formatException(record.exc_info) if record.exc_info else None,
            }
        
        # Add extra context from record
        # Exclude standard LogRecord attributes
        standard_attrs = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName',
            'levelname', 'levelno', 'lineno', 'module', 'msecs', 'message',
            'pathname', 'process', 'processName', 'relativeCreated', 'thread',
            'threadName', 'exc_info', 'exc_text', 'stack_info', 'getMessage'
        }
        
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith('_'):
                # Serialize value if it's not JSON-serializable
                try:
                    json.dumps(value)
                    log_data[key] = value
                except (TypeError, ValueError):
                    log_data[key] = str(value)
        
        # Add request context if available (from middleware)
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'ip_address'):
            log_data['ip_address'] = record.ip_address
        if hasattr(record, 'path'):
            log_data['path'] = record.path
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


class ContextualJSONFormatter(JSONFormatter):
    """
    Enhanced JSON formatter with automatic context enrichment.
    
    Automatically adds context from Django request, user, and other sources.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with automatic context enrichment.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON string representation with enriched context
        """
        # Get base JSON format
        log_data = json.loads(super().format(record))
        
        # Try to enrich with Django request context
        try:
            from django.conf import settings
            if hasattr(settings, 'MIDDLEWARE'):
                # Check if we have request in context
                import threading
                request = getattr(threading.current_thread(), 'request', None)
                if request:
                    log_data['request'] = {
                        'method': request.method,
                        'path': request.path,
                        'query_string': request.GET.urlencode(),
                        'remote_addr': request.META.get('REMOTE_ADDR'),
                        'user_agent': request.META.get('HTTP_USER_AGENT'),
                    }
                    if hasattr(request, 'user') and request.user.is_authenticated:
                        log_data['request']['user_id'] = str(request.user.id)
                        log_data['request']['user_email'] = request.user.email
        except Exception:
            # Silently fail if Django context is not available
            pass
        
        return json.dumps(log_data, ensure_ascii=False, default=str)

