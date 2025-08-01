"""
Development settings for SarkariBot project.
"""

from .base import *

DEBUG = True

# Database
DATABASES['default']['NAME'] = 'sarkaribot_dev'

# Development-specific apps
INSTALLED_APPS += [
    # 'django_extensions',  # Temporarily commented until installed
]

if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',  # Django debug toolbar for development
    ]
    
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE
    
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]

# Disable caching in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging - more verbose in development
LOGGING['loggers']['apps']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Celery - run tasks synchronously in development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# CORS - allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Scraping settings for development
SCRAPING_DEFAULT_DELAY = 1  # Faster scraping in development
SCRAPING_MAX_RETRIES = 1
