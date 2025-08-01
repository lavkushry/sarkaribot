#!/bin/bash

# SarkariBot Local Development Setup
# Sets up local development environment without PostgreSQL for testing

echo "🤖 SarkariBot Local Development Setup"
echo "===================================="

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/sarkaribot/backend"

echo "📁 Using backend directory: $BACKEND_DIR"

# Navigate to backend directory
cd "$BACKEND_DIR"

# Activate virtual environment
echo "📦 Activating virtual environment..."
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install core Django packages first (excluding PostgreSQL)
echo "📥 Installing core Django packages..."
pip install Django==4.2.14
pip install djangorestframework==3.14.0
pip install django-cors-headers==4.3.1
pip install django-filter==23.2
pip install django-extensions==3.2.3

# Install NLP packages
echo "🧠 Installing NLP packages..."
pip install spacy==3.6.1
pip install nltk==3.8.1

# Install other utilities
echo "🔧 Installing utilities..."
pip install python-decouple==3.8
pip install pillow==10.0.0
pip install python-slugify==8.0.1
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3

# Install spaCy English model
echo "📚 Installing spaCy English model..."
python -m spacy download en_core_web_sm

# Verify spaCy installation
echo "🔍 Verifying spaCy installation..."
python -c "
import spacy
try:
    nlp = spacy.load('en_core_web_sm')
    print('✅ spaCy English model loaded successfully')
    print(f'   Model version: {nlp.meta.get(\"version\", \"unknown\")}')
except Exception as e:
    print(f'❌ spaCy model failed to load: {e}')
    exit(1)
"

# Test Django setup
echo "🧪 Testing Django setup..."
python -c "
import django
print(f'✅ Django version: {django.VERSION}')
import rest_framework
print('✅ Django REST Framework imported successfully')
"

# Create SEO migrations
echo "📝 Creating SEO app migrations..."
python manage.py makemigrations seo --settings=config.settings_local --empty --name initial

# Test NLP SEO engine
echo "🧪 Testing NLP SEO Engine..."
python -c "
import sys
import os
sys.path.append(os.getcwd())
import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_local')
django.setup()

from apps.seo.engine import seo_engine

test_job_data = {
    'title': 'SSC CGL 2025 Notification',
    'description': 'Staff Selection Commission Combined Graduate Level Examination 2025',
    'source': 'SSC',
    'category': 'Central Government',
    'department': 'Staff Selection Commission',
    'total_posts': 5000,
    'application_end_date': '2025-09-15'
}

try:
    metadata = seo_engine.generate_seo_metadata(test_job_data)
    print('✅ SEO Engine working correctly')
    print(f'   Generated title: {metadata[\"seo_title\"]}')
    print(f'   Keywords count: {len(metadata[\"keywords\"])}')
    print(f'   Quality score: {metadata[\"quality_score\"]}')
except Exception as e:
    print(f'❌ SEO Engine test failed: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "🎉 Local development setup complete!"
echo ""
echo "📋 What's installed:"
echo "   ✅ Django 4.2.14"
echo "   ✅ Django REST Framework"  
echo "   ✅ spaCy with English model"
echo "   ✅ Core utilities"
echo ""
echo "🚀 You can now start development with:"
echo "   python manage.py runserver --settings=config.settings_local"
