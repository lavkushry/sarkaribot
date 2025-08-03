#!/bin/bash

# SarkariBot Backend Development Server
# Starts Django development server with proper environment

echo "🚀 Starting SarkariBot Backend Server"
echo "===================================="

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/sarkaribot/backend"

echo "📁 Using backend directory: $BACKEND_DIR"

cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup_dev.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Django is installed
if ! python -c "import django" 2>/dev/null; then
    echo "❌ Django not found. Please run setup_dev.sh first."
    exit 1
fi

echo "🔧 Running system checks..."
python manage.py check --settings=config.settings

echo "🔧 Applying any pending migrations..."
python manage.py migrate --settings=config.settings

echo "📊 Creating sample data if needed..."
if [ -f "create_sample_data.py" ]; then
    python create_sample_data.py
fi

echo "🌐 Starting Django development server..."
echo "📍 Backend will be available at: http://localhost:8000"
echo "📍 Admin panel at: http://localhost:8000/admin/"
echo "📍 API documentation at: http://localhost:8000/api/docs/"
echo ""
echo "Press Ctrl+C to stop the server"

python manage.py runserver 8000 --settings=config.settings
