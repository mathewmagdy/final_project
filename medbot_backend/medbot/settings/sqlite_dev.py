"""
SQLite development settings for MedBot project.
Use this temporarily if PostgreSQL setup is challenging.
"""

from .base import *

# Debug settings
DEBUG = True

# Use SQLite for quick development setup
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Additional development apps
# django_extensions already in base.py

# Development middleware
MIDDLEWARE += [
    # Add any development-specific middleware here
]

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Security settings for development
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Cache configuration for development (use dummy cache if Redis not available)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Development logging
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['root']['level'] = 'DEBUG'

# n8n settings for development
N8N_BASE_URL = config('N8N_BASE_URL', default='http://localhost:5678')
N8N_API_KEY = config('N8N_API_KEY', default='development-key')

# Create logs directory if it doesn't exist
import os
logs_dir = BASE_DIR / 'logs'
if not logs_dir.exists():
    logs_dir.mkdir(parents=True, exist_ok=True)
