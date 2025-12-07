"""
Development settings for HishamOS project.
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Override database for development - use SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS Settings for development
# In development, allow all origins for easier debugging
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Also set specific origins as fallback
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=[
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:5174',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:5174',
    ]
)

# Add development apps
# INSTALLED_APPS += [
#     'django_extensions',
#     'debug_toolbar',
# ]

# Add debug toolbar middleware
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Additional logging for development
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# Disable caching in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# CSRF Trusted Origins for development - Allow all origins
# Allows requests from any origin for maximum flexibility during development
_csrf_origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS')
if _csrf_origins_env:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _csrf_origins_env.split(',')]
else:
    # Default: Comprehensive list of common origins for development
    # Note: API endpoints have CSRF disabled via middleware, so this mainly affects admin/session auth
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
    ]