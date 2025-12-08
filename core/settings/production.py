"""
Production settings for HishamOS project.
"""

from .base import *

DEBUG = False

# Enable JSON logging in production
USE_JSON_LOGGING = True

# ALLOWED_HOSTS - Accept all hosts by default for flexibility
# Can be restricted via DJANGO_ALLOWED_HOSTS environment variable
_allowed_hosts_env = os.environ.get('DJANGO_ALLOWED_HOSTS')
if _allowed_hosts_env:
    ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')
else:
    # Default: Allow all hosts (most flexible)
    # This allows the backend to accept requests from any domain/IP
    ALLOWED_HOSTS = ['*']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS Settings for production - Allow all origins by default
# Can be restricted via CORS_ALLOWED_ORIGINS environment variable
_cors_all_origins_env = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'true').lower()
CORS_ALLOW_ALL_ORIGINS = _cors_all_origins_env in ('true', '1', 'yes', 'on')
CORS_ALLOW_CREDENTIALS = True

# Specific origins (used when CORS_ALLOW_ALL_ORIGINS is False)
_cors_origins_env = os.environ.get('CORS_ALLOWED_ORIGINS')
if _cors_origins_env:
    CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')
else:
    CORS_ALLOWED_ORIGINS = []

# CSRF Trusted Origins - Flexible configuration for production
# Allows requests from any origin by default (can be restricted via environment variable)
# Note: Wildcards (*) are supported by Django for CSRF_TRUSTED_ORIGINS
_csrf_origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS')
if _csrf_origins_env:
    # Use environment variable if provided
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _csrf_origins_env.split(',')]
else:
    # Default: Comprehensive list of common origins
    # Note: Django doesn't support full wildcards like http://*
    # API endpoints have CSRF disabled via middleware, so this mainly affects admin/session auth
    CSRF_TRUSTED_ORIGINS = [
        # Localhost variants (common ports)
        'http://localhost',
        'http://127.0.0.1',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:5174',
        'http://127.0.0.1:5174',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        # Cloud platforms (wildcard patterns supported)
        'https://*.replit.dev',
        'https://*.repl.co',
        'https://*.render.com',
        'https://*.railway.app',
        'https://*.fly.dev',
        'https://*.vercel.app',
        'https://*.netlify.app',
        'https://*.herokuapp.com',
        'https://*.pythonanywhere.com',
    ]

# Production caching with Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50}
        },
        'KEY_PREFIX': 'hishamos',
        'TIMEOUT': 300,
    }
}

# Sentry error tracking
SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

# Production logging - Use console only for cloud platforms (Render, Railway, etc.)
# Override base logging to use console handler only
import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# If running on a server with /var/log access, add file handler
if os.path.exists('/var/log') and os.access('/var/log', os.W_OK):
    try:
        os.makedirs('/var/log/hishamos', exist_ok=True)
        LOGGING['handlers']['file'] = {
            'class': 'logging.FileHandler',
            'filename': '/var/log/hishamos/django.log',
            'formatter': 'verbose',
        }
        LOGGING['root']['handlers'].append('file')
        LOGGING['loggers']['django']['handlers'].append('file')
        LOGGING['loggers']['apps']['handlers'].append('file')
    except (OSError, PermissionError):
        # If we can't create log directory, continue with console only
        pass
