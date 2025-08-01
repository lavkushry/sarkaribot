"""
Quick local development settings for SarkariBot.

This file provides a minimal configuration for running SarkariBot locally
without requiring environment setup. Use this for:
- Quick testing and development
- Running migrations
- Initial project setup

For production or advanced development, use the proper settings structure:
- config.settings.development (with .env file)
- config.settings.production (for deployment)
"""

from .settings.base import *
import os

# Override settings for simple local development
DEBUG = True
ALLOWED_HOSTS = ['*']

# Simple SQLite database - no setup required
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_local.sqlite3',
    }
}

# Use dummy cache - no Redis required
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Console email backend - emails printed to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS - Allow all origins for local development
CORS_ALLOW_ALL_ORIGINS = True

# Celery - Run synchronously for simple setup
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Simple logging to console
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Create necessary directories
for directory in [BASE_DIR / 'media', BASE_DIR / 'static', BASE_DIR / 'logs']:
    directory.mkdir(exist_ok=True)

print("🏠 Local development settings loaded")
print("📊 Database: SQLite (no setup required)")
print("💾 Cache: Dummy cache (no Redis required)")
print("📧 Email: Console backend")
print("🔧 Celery: Synchronous execution")
print("✨ Ready for local development!")
