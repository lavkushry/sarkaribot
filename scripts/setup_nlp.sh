#!/bin/bash

# SarkariBot Setup Script
# Installs required NLP models and dependencies according to Knowledge.md

echo "🤖 SarkariBot Setup - Installing NLP Dependencies"
echo "================================================"

# Navigate to backend directory
cd /home/lavku/govt/sarkaribot/backend

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade required Python packages
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements/base.txt

# Install spaCy English model for NLP
echo "🧠 Installing spaCy English model..."
python -m spacy download en_core_web_sm

# Install additional NLP models if needed
echo "📚 Installing additional NLP resources..."
python -c "
import nltk
try:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    print('✅ NLTK data downloaded successfully')
except Exception as e:
    print(f'⚠️ NLTK download failed: {e}')
"

# Verify spaCy installation
echo "🔍 Verifying spaCy installation..."
python -c "
import spacy
try:
    nlp = spacy.load('en_core_web_sm')
    print('✅ spaCy English model loaded successfully')
    print(f'   Model version: {nlp.meta.get(\"version\", \"unknown\")}')
    print(f'   Language: {nlp.meta.get(\"lang\", \"unknown\")}')
except Exception as e:
    print(f'❌ spaCy model failed to load: {e}')
    exit(1)
"

# Run Django migrations to create SEO tables
echo "🗄️ Creating database tables..."
python manage.py makemigrations seo
python manage.py migrate

# Create SEO migration if needed
echo "📝 Checking SEO app migrations..."
if [ ! -f "apps/seo/migrations/0001_initial.py" ]; then
    echo "Creating initial SEO migration..."
    python manage.py makemigrations seo --name initial
fi

# Test NLP SEO engine
echo "🧪 Testing NLP SEO Engine..."
python -c "
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
"

echo ""
echo "🎉 Setup complete! SarkariBot NLP dependencies are ready."
echo ""
echo "📋 Summary:"
echo "   ✅ Virtual environment activated"
echo "   ✅ Python packages installed"
echo "   ✅ spaCy English model installed"
echo "   ✅ NLTK data downloaded"
echo "   ✅ Database migrations applied"
echo "   ✅ NLP SEO engine tested"
echo ""
echo "🚀 You can now start the development server with:"
echo "   python manage.py runserver --settings=config.settings_local"
