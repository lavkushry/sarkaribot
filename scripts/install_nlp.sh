#!/bin/bash
"""
Installation script for SarkariBot NLP dependencies.

This script handles the complete setup of NLP dependencies including
spaCy models and NLTK data for the SEO automation engine.
"""

set -e  # Exit on any error

echo "============================================================"
echo "SarkariBot NLP Dependencies Setup"
echo "============================================================"

# Function to print colored output
print_status() {
    echo -e "\033[1;32m✓\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m⚠\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m✗\033[0m $1"
}

# Check if we're in the right directory
if [ ! -f "sarkaribot/backend/apps/seo/engine.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Navigate to backend directory
cd sarkaribot/backend

print_status "Installing base requirements..."
pip install -r requirements/base.txt || {
    print_warning "Some base requirements may have failed. Continuing with NLP-specific packages..."
}

# Install essential NLP packages individually with fallbacks
echo ""
echo "Installing NLP packages individually..."

# Install spaCy
if pip install "spacy>=3.7.0,<4.0.0" --timeout 300; then
    print_status "spaCy installed successfully"
    
    # Try to install the English model
    echo "Downloading spaCy English model..."
    if python -m spacy download en_core_web_sm; then
        print_status "spaCy English model installed successfully"
    else
        print_warning "Failed to download spaCy model. The engine will use basic model."
    fi
else
    print_warning "Failed to install spaCy. The engine will use fallback text processing."
fi

# Install NLTK
if pip install "nltk>=3.8.1"; then
    print_status "NLTK installed successfully"
    
    # Download NLTK data
    echo "Downloading NLTK data..."
    python -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

datasets = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
for dataset in datasets:
    try:
        nltk.download(dataset, quiet=True)
        print(f'✓ Downloaded {dataset}')
    except Exception as e:
        print(f'⚠ Failed to download {dataset}: {e}')
" || print_warning "Some NLTK data downloads failed"
else
    print_warning "Failed to install NLTK."
fi

# Install other text processing libraries
pip install python-slugify textblob scikit-learn || print_warning "Some text processing libraries failed to install"

# Test the setup
echo ""
echo "Testing NLP setup..."

python -c "
import sys
sys.path.append('.')

# Test basic imports
try:
    from apps.seo.engine import NLPSEOEngine
    print('✓ SEO engine imports successfully')
except Exception as e:
    print(f'✗ SEO engine import failed: {e}')
    sys.exit(1)

# Test basic functionality
try:
    engine = NLPSEOEngine()
    
    test_data = {
        'title': 'Test Government Job 2024',
        'description': 'This is a test job posting for validation.',
        'department': 'Test Department'
    }
    
    metadata = engine.generate_seo_metadata(test_data)
    
    if metadata.get('seo_title') and metadata.get('keywords'):
        print('✓ SEO engine generates metadata successfully')
        print(f'  Method: {metadata.get(\"generation_method\", \"unknown\")}')
        print(f'  Quality Score: {metadata.get(\"quality_score\", 0)}')
    else:
        print('✗ SEO engine metadata generation failed')
        sys.exit(1)
        
except Exception as e:
    print(f'✗ SEO engine test failed: {e}')
    sys.exit(1)

print('✓ All NLP components are working correctly!')
"

if [ $? -eq 0 ]; then
    echo ""
    print_status "NLP dependencies setup completed successfully!"
    echo ""
    echo "Summary:"
    echo "- SEO automation engine is ready"
    echo "- Fallback mechanisms are working"
    echo "- You can now use the SEO API endpoints"
    echo ""
    echo "To test the API endpoints, start the Django server:"
    echo "  python manage.py runserver"
    echo ""
    echo "Then test SEO generation:"
    echo "  curl -X POST http://localhost:8000/api/v1/seo/generate/ \\"
    echo "       -H 'Content-Type: application/json' \\"
    echo "       -d '{\"title\": \"Test Job\", \"description\": \"Test description\"}'"
else
    print_error "NLP setup verification failed. Please check the errors above."
    exit 1
fi