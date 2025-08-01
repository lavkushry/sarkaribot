"""
Production settings for SarkariBot project.

These settings are optimized for production deployment with:
- Enhanced security settings
- PostgreSQL database
- Redis cache and message broker
- Proper logging to files
- Error tracking with Sentry
- Performance optimizations
"""

from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

# Security - Force secure settings in production
DEBUG = False

# Security headers and settings
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

# Additional security middleware for production
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static file serving
] + MIDDLEWARE

# Database - Override for PostgreSQL in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=600, cast=int),
        'OPTIONS': {
            'sslmode': config('DB_SSL_MODE', default='require'),
        },
    }
}

# Cache - Use Redis in production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('CACHE_URL'),
        'TIMEOUT': config('CACHE_TIMEOUT', default=3600, cast=int),  # 1 hour
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': config('CACHE_MAX_CONNECTIONS', default=20, cast=int),
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'sarkaribot-prod',
        'VERSION': 1,
    }
}

# Session configuration for production
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=1209600, cast=int)  # 2 weeks
SESSION_COOKIE_HTTPONLY = True

# Static files configuration for production
STATIC_ROOT = config('STATIC_ROOT', default='/var/www/sarkaribot/static', cast=Path)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False

# Media files configuration for production
MEDIA_ROOT = config('MEDIA_ROOT', default='/var/www/sarkaribot/media', cast=Path)

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

# Logging configuration for production
LOGS_DIR = Path(config('LOGS_DIR', default='/var/log/sarkaribot'))
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOGGING.update({
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 1024*1024*50,  # 50 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django_errors.log',
            'maxBytes': 1024*1024*50,  # 50 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'scraping_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'scraping.log',
            'maxBytes': 1024*1024*100,  # 100 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',  # Only log errors to console in production
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.scraping': {
            'handlers': ['scraping_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.seo': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
})

# Sentry error tracking
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=False,
            ),
            CeleryIntegration(monitor_beat_tasks=True),
        ],
        traces_sample_rate=config('SENTRY_TRACES_SAMPLE_RATE', default=0.1, cast=float),
        send_default_pii=False,  # Don't send PII for privacy
        environment=config('SENTRY_ENVIRONMENT', default='production'),
        release=config('APP_VERSION', default='1.0.0'),
    )

# Celery configuration for production
CELERY_TASK_ALWAYS_EAGER = False
CELERY_WORKER_PREFETCH_MULTIPLIER = config('CELERY_PREFETCH_MULTIPLIER', default=1, cast=int)
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = config('CELERY_MAX_TASKS_PER_CHILD', default=1000, cast=int)

# Production-specific DRF settings
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        # Remove browsable API in production for security
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': config('DRF_ANON_RATE', default='100/hour'),
        'user': config('DRF_USER_RATE', default='1000/hour'),
    }
})

# CORS - Strict configuration for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    cast=Csv()
)

# Production performance settings
CONN_MAX_AGE = 600  # Database connection pooling

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = config('FILE_UPLOAD_MAX_MEMORY_SIZE', default=2621440, cast=int)  # 2.5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = config('DATA_UPLOAD_MAX_MEMORY_SIZE', default=2621440, cast=int)  # 2.5 MB

# Production-specific SarkariBot settings
SARKARIBOT_SETTINGS.update({
    'MAX_JOBS_PER_SOURCE': config('MAX_JOBS_PER_SOURCE', default=5000, cast=int),
    'SCRAPING_DELAY': config('SCRAPING_DELAY', default=3, cast=int),  # Slower in production
    'MAX_RETRY_ATTEMPTS': config('MAX_RETRY_ATTEMPTS', default=5, cast=int),
    'ENABLE_SEO_AUTOMATION': config('ENABLE_SEO_AUTOMATION', default=True, cast=bool),
    'GENERATE_SITEMAP': config('GENERATE_SITEMAP', default=True, cast=bool),
    'CLEANUP_AFTER_DAYS': config('CLEANUP_AFTER_DAYS', default=730, cast=int),  # 2 years
})

print("🚀 Production settings loaded")
print(f"🔒 Debug mode: {DEBUG}")
print(f"📊 Database: PostgreSQL")
print(f"💾 Cache: Redis")
print(f"📧 Email: SMTP")
print(f"📝 Logs: {LOGS_DIR}")
if SENTRY_DSN:
    print("🔍 Error tracking: Sentry enabled")

# Validate required production settings
required_settings = [
    'SECRET_KEY',
    'DB_NAME',
    'DB_USER', 
    'DB_PASSWORD',
    'EMAIL_HOST',
    'EMAIL_HOST_USER',
    'EMAIL_HOST_PASSWORD',
]

missing_settings = []
for setting in required_settings:
    try:
        config(setting)
    except Exception:
        missing_settings.append(setting)

if missing_settings:
    raise Exception(f"Missing required production settings: {', '.join(missing_settings)}")

print("✅ All required production settings validated")
