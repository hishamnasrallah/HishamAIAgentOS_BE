"""
Base settings for HishamOS project.
This file contains settings common to all environments.
"""

import os
from pathlib import Path
from datetime import timedelta
import environ

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment variables
env = environ.Env(
    DJANGO_DEBUG=(bool, False)
)

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR.parent, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-dev-key-CHANGE-IN-PRODUCTION')

# Application definition
INSTALLED_APPS = [
    'daphne',  # ASGI server - must be first
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'channels',
    'django_celery_beat',
    'drf_spectacular',
    
    # Local apps
    'apps.authentication',
    'apps.organizations',  # Organizations (SaaS multi-tenancy)
    'apps.agents',
    'apps.commands',
    'apps.workflows',
    'apps.projects',
    'apps.integrations',
    'apps.integrations_external',  # Phase 21: External integrations (GitHub, Slack, Email, Webhooks)
    'apps.results',
    'apps.monitoring',
    'apps.chat',  # Phase 13-14: Chat interface
    'apps.core',  # Core system settings and feature flags
    'apps.docs',  # Documentation viewer
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'core.security_middleware.RequestThrottlingMiddleware',  # Request throttling
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'core.csrf_middleware.DisableCSRFForAPI',  # Disable CSRF for API endpoints
    'django.middleware.csrf.CsrfViewMiddleware',  # Still enabled for admin/forms
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.authentication.middleware.AuthenticationLoggingMiddleware',
    'apps.monitoring.middleware.AuditLoggingMiddleware',  # Automatic audit logging for all API requests
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.security_middleware.SecurityHeadersMiddleware',  # Security headers
]

# CORS settings - Allow all origins by default for flexibility
# Can be restricted via environment variable CORS_ALLOWED_ORIGINS
CORS_ALLOW_ALL_ORIGINS = env.bool('CORS_ALLOW_ALL_ORIGINS', default=True)
CORS_ALLOW_CREDENTIALS = True

# Specific origins (used when CORS_ALLOW_ALL_ORIGINS is False)
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
)

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# Database
# Using SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR.parent / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom user model
AUTH_USER_MODEL = 'authentication.User'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'apps.authentication.middleware.APIKeyAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # For browseable API
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',  # Allow read access to docs
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
    # Rate limiting/throttling
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'apps.authentication.throttling.APIKeyRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Anonymous users: 100 requests per hour
        'user': '1000/hour',  # Authenticated users: 1000 requests per hour
        'api_key': '60/minute',  # Default API key rate: 60 requests per minute
    },
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', default=30)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('JWT_REFRESH_TOKEN_EXPIRE_DAYS', default=30)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': env('JWT_ALGORITHM', default='HS256'),
    'SIGNING_KEY': env('JWT_SECRET_KEY', default=SECRET_KEY),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Celery Configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# Redis Configuration
REDIS_HOST = env('REDIS_HOST', default='localhost')
REDIS_PORT = env.int('REDIS_PORT', default=6379)
REDIS_DB = env.int('REDIS_DB', default=0)
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

# Cache Configuration
# Use Redis if available, fallback to local memory for development
try:
    import django_redis
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'IGNORE_EXCEPTIONS': True,  # Fallback gracefully if Redis is unavailable
            },
            'KEY_PREFIX': 'hishamos',
            'TIMEOUT': 300,  # Default 5 minutes
        }
    }
except ImportError:
    # Fallback to local memory cache if django-redis is not installed
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'hishamos-cache',
            'TIMEOUT': 300,
        }
    }

# Cache timeout settings (in seconds)
CACHE_TIMEOUT_SHORT = 60  # 1 minute
CACHE_TIMEOUT_MEDIUM = 300  # 5 minutes
CACHE_TIMEOUT_LONG = 600  # 10 minutes

# Channels - Using InMemory for development (no Redis required)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    },
}

# AI Platform Configuration
OPENAI_API_KEY = env('OPENAI_API_KEY', default='')
OPENAI_ORG_ID = env('OPENAI_ORG_ID', default='')
ANTHROPIC_API_KEY = env('ANTHROPIC_API_KEY', default='')
GOOGLE_GEMINI_API_KEY = env('GOOGLE_GEMINI_API_KEY', default='')

# Email Configuration
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@hishamos.com')

# Generated Projects Configuration
GENERATED_PROJECTS_DIR = env('GENERATED_PROJECTS_DIR', default=str(BASE_DIR / 'generated-projects'))
GENERATED_PROJECTS_RETENTION_DAYS = env.int('GENERATED_PROJECTS_RETENTION_DAYS', default=30)
MAX_FILE_SIZE = env.int('MAX_FILE_SIZE', default=10 * 1024 * 1024)  # 10MB default
MAX_PROJECT_SIZE = env.int('MAX_PROJECT_SIZE', default=100 * 1024 * 1024)  # 100MB default

# Backend URL for internal API calls
BACKEND_URL = env('BACKEND_URL', default='http://localhost:8000')

# Logging
# Enable structured JSON logging in production, verbose in development
USE_JSON_LOGGING = env.bool('USE_JSON_LOGGING', default=False)

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
        'json': {
            '()': 'core.logging_formatters.JSONFormatter',
        },
        'json_contextual': {
            '()': 'core.logging_formatters.ContextualJSONFormatter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json' if USE_JSON_LOGGING else 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'json' if USE_JSON_LOGGING else 'verbose',
        },
        'json_file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.json.log',
            'formatter': 'json_contextual',
        },
    },
    'root': {
        'handlers': ['console', 'file'] + (['json_file'] if USE_JSON_LOGGING else []),
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'] + (['json_file'] if USE_JSON_LOGGING else []),
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'] + (['json_file'] if USE_JSON_LOGGING else []),
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# DRF Spectacular Settings (API Documentation)
# Windows-compatible settings to prevent OSError [Errno 22] Invalid argument
import sys
import tempfile

SPECTACULAR_SETTINGS = {
    'TITLE': 'HishamOS API',
    'DESCRIPTION': 'AI Agent Operating System - Complete API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    # Windows-specific fixes
    'SCHEMA_PATH_PREFIX': '/api/v1',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SERVE_AUTHENTICATION': None,
    # Disable problematic features on Windows
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
    # Use a safe temp directory for Windows
    'TEMP_DIR': tempfile.gettempdir() if sys.platform == 'win32' else None,
    # Disable caching that can cause issues on Windows
    'DISABLE_ERRORS_AND_WARNINGS': False,
    'PREPROCESSING_HOOKS': [],
    'POSTPROCESSING_HOOKS': [],
    # Ensure proper encoding
    'ENUM_NAME_OVERRIDES': {},
    'CONTACT': {
        'name': 'HishamOS Support',
        'email': 'support@hishamos.com',
    },
    'LICENSE': {
        'name': 'Proprietary',
    },
    'TAGS': [
        {'name': 'Authentication', 'description': 'User authentication and authorization'},
        {'name': 'Agents', 'description': 'AI agent management'},
        {'name': 'Commands', 'description': 'Command library'},
        {'name': 'Workflows', 'description': 'Workflow orchestration'},
        {'name': 'Projects', 'description': 'Project management'},
        {'name': 'Integrations', 'description': 'AI platform integrations'},
        {'name': 'Results', 'description': 'Execution results'},
        {'name': 'Monitoring', 'description': 'System monitoring'},
        {'name': 'Chat', 'description': 'Chat interface'},
    ],
}

# Rate Limiting
RATE_LIMIT_PER_MINUTE = env.int('RATE_LIMIT_PER_MINUTE', default=60)
RATE_LIMIT_PER_HOUR = env.int('RATE_LIMIT_PER_HOUR', default=1000)

# Secrets Management (HashiCorp Vault)
VAULT_ENABLED = env.bool('VAULT_ENABLED', default=False)
VAULT_ADDR = env('VAULT_ADDR', default='')
VAULT_TOKEN = env('VAULT_TOKEN', default='')
VAULT_MOUNT_POINT = env('VAULT_MOUNT_POINT', default='secret')
USE_LOCAL_ENCRYPTION = env.bool('USE_LOCAL_ENCRYPTION', default=True)
SECRETS_ENCRYPTION_KEY = env('SECRETS_ENCRYPTION_KEY', default=None)

# Alerting Configuration
ALERT_EMAIL_RECIPIENTS = env.list('ALERT_EMAIL_RECIPIENTS', default=[])
SLACK_ALERT_WEBHOOK = env('SLACK_ALERT_WEBHOOK', default='')
ALERT_WEBHOOK_URL = env('ALERT_WEBHOOK_URL', default='')

# Enhanced Caching Configuration
MEMORY_CACHE_TTL = env.int('MEMORY_CACHE_TTL', default=60)  # 1 minute
REDIS_CACHE_TTL = env.int('REDIS_CACHE_TTL', default=300)  # 5 minutes
DB_CACHE_TTL = env.int('DB_CACHE_TTL', default=3600)  # 1 hour

# Security Settings (Override in production)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CSRF Trusted Origins - Flexible configuration
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