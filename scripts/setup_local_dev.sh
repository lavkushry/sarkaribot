#!/bin/bash

# SarkariBot Local Development Setup Script
# This script sets up the development environment without requiring PostgreSQL

set -e  # Exit on any error

echo "🚀 Setting up SarkariBot for local development..."
echo "📋 This setup uses SQLite (no PostgreSQL required)"

# Check if we're in the backend directory or repository root
if [ -f "manage.py" ]; then
    # We're in the backend directory
    BACKEND_DIR="."
elif [ -f "sarkaribot/backend/manage.py" ]; then
    # We're in the repository root
    BACKEND_DIR="sarkaribot/backend"
elif [ -f "backend/manage.py" ]; then
    # We're in the sarkaribot directory
    BACKEND_DIR="backend"
else
    echo "❌ Please run this script from the repository root, sarkaribot directory, or backend directory"
    exit 1
fi

# Navigate to backend directory
cd "$BACKEND_DIR"

echo "📂 Working in directory: $(pwd)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install development requirements (without PostgreSQL)
echo "📚 Installing development dependencies..."
pip install -r requirements/development.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file for local development..."
    cp .env.example .env
    echo "✅ Created .env file with SQLite configuration"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p media
mkdir -p static
mkdir -p staticfiles

# Run Django checks
echo "🔍 Running Django system checks..."
export DJANGO_SETTINGS_MODULE="config.settings_local"
python manage.py check

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser prompt
echo ""
echo "👤 Would you like to create a superuser account? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    python manage.py createsuperuser
fi

# Success message
echo ""
echo "🎉 Local development setup complete!"
echo ""
echo "📊 Configuration:"
echo "   • Database: SQLite (sarkaribot_dev.sqlite3)"
echo "   • Cache: Dummy cache (no Redis required)"
echo "   • Debug mode: Enabled"
echo "   • Settings: config.settings_local"
echo ""
echo "🚀 To start development:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Start Django server: python manage.py runserver"
echo "   3. Access admin panel: http://localhost:8000/admin/"
echo "   4. Access API docs: http://localhost:8000/api/docs/"
echo ""
echo "💡 For frontend development:"
echo "   cd ../frontend"
echo "   npm install"
echo "   npm start"
echo ""
echo "✨ Happy coding!"
