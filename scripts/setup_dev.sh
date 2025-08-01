#!/bin/bash

# SarkariBot Development Environment Setup
# Cross-platform setup script that works from any directory
# Follows Knowledge.md requirements for comprehensive development automation

set -e  # Exit on any error

echo "🤖 SarkariBot Development Environment Setup"
echo "==========================================="

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/sarkaribot/backend"
FRONTEND_DIR="$PROJECT_ROOT/sarkaribot/frontend"

echo "📁 Project root: $PROJECT_ROOT"
echo "📁 Backend: $BACKEND_DIR"
echo "📁 Frontend: $FRONTEND_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo ""
echo "🔍 Checking prerequisites..."

# Check Python version
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 12 ]; then
        print_status "Python $PYTHON_VERSION detected"
    else
        print_error "Python 3.12+ required, found $PYTHON_VERSION"
        echo "Please install Python 3.12 or later"
        exit 1
    fi
else
    print_error "Python 3 not found"
    echo "Please install Python 3.12 or later"
    exit 1
fi

# Check Node.js version
if command_exists node; then
    NODE_VERSION=$(node --version | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
    
    if [ "$NODE_MAJOR" -ge 18 ]; then
        print_status "Node.js $NODE_VERSION detected"
    else
        print_error "Node.js 18+ required, found $NODE_VERSION"
        echo "Please install Node.js 18 or later"
        exit 1
    fi
else
    print_error "Node.js not found"
    echo "Please install Node.js 18 or later"
    exit 1
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_status "npm $NPM_VERSION detected"
else
    print_error "npm not found"
    echo "Please install npm (usually comes with Node.js)"
    exit 1
fi

# Check directories exist
if [ ! -d "$BACKEND_DIR" ]; then
    print_error "Backend directory not found: $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    print_error "Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

print_status "All prerequisites met"

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

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
print_info "Installing development dependencies..."
pip install -r requirements/development.txt

print_status "Backend dependencies installed"

# Setup environment file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_info "Creating .env from .env.example..."
        cp .env.example .env
        print_warning "Please review and update .env file with your settings"
    else
        print_warning ".env.example not found, creating basic .env file..."
        cat > .env << EOF
DEBUG=True
SECRET_KEY=your-secret-key-change-this
DATABASE_URL=sqlite:///sarkaribot_dev.db
REDIS_URL=redis://localhost:6379/0
SCRAPING_ENABLED=False
EOF
    fi
    print_status ".env file created"
else
    print_status ".env file already exists"
fi

# Run migrations
print_info "Running database migrations..."
python manage.py migrate

print_status "Database migrations completed"

# Frontend setup
echo ""
echo "⚛️ Setting up Frontend..."

cd "$FRONTEND_DIR"

# Install frontend dependencies
print_info "Installing frontend dependencies..."
npm install

print_status "Frontend dependencies installed"

# Return to project root
cd "$PROJECT_ROOT"

print_status "Development environment setup completed!"

echo ""
echo "🎉 Setup Summary:"
echo "   ✅ Python virtual environment created and activated"
echo "   ✅ Backend dependencies installed"
echo "   ✅ Database migrations completed"
echo "   ✅ Frontend dependencies installed"
echo "   ✅ Environment configuration created"
echo ""
echo "🚀 Next steps:"
echo "   1. Review and update $BACKEND_DIR/.env file"
echo "   2. Run verification script: ./scripts/verify_setup.sh"
echo "   3. Start development servers:"
echo "      - Backend: ./scripts/start_backend.sh"
echo "      - Frontend: ./scripts/start_frontend.sh"
echo ""
echo "📚 For more information, see docs/DEVELOPMENT.md"