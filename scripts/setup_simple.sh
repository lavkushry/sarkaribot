#!/bin/bash

# SarkariBot Simple Development Setup
# Minimal setup focusing on core dependencies

set -e

echo "🤖 SarkariBot Simple Development Setup"
echo "======================================"

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/sarkaribot/backend"
FRONTEND_DIR="$PROJECT_ROOT/sarkaribot/frontend"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

echo "📁 Project root: $PROJECT_ROOT"
echo "📁 Backend: $BACKEND_DIR"
echo "📁 Frontend: $FRONTEND_DIR"

# Backend setup
echo ""
echo "🐍 Setting up Backend..."

cd "$BACKEND_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Install core dependencies only
print_info "Installing core dependencies..."
pip install --upgrade pip

# Install Django and essential packages first
pip install Django==4.2.14
pip install djangorestframework==3.14.0
pip install django-cors-headers==4.3.1

print_status "Core Django dependencies installed"

# Setup environment file
if [ ! -f ".env" ]; then
    print_info "Creating .env file for development..."
    cat > .env << 'EOF'
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///sarkaribot_dev.db
REDIS_URL=redis://localhost:6379/0
SCRAPING_ENABLED=False
SEO_AUTOMATION=False
CELERY_ALWAYS_EAGER=True
EOF
    print_status ".env file created"
else
    print_status ".env file already exists"
fi

# Run migrations
print_info "Running database migrations..."
python manage.py migrate

print_status "Backend basic setup completed"

# Frontend setup
echo ""
echo "⚛️ Setting up Frontend..."

cd "$FRONTEND_DIR"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    print_error "Frontend package.json not found"
    exit 1
fi

# Install frontend dependencies with timeout handling
print_info "Installing frontend dependencies..."
if timeout 120 npm install; then
    print_status "Frontend dependencies installed"
else
    print_warning "Frontend installation timed out, but basic setup continues"
fi

# Return to project root
cd "$PROJECT_ROOT"

print_status "Basic development environment setup completed!"

echo ""
echo "🎉 Setup Summary:"
echo "   ✅ Python virtual environment created"
echo "   ✅ Core Django dependencies installed"
echo "   ✅ Database migrations completed"
echo "   ✅ Environment configuration created"
echo "   ⚠️  Additional dependencies may need manual installation"
echo ""
echo "🚀 Next steps:"
echo "   1. Install additional dependencies: pip install -r requirements/development.txt"
echo "   2. Install NLP dependencies: ./scripts/setup_nlp.sh"
echo "   3. Run verification: ./scripts/verify_setup.sh"
echo "   4. Start development servers:"
echo "      - Backend: ./scripts/start_backend.sh"
echo "      - Frontend: ./scripts/start_frontend.sh"
echo ""
echo "💡 For network issues, install dependencies manually as needed."