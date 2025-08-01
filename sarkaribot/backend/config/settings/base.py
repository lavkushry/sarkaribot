"""
Django settings for SarkariBot project.

Base settings shared across all environments.
Environment-specific settings should inherit from this file.
"""

import os
from pathlib import Path
from decouple import config, Csv
from typing import List, Dict, Any
import logging.config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    'SECRET_KEY', 
    default='django-insecure-dev-key-change-in-production-environments'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Allowed hosts configuration
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', 
    default='localhost,127.0.0.1', 
    cast=Csv()
)

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.core',
    'apps.sources',
    'apps.jobs',
    'apps.scraping',
    'apps.seo',
    # Stage 4 Advanced Features (enable when ready)
    # 'apps.analytics',
    # 'apps.ai_search', 
    # 'apps.monitoring',
    # 'apps.alerts',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# Database configuration (environment-specific)
# Default to SQLite for development, override in production
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DB_NAME', default=BASE_DIR / 'db.sqlite3'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
        'OPTIONS': config(
            'DB_OPTIONS', 
            default={}, 
            cast=lambda v: eval(v) if v else {}
        ),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')
TIME_ZONE = config('TIME_ZONE', default='Asia/Kolkata')
USE_I18N = True
USE_TZ = True

# Site framework
SITE_ID = 1

# Static files (CSS, JavaScript, Images)
STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = config('STATIC_ROOT', default=BASE_DIR / 'staticfiles', cast=Path)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = config('MEDIA_ROOT', default=BASE_DIR / 'media', cast=Path)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': config('DRF_PAGE_SIZE', default=20, cast=int),
    'MAX_PAGE_SIZE': config('DRF_MAX_PAGE_SIZE', default=100, cast=int),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': config('DRF_ANON_RATE', default='100/hour'),
        'user': config('DRF_USER_RATE', default='1000/hour')
    },
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}

# API Documentation settings
SPECTACULAR_SETTINGS = {
    'TITLE': config('API_TITLE', default='SarkariBot API'),
    'DESCRIPTION': config('API_DESCRIPTION', default='Government Job Portal API'),
    'VERSION': config('API_VERSION', default='1.0.0'),
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
}

# CORS Settings
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)
CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', default=True, cast=bool)
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'scrape-all-sources': {
        'task': 'apps.scraping.tasks.scrape_all_sources',
        'schedule': config('SCRAPE_INTERVAL', default=3600.0, cast=float),  # Every hour
    },
    'update-job-statuses': {
        'task': 'apps.jobs.tasks.update_job_statuses',
        'schedule': config('STATUS_UPDATE_INTERVAL', default=21600.0, cast=float),  # Every 6 hours
    },
    'generate-seo-metadata': {
        'task': 'apps.seo.tasks.generate_seo_metadata_batch',
        'schedule': config('SEO_GENERATION_INTERVAL', default=7200.0, cast=float),  # Every 2 hours
    },
    'cleanup-old-jobs': {
        'task': 'apps.jobs.tasks.cleanup_old_jobs',
        'schedule': config('CLEANUP_INTERVAL', default=86400.0, cast=float),  # Daily
    },
}

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': config(
            'CACHE_BACKEND', 
            default='django.core.cache.backends.dummy.DummyCache'
        ),
        'LOCATION': config('CACHE_LOCATION', default=''),
        'TIMEOUT': config('CACHE_TIMEOUT', default=300, cast=int),
        'OPTIONS': {
            'CLIENT_CLASS': config('CACHE_CLIENT_CLASS', default=''),
        },
        'KEY_PREFIX': 'sarkaribot',
        'VERSION': 1,
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=1209600, cast=int)  # 2 weeks

# Email configuration
EMAIL_BACKEND = config(
    'EMAIL_BACKEND', 
    default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@sarkaribot.com')

# Logging Configuration
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

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
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.scraping': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'apps.seo': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Custom SarkariBot Settings
SARKARIBOT_SETTINGS = {
    'MAX_JOBS_PER_SOURCE': config('MAX_JOBS_PER_SOURCE', default=1000, cast=int),
    'SCRAPING_DELAY': config('SCRAPING_DELAY', default=2, cast=int),
    'MAX_RETRY_ATTEMPTS': config('MAX_RETRY_ATTEMPTS', default=3, cast=int),
    'ENABLE_SEO_AUTOMATION': config('ENABLE_SEO_AUTOMATION', default=True, cast=bool),
    'GENERATE_SITEMAP': config('GENERATE_SITEMAP', default=True, cast=bool),
    'CLEANUP_AFTER_DAYS': config('CLEANUP_AFTER_DAYS', default=365, cast=int),
    'ENABLE_JOB_ALERTS': config('ENABLE_JOB_ALERTS', default=True, cast=bool),
    'MAX_SEARCH_RESULTS': config('MAX_SEARCH_RESULTS', default=500, cast=int),
}

# Web Scraping Configuration
SCRAPING_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
]

SCRAPING_DEFAULT_DELAY = config('SCRAPING_DEFAULT_DELAY', default=2, cast=int)
SCRAPING_MAX_RETRIES = config('SCRAPING_MAX_RETRIES', default=3, cast=int)
SCRAPING_TIMEOUT = config('SCRAPING_TIMEOUT', default=30, cast=int)

# SEO Settings
SEO_TITLE_MAX_LENGTH = config('SEO_TITLE_MAX_LENGTH', default=60, cast=int)
SEO_DESCRIPTION_MAX_LENGTH = config('SEO_DESCRIPTION_MAX_LENGTH', default=160, cast=int)
SEO_KEYWORDS_MAX_COUNT = config('SEO_KEYWORDS_MAX_COUNT', default=7, cast=int)

# NLP Model Configuration
SPACY_MODEL = config('SPACY_MODEL', default='en_core_web_sm')

# Government Sources Configuration
GOVERNMENT_SOURCES_CONFIG_PATH = BASE_DIR / 'config' / 'government_sources.json'
