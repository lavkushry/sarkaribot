#!/bin/bash

# SarkariBot Development Environment Verification
# Comprehensive verification of development setup
# Validates all components required for development

set -e

echo "🔍 SarkariBot Development Environment Verification"
echo "================================================="

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/sarkaribot/backend"
FRONTEND_DIR="$PROJECT_ROOT/sarkaribot/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to print colored output
print_check() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if [ "$2" = "PASS" ]; then
        echo -e "${GREEN}✅ PASS${NC} $1"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    elif [ "$2" = "FAIL" ]; then
        echo -e "${RED}❌ FAIL${NC} $1"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    elif [ "$2" = "WARN" ]; then
        echo -e "${YELLOW}⚠️ WARN${NC} $1"
    else
        echo -e "${BLUE}ℹ️ INFO${NC} $1"
    fi
}

print_section() {
    echo ""
    echo -e "${BLUE}📋 $1${NC}"
    echo "----------------------------------------"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. System Requirements Check
print_section "System Requirements"

# Python version check
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 12 ]; then
        print_check "Python $PYTHON_VERSION (>= 3.12)" "PASS"
    else
        print_check "Python $PYTHON_VERSION (>= 3.12 required)" "FAIL"
    fi
else
    print_check "Python 3 installation" "FAIL"
fi

# Node.js version check
if command_exists node; then
    NODE_VERSION=$(node --version | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
    
    if [ "$NODE_MAJOR" -ge 18 ]; then
        print_check "Node.js $NODE_VERSION (>= 18)" "PASS"
    else
        print_check "Node.js $NODE_VERSION (>= 18 required)" "FAIL"
    fi
else
    print_check "Node.js installation" "FAIL"
fi

# npm check
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_check "npm $NPM_VERSION" "PASS"
else
    print_check "npm installation" "FAIL"
fi

# Git check
if command_exists git; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    print_check "Git $GIT_VERSION" "PASS"
else
    print_check "Git installation" "WARN"
fi

# 2. Project Structure Check
print_section "Project Structure"

# Check main directories
if [ -d "$PROJECT_ROOT" ]; then
    print_check "Project root directory" "PASS"
else
    print_check "Project root directory" "FAIL"
fi

if [ -d "$BACKEND_DIR" ]; then
    print_check "Backend directory" "PASS"
else
    print_check "Backend directory" "FAIL"
fi

if [ -d "$FRONTEND_DIR" ]; then
    print_check "Frontend directory" "PASS"
else
    print_check "Frontend directory" "FAIL"
fi

# Check key files
if [ -f "$BACKEND_DIR/manage.py" ]; then
    print_check "Django manage.py file" "PASS"
else
    print_check "Django manage.py file" "FAIL"
fi

if [ -f "$FRONTEND_DIR/package.json" ]; then
    print_check "Frontend package.json file" "PASS"
else
    print_check "Frontend package.json file" "FAIL"
fi

# 3. Backend Environment Check
print_section "Backend Environment"

cd "$BACKEND_DIR"

# Virtual environment check
if [ -d "venv" ]; then
    print_check "Python virtual environment" "PASS"
    
    # Activate virtual environment for tests
    source venv/bin/activate
    
    # Django check
    if python -c "import django; print('Django', django.VERSION)" >/dev/null 2>&1; then
        DJANGO_VERSION=$(python -c "import django; print('.'.join(map(str, django.VERSION[:2])))")
        print_check "Django $DJANGO_VERSION installation" "PASS"
    else
        print_check "Django installation" "FAIL"
    fi
    
    # Django REST Framework check
    if python -c "import rest_framework" >/dev/null 2>&1; then
        print_check "Django REST Framework" "PASS"
    else
        print_check "Django REST Framework" "FAIL"
    fi
    
    # spaCy check
    if python -c "import spacy" >/dev/null 2>&1; then
        print_check "spaCy installation" "PASS"
        
        # spaCy model check
        if python -c "import spacy; spacy.load('en_core_web_sm')" >/dev/null 2>&1; then
            print_check "spaCy English model" "PASS"
        else
            print_check "spaCy English model" "FAIL"
        fi
    else
        print_check "spaCy installation" "FAIL"
    fi
    
    # Other key packages
    PACKAGES=("celery" "requests" "beautifulsoup4" "scrapy" "redis")
    for package in "${PACKAGES[@]}"; do
        if python -c "import $package" >/dev/null 2>&1; then
            print_check "$package package" "PASS"
        else
            print_check "$package package" "FAIL"
        fi
    done
    
else
    print_check "Python virtual environment" "FAIL"
fi

# Environment file check
if [ -f ".env" ]; then
    print_check ".env configuration file" "PASS"
else
    print_check ".env configuration file" "FAIL"
fi

# Database check
if [ -f "sarkaribot_dev.db" ] || [ -f "db.sqlite3" ]; then
    print_check "Development database" "PASS"
else
    print_check "Development database" "WARN"
fi

# Django settings check
if python manage.py check --settings=config.settings >/dev/null 2>&1; then
    print_check "Django configuration" "PASS"
else
    print_check "Django configuration" "FAIL"
fi

# 4. Frontend Environment Check
print_section "Frontend Environment"

cd "$FRONTEND_DIR"

# node_modules check
if [ -d "node_modules" ]; then
    print_check "Frontend dependencies (node_modules)" "PASS"
else
    print_check "Frontend dependencies (node_modules)" "FAIL"
fi

# Key dependencies check
if [ -f "package.json" ]; then
    # React check
    if npm list react >/dev/null 2>&1; then
        print_check "React installation" "PASS"
    else
        print_check "React installation" "FAIL"
    fi
    
    # TypeScript check
    if npm list typescript >/dev/null 2>&1; then
        print_check "TypeScript installation" "PASS"
    else
        print_check "TypeScript installation" "WARN"
    fi
fi

# Build check
if npm run build >/dev/null 2>&1; then
    print_check "Frontend build process" "PASS"
else
    print_check "Frontend build process" "FAIL"
fi

# 5. Development Tools Check
print_section "Development Tools"

cd "$BACKEND_DIR"

# Linting tools
if python -c "import black" >/dev/null 2>&1; then
    print_check "Black code formatter" "PASS"
else
    print_check "Black code formatter" "FAIL"
fi

if python -c "import flake8" >/dev/null 2>&1; then
    print_check "Flake8 linter" "PASS"
else
    print_check "Flake8 linter" "FAIL"
fi

# Testing tools
if python -c "import pytest" >/dev/null 2>&1; then
    print_check "Pytest testing framework" "PASS"
else
    print_check "Pytest testing framework" "FAIL"
fi

# 6. API and Services Check
print_section "API and Services"

cd "$BACKEND_DIR"

# Django admin check
if python manage.py shell -c "from django.contrib.auth import get_user_model; print('Admin accessible')" >/dev/null 2>&1; then
    print_check "Django admin accessibility" "PASS"
else
    print_check "Django admin accessibility" "FAIL"
fi

# 7. Documentation Check
print_section "Documentation"

cd "$PROJECT_ROOT"

# README check
if [ -f "README.md" ]; then
    print_check "Project README" "PASS"
else
    print_check "Project README" "FAIL"
fi

# Documentation directory
if [ -d "docs" ]; then
    print_check "Documentation directory" "PASS"
else
    print_check "Documentation directory" "FAIL"
fi

# CONTRIBUTING guide
if [ -f "CONTRIBUTING.md" ] || [ -f "docs/CONTRIBUTING.md" ]; then
    print_check "Contributing guidelines" "PASS"
else
    print_check "Contributing guidelines" "WARN"
fi

# Final Summary
echo ""
echo "🏁 Verification Summary"
echo "======================"
echo -e "Total checks: ${BLUE}$TOTAL_CHECKS${NC}"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical checks passed! Your development environment is ready.${NC}"
    echo ""
    echo "🚀 You can now start development:"
    echo "   - Backend: ./scripts/start_backend.sh"
    echo "   - Frontend: ./scripts/start_frontend.sh"
    exit 0
else
    echo -e "${RED}❌ $FAILED_CHECKS checks failed. Please fix the issues above.${NC}"
    echo ""
    echo "💡 To fix issues, try running:"
    echo "   - Setup script: ./scripts/setup_dev.sh"
    echo "   - NLP setup: ./scripts/setup_nlp.sh"
    exit 1
fi