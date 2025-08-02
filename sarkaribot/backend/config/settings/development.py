"""
Development settings for SarkariBot project.

These settings are optimized for local development with:
- Debug mode enabled
- SQLite database for simplicity
- Console email backend
- Dummy cache for faster development
- Reduced security for ease of development
"""

from .base import *
import os

# Override base settings for development
DEBUG = True

# Allow all hosts in development for convenience
ALLOWED_HOSTS = ['*']

# Development-specific apps
DEV_APPS = []

# Add Django Debug Toolbar if available
try:
    import debug_toolbar
    DEV_APPS.append('debug_toolbar')
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
    }
except ImportError:
    pass

# Add Django Extensions if available
try:
    import django_extensions
    DEV_APPS.append('django_extensions')
except ImportError:
    pass

INSTALLED_APPS += DEV_APPS

# Database - Override to ensure SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_dev.sqlite3',
    }
}

# Cache - Use dummy cache for development (no Redis required)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email backend for development - print emails to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging - More verbose in development
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# Add file logging for development
DEV_LOG_FILE = BASE_DIR / 'logs' / 'development.log'
LOGGING['handlers']['dev_file'] = {
    'level': 'DEBUG',
    'class': 'logging.FileHandler',
    'filename': DEV_LOG_FILE,
    'formatter': 'verbose',
}
LOGGING['loggers']['apps']['handlers'].append('dev_file')

# Celery - Run tasks synchronously in development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Security - Relax security settings for development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Static files - Enable serving during development
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Development-specific DRF settings
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Enable browsable API
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/hour',   # More lenient rates for development
        'user': '5000/hour',
    }
})

# Development-specific scraping settings
SCRAPING_DEFAULT_DELAY = 1  # Faster scraping in development
SCRAPING_MAX_RETRIES = 1    # Fail fast in development
SCRAPING_TIMEOUT = 10       # Shorter timeout for development

# Celery beat schedule - More frequent for development testing
CELERY_BEAT_SCHEDULE.update({
    'scrape-all-sources': {
        'task': 'apps.scraping.tasks.scrape_all_sources',
        'schedule': 600.0,  # Every 10 minutes for testing
    },
    'update-job-statuses': {
        'task': 'apps.jobs.tasks.update_job_statuses', 
        'schedule': 1800.0,  # Every 30 minutes for testing
    },
})

# Custom development settings
SARKARIBOT_SETTINGS.update({
    'MAX_JOBS_PER_SOURCE': 100,  # Smaller limit for development
    'ENABLE_SEO_AUTOMATION': False,  # Disable for faster development
    'GENERATE_SITEMAP': False,  # Disable for development
})

print("🔧 Development settings loaded")
print(f"📊 Database: SQLite ({DATABASES['default']['NAME']})")
print(f"📧 Email: Console backend")
print(f"💾 Cache: Dummy cache")
print(f"🔍 Debug mode: {DEBUG}")
print(f"🌐 Allowed hosts: {ALLOWED_HOSTS}")

# Environment validation
required_dirs = [BASE_DIR / 'logs', BASE_DIR / 'media', BASE_DIR / 'static']
for directory in required_dirs:
    directory.mkdir(exist_ok=True)
    
# Check for .env file
env_file = BASE_DIR / '.env'
if not env_file.exists():
    print("⚠️  No .env file found. Using default development settings.")
    print(f"📄 Copy .env.example to .env for custom configuration")
else:
    print("✅ Using .env file for configuration")
