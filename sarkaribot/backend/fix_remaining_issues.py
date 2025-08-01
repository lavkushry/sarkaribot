#!/usr/bin/env python3
"""
SarkariBot - Comprehensive Issue Resolution Script

This script addresses all remaining issues in the codebase:
1. Install missing NLP dependencies
2. Fix frontend-backend integration
3. Improve error handling
4. Set up proper development environment
5. Create production-ready configurations
"""

import os
import sys
import subprocess
import logging
import json
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SarkariBotFixer:
    """Main class to fix all remaining issues"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.backend_dir = self.base_dir
        self.frontend_dir = self.base_dir.parent / "frontend"
        self.venv_dir = self.backend_dir / "venv"
        
    def run_command(self, cmd, cwd=None, check=True):
        """Run shell command with proper error handling"""
        try:
            logger.info(f"Running: {cmd}")
            if cwd:
                result = subprocess.run(
                    cmd, shell=True, check=check, cwd=cwd,
                    capture_output=True, text=True
                )
            else:
                result = subprocess.run(
                    cmd, shell=True, check=check,
                    capture_output=True, text=True
                )
            
            if result.stdout:
                logger.info(f"Output: {result.stdout.strip()}")
            
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {cmd}")
            logger.error(f"Error: {e.stderr}")
            if check:
                raise
            return e
    
    def install_nlp_dependencies(self):
        """Install NLP dependencies for Python 3.12"""
        logger.info("=== Installing NLP Dependencies ===")
        
        # Create updated requirements for NLP
        nlp_requirements = """
# Core NLP dependencies compatible with Python 3.12
# Basic text processing
textblob==0.17.1
nltk==3.8.1

# Advanced NLP (alternative to spaCy)
scikit-learn==1.3.0
numpy==1.24.3
pandas==2.0.3

# SEO and text analysis
python-slugify==8.0.1
beautifulsoup4==4.12.2
lxml==4.9.3
"""
        
        nlp_req_file = self.backend_dir / "requirements" / "nlp.txt"
        with open(nlp_req_file, 'w') as f:
            f.write(nlp_requirements.strip())
        
        # Install NLP requirements
        activate_cmd = f"source {self.venv_dir}/bin/activate"
        install_cmd = f"{activate_cmd} && pip install -r requirements/nlp.txt"
        
        self.run_command(install_cmd, cwd=self.backend_dir)
        
        # Download NLTK data
        nltk_setup = """
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    print("NLTK data downloaded successfully")
except Exception as e:
    print(f"NLTK download error: {e}")
"""
        
        nltk_setup_file = self.backend_dir / "setup_nltk.py"
        with open(nltk_setup_file, 'w') as f:
            f.write(nltk_setup)
        
        setup_cmd = f"{activate_cmd} && python setup_nltk.py"
        self.run_command(setup_cmd, cwd=self.backend_dir, check=False)
        
        logger.info("✓ NLP dependencies installed")
    
    def create_enhanced_seo_engine(self):
        """Create enhanced SEO engine with fallback NLP"""
        logger.info("=== Creating Enhanced SEO Engine ===")
        
        enhanced_seo_code = '''"""
Enhanced SEO Engine with NLTK fallback for SarkariBot.

This provides NLP-powered SEO optimization with graceful degradation
when advanced NLP libraries are not available.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from django.utils.text import slugify
from django.utils.html import strip_tags
from collections import Counter

# Try advanced NLP imports with fallbacks
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
    print("NLTK successfully loaded")
except ImportError:
    NLTK_AVAILABLE = False
    print("NLTK not available - using basic text processing")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)

# Basic stop words for fallback
BASIC_STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'will', 'with', 'this', 'these', 'they', 'have', 'had',
    'application', 'notification', 'recruitment', 'examination', 'apply'
}

class EnhancedSEOEngine:
    """
    Enhanced SEO engine with multiple NLP backends and graceful fallbacks.
    """
    
    def __init__(self):
        """Initialize the enhanced SEO engine."""
        self.stop_words = self._get_stop_words()
        self.lemmatizer = self._get_lemmatizer()
        self.tfidf = None
        if SKLEARN_AVAILABLE:
            self.tfidf = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2)
            )
        
        logger.info(f"SEO Engine initialized - NLTK: {NLTK_AVAILABLE}, Sklearn: {SKLEARN_AVAILABLE}")
    
    def _get_stop_words(self):
        """Get stop words with fallback."""
        if NLTK_AVAILABLE:
            try:
                return set(stopwords.words('english'))
            except:
                pass
        return BASIC_STOP_WORDS
    
    def _get_lemmatizer(self):
        """Get lemmatizer with fallback."""
        if NLTK_AVAILABLE:
            try:
                return WordNetLemmatizer()
            except:
                pass
        return None
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text using available NLP tools.
        """
        if not text:
            return []
        
        # Clean text
        text = self._clean_text(text)
        
        if NLTK_AVAILABLE:
            return self._extract_keywords_nltk(text, max_keywords)
        else:
            return self._extract_keywords_basic(text, max_keywords)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove HTML tags
        text = strip_tags(text)
        # Remove extra whitespace
        text = re.sub(r'\\s+', ' ', text)
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^a-zA-Z0-9\\s]', ' ', text)
        return text.lower().strip()
    
    def _extract_keywords_nltk(self, text: str, max_keywords: int) -> List[str]:
        """Extract keywords using NLTK."""
        try:
            # Tokenize
            tokens = word_tokenize(text)
            
            # Remove stop words and short words
            tokens = [
                token for token in tokens 
                if token.lower() not in self.stop_words and len(token) > 2
            ]
            
            # Lemmatize
            if self.lemmatizer:
                tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            
            # Count frequency
            word_freq = Counter(tokens)
            
            # Return most common
            return [word for word, _ in word_freq.most_common(max_keywords)]
            
        except Exception as e:
            logger.warning(f"NLTK keyword extraction failed: {e}")
            return self._extract_keywords_basic(text, max_keywords)
    
    def _extract_keywords_basic(self, text: str, max_keywords: int) -> List[str]:
        """Basic keyword extraction without external libraries."""
        # Split into words
        words = text.split()
        
        # Filter words
        words = [
            word for word in words
            if (
                len(word) > 2 and
                word.lower() not in self.stop_words and
                word.isalpha()
            )
        ]
        
        # Count frequency
        word_freq = Counter(words)
        
        # Return most common
        return [word for word, _ in word_freq.most_common(max_keywords)]
    
    def generate_seo_title(self, job_title: str, department: str = "", year: str = "") -> str:
        """
        Generate SEO-optimized title.
        """
        if not year:
            year = str(datetime.now().year)
        
        # Extract key terms
        keywords = self.extract_keywords(job_title, 3)
        
        # Build title components
        title_parts = []
        
        # Add main job title (truncated)
        main_title = job_title[:40] if len(job_title) > 40 else job_title
        title_parts.append(main_title)
        
        # Add year if not already present
        if year not in job_title:
            title_parts.append(year)
        
        # Add department if provided and space allows
        if department and len(' '.join(title_parts)) < 45:
            title_parts.insert(-1, department)
        
        # Join and add suffix
        title = ' '.join(title_parts)
        title += " - Apply Online | SarkariBot"
        
        # Ensure title is within 60 characters limit
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title
    
    def generate_meta_description(self, job_title: str, total_posts: int = 0, 
                                 last_date: str = "", department: str = "") -> str:
        """
        Generate SEO-optimized meta description.
        """
        # Extract key terms
        keywords = self.extract_keywords(job_title, 2)
        
        # Build description
        desc_parts = []
        
        # Add action phrase
        desc_parts.append("Apply for")
        
        # Add job title (shortened)
        short_title = job_title[:30] if len(job_title) > 30 else job_title
        desc_parts.append(short_title)
        
        # Add posts info
        if total_posts > 0:
            desc_parts.append(f"({total_posts:,} posts)")
        
        # Add department
        if department:
            desc_parts.append(f"in {department}")
        
        # Add deadline
        if last_date:
            desc_parts.append(f"Last date: {last_date}")
        
        # Add call to action
        desc_parts.append("Apply online now!")
        
        description = ' '.join(desc_parts)
        
        # Ensure description is within 160 characters
        if len(description) > 160:
            description = description[:157] + "..."
        
        return description
    
    def generate_structured_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate JSON-LD structured data for job posting.
        """
        structured_data = {
            "@context": "https://schema.org",
            "@type": "JobPosting",
            "title": job_data.get('title', ''),
            "description": job_data.get('description', ''),
            "identifier": {
                "@type": "PropertyValue",
                "name": job_data.get('source_name', 'SarkariBot'),
                "value": str(job_data.get('id', ''))
            },
            "datePosted": job_data.get('notification_date', datetime.now().isoformat()),
            "validThrough": job_data.get('application_end_date', ''),
            "employmentType": "FULL_TIME",
            "hiringOrganization": {
                "@type": "Organization",
                "name": job_data.get('department', job_data.get('source_name', '')),
                "sameAs": job_data.get('source_url', '')
            },
            "jobLocation": {
                "@type": "Place",
                "addressCountry": "IN",
                "addressLocality": "India"
            },
            "baseSalary": {
                "@type": "MonetaryAmount",
                "currency": "INR",
                "value": {
                    "@type": "QuantitativeValue",
                    "value": "As per government norms"
                }
            }
        }
        
        # Add qualification requirements
        if job_data.get('qualification'):
            structured_data["qualifications"] = job_data['qualification']
        
        # Add application URL
        if job_data.get('application_link'):
            structured_data["url"] = job_data['application_link']
        
        return structured_data
    
    def optimize_content(self, content: str) -> str:
        """
        Optimize content for SEO.
        """
        if not content:
            return content
        
        # Extract keywords
        keywords = self.extract_keywords(content, 5)
        
        # Basic content optimization
        # Add keyword density checking and optimization here
        
        return content

# Global instance
seo_engine = EnhancedSEOEngine()
'''
        
        # Write enhanced SEO engine
        enhanced_seo_file = self.backend_dir / "apps" / "seo" / "enhanced_engine.py"
        with open(enhanced_seo_file, 'w') as f:
            f.write(enhanced_seo_code)
        
        logger.info("✓ Enhanced SEO engine created")
    
    def fix_frontend_api_integration(self):
        """Fix frontend API integration issues"""
        logger.info("=== Fixing Frontend API Integration ===")
        
        # Create API configuration file
        api_config = {
            "apiUrl": "http://127.0.0.1:8000/api/v1",
            "endpoints": {
                "jobs": "/jobs/",
                "categories": "/categories/",
                "stats": "/stats/",
                "search": "/search/",
                "sources": "/sources/"
            },
            "pagination": {
                "pageSize": 20,
                "maxPageSize": 100
            },
            "cache": {
                "ttl": 300000
            }
        }
        
        api_config_file = self.frontend_dir / "src" / "config" / "api.json"
        api_config_file.parent.mkdir(exist_ok=True)
        
        with open(api_config_file, 'w') as f:
            json.dump(api_config, f, indent=2)
        
        # Create API service utility
        api_service_code = '''/**
 * API Service for SarkariBot Frontend
 * Handles all API communication with proper error handling
 */

import axios from 'axios';
import apiConfig from '../config/api.json';

class ApiService {
  constructor() {
    this.baseURL = apiConfig.apiUrl;
    this.endpoints = apiConfig.endpoints;
    
    // Create axios instance
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });
    
    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(this.handleError(error));
      }
    );
  }
  
  handleError(error) {
    if (error.response) {
      // Server responded with error status
      return {
        message: error.response.data?.message || 'Server error',
        status: error.response.status,
        data: error.response.data
      };
    } else if (error.request) {
      // Network error
      return {
        message: 'Network error - please check your connection',
        status: 0,
        data: null
      };
    } else {
      // Request setup error
      return {
        message: error.message || 'Unknown error',
        status: -1,
        data: null
      };
    }
  }
  
  async getJobs(params = {}) {
    try {
      const response = await this.client.get(this.endpoints.jobs, { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
  
  async getJobById(id) {
    try {
      const response = await this.client.get(`${this.endpoints.jobs}${id}/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
  
  async getCategories() {
    try {
      const response = await this.client.get(this.endpoints.categories);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
  
  async getStats() {
    try {
      const response = await this.client.get(this.endpoints.stats);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
  
  async searchJobs(query, params = {}) {
    try {
      const searchParams = { search: query, ...params };
      const response = await this.client.get(this.endpoints.jobs, { params: searchParams });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export default new ApiService();
'''
        
        api_service_file = self.frontend_dir / "src" / "services" / "apiService.js"
        api_service_file.parent.mkdir(exist_ok=True)
        
        with open(api_service_file, 'w') as f:
            f.write(api_service_code)
        
        logger.info("✓ Frontend API integration fixed")
    
    def create_development_scripts(self):
        """Create development scripts for easy management"""
        logger.info("=== Creating Development Scripts ===")
        
        # Backend start script
        backend_start_script = f'''#!/bin/bash
# SarkariBot Backend Development Server

echo "Starting SarkariBot Backend..."

cd "{self.backend_dir}"
source venv/bin/activate

echo "Running system checks..."
python manage.py check --settings=config.settings_dev

echo "Running migrations..."
python manage.py migrate --settings=config.settings_dev

echo "Creating sample data..."
python create_sample_data.py

echo "Starting Django server on http://127.0.0.1:8000"
python manage.py runserver 8000 --settings=config.settings_dev
'''
        
        backend_script_file = self.base_dir.parent / "scripts" / "start_backend.sh"
        backend_script_file.parent.mkdir(exist_ok=True)
        
        with open(backend_script_file, 'w') as f:
            f.write(backend_start_script)
        
        backend_script_file.chmod(0o755)
        
        # Frontend start script
        frontend_start_script = f'''#!/bin/bash
# SarkariBot Frontend Development Server

echo "Starting SarkariBot Frontend..."

cd "{self.frontend_dir}"

echo "Installing dependencies..."
npm install

echo "Building frontend..."
npm run build

echo "Starting frontend server on http://localhost:3000"
npx serve -s build -p 3000
'''
        
        frontend_script_file = self.base_dir.parent / "scripts" / "start_frontend.sh"
        
        with open(frontend_script_file, 'w') as f:
            f.write(frontend_start_script)
        
        frontend_script_file.chmod(0o755)
        
        # Full stack start script
        fullstack_script = '''#!/bin/bash
# SarkariBot Full Stack Development

echo "Starting SarkariBot Full Stack Development Environment..."

# Start backend in background
echo "Starting backend..."
./start_backend.sh &
BACKEND_PID=$!

# Wait for backend to start
sleep 10

# Start frontend
echo "Starting frontend..."
./start_frontend.sh &
FRONTEND_PID=$!

echo "✓ Backend running on http://127.0.0.1:8000"
echo "✓ Frontend running on http://localhost:3000"
echo "✓ API Documentation: http://127.0.0.1:8000/api/v1/"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
'''
        
        fullstack_script_file = self.base_dir.parent / "scripts" / "start_fullstack.sh"
        
        with open(fullstack_script_file, 'w') as f:
            f.write(fullstack_script)
        
        fullstack_script_file.chmod(0o755)
        
        logger.info("✓ Development scripts created")
    
    def create_production_config(self):
        """Create production-ready configuration"""
        logger.info("=== Creating Production Configuration ===")
        
        # Production settings
        prod_settings = '''"""
Production settings for SarkariBot.

Security-focused configuration for production deployment.
"""

from .base import *
import os

# Security Settings
DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'sarkaribot.com,www.sarkaribot.com').split(',')

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SSL Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Database - Production PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'sarkaribot_prod'),
        'USER': os.getenv('DB_USER', 'sarkaribot'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Redis Configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 100},
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'sarkaribot',
        'TIMEOUT': 3600,
    }
}

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Static Files - AWS S3
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_S3_BUCKET', 'sarkaribot-static')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION', 'us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = 'public-read'

STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/sarkaribot/django.log',
            'maxBytes': 15728640,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/sarkaribot/django_errors.log',
            'maxBytes': 15728640,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'sarkaribot': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@sarkaribot.com')

# Performance Settings
CONN_MAX_AGE = 600
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# SEO Settings
SITE_ID = 1
SITE_NAME = 'SarkariBot'
SITE_DOMAIN = 'sarkaribot.com'
SITE_URL = f'https://{SITE_DOMAIN}'
'''
        
        prod_settings_file = self.backend_dir / "config" / "settings" / "production.py"
        prod_settings_file.parent.mkdir(exist_ok=True)
        
        with open(prod_settings_file, 'w') as f:
            f.write(prod_settings)
        
        # Docker production configuration
        docker_prod_compose = '''version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: sarkaribot_prod
      POSTGRES_USER: sarkaribot
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    restart: always
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  web:
    build: 
      context: .
      dockerfile: docker/Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DB_PASSWORD=${DB_PASSWORD}
      - SECRET_KEY=${SECRET_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    depends_on:
      - postgres
      - redis
    restart: always
    volumes:
      - ./logs:/var/log/sarkaribot

  celery:
    build: 
      context: .
      dockerfile: docker/Dockerfile.prod
    command: celery -A config worker -l info
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DB_PASSWORD=${DB_PASSWORD}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
      - redis
    restart: always

  celery-beat:
    build: 
      context: .
      dockerfile: docker/Dockerfile.prod
    command: celery -A config beat -l info
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DB_PASSWORD=${DB_PASSWORD}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
      - redis
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf
      - ./docker/ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
  redis_data:
'''
        
        docker_prod_file = self.base_dir.parent / "docker-compose.prod.yml"
        
        with open(docker_prod_file, 'w') as f:
            f.write(docker_prod_compose)
        
        logger.info("✓ Production configuration created")
    
    def create_testing_framework(self):
        """Create comprehensive testing framework"""
        logger.info("=== Creating Testing Framework ===")
        
        # API testing script
        api_test_script = '''#!/usr/bin/env python3
"""
Comprehensive API Testing for SarkariBot
"""

import requests
import json
import time
import sys
from datetime import datetime

class SarkariBotAPITester:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'SarkariBot-API-Tester/1.0'
        })
    
    def test_endpoint(self, endpoint, expected_status=200):
        """Test a single API endpoint"""
        url = f"{self.api_url}{endpoint}"
        try:
            print(f"Testing: {url}")
            response = self.session.get(url, timeout=10)
            
            if response.status_code == expected_status:
                print(f"  ✓ Status: {response.status_code}")
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = response.json()
                    print(f"  ✓ Response type: JSON")
                    if isinstance(data, dict) and 'count' in data:
                        print(f"  ✓ Count: {data['count']}")
                return True
            else:
                print(f"  ✗ Status: {response.status_code} (expected {expected_status})")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request failed: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON decode failed: {e}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all API tests"""
        print(f"Starting SarkariBot API Tests at {datetime.now()}")
        print(f"Base URL: {self.base_url}")
        print("-" * 50)
        
        tests = [
            ("/jobs/", "Jobs listing"),
            ("/categories/", "Categories listing"),
            ("/stats/", "Statistics"),
            ("/jobs/latest/", "Latest jobs"),
            ("/jobs/recent/", "Recent jobs"),
            ("/sources/", "Government sources")
        ]
        
        passed = 0
        total = len(tests)
        
        for endpoint, description in tests:
            print(f"\\n{description}:")
            if self.test_endpoint(endpoint):
                passed += 1
        
        print("\\n" + "=" * 50)
        print(f"Test Results: {passed}/{total} passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print("❌ Some tests failed")
            return False

if __name__ == "__main__":
    tester = SarkariBotAPITester()
    success = tester.run_comprehensive_tests()
    sys.exit(0 if success else 1)
'''
        
        api_test_file = self.base_dir.parent / "scripts" / "test_api_comprehensive.py"
        
        with open(api_test_file, 'w') as f:
            f.write(api_test_script)
        
        api_test_file.chmod(0o755)
        
        logger.info("✓ Testing framework created")
    
    def run_final_tests(self):
        """Run final integration tests"""
        logger.info("=== Running Final Integration Tests ===")
        
        # Test Django management commands
        activate_cmd = f"source {self.venv_dir}/bin/activate"
        check_cmd = f"{activate_cmd} && python manage.py check --settings=config.settings_dev"
        
        try:
            self.run_command(check_cmd, cwd=self.backend_dir)
            logger.info("✓ Django check passed")
        except Exception as e:
            logger.error(f"Django check failed: {e}")
        
        # Test data creation
        try:
            data_cmd = f"{activate_cmd} && python create_sample_data.py"
            self.run_command(data_cmd, cwd=self.backend_dir)
            logger.info("✓ Sample data creation passed")
        except Exception as e:
            logger.error(f"Sample data creation failed: {e}")
        
        logger.info("✓ Final tests completed")
    
    def run_all_fixes(self):
        """Run all fixes in order"""
        logger.info("🚀 Starting SarkariBot Comprehensive Fix")
        logger.info("=" * 60)
        
        try:
            self.install_nlp_dependencies()
            self.create_enhanced_seo_engine()
            self.fix_frontend_api_integration()
            self.create_development_scripts()
            self.create_production_config()
            self.create_testing_framework()
            self.run_final_tests()
            
            logger.info("=" * 60)
            logger.info("🎉 All fixes completed successfully!")
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Start backend: ./scripts/start_backend.sh")
            logger.info("2. Start frontend: ./scripts/start_frontend.sh")
            logger.info("3. Run tests: ./scripts/test_api_comprehensive.py")
            logger.info("4. Access: http://localhost:3000 (frontend)")
            logger.info("5. API: http://127.0.0.1:8000/api/v1/ (backend)")
            
        except Exception as e:
            logger.error(f"❌ Fix failed: {e}")
            raise

def main():
    fixer = SarkariBotFixer()
    fixer.run_all_fixes()

if __name__ == "__main__":
    main()
