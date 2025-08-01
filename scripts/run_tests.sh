#!/bin/bash

# Test Coverage Verification Script
# Runs all test suites and verifies coverage thresholds

set -e

echo "🧪 Starting SarkariBot Test Coverage Verification"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "sarkaribot/backend/manage.py" ]; then
    print_error "Please run this script from the repository root"
    exit 1
fi

# Set environment variables
export DJANGO_SETTINGS_MODULE=config.settings.testing
export PYTHONPATH="${PWD}/sarkaribot/backend:${PYTHONPATH}"

print_status "Setting up test environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

print_status "Installing backend dependencies..."
cd sarkaribot/backend
pip install -r requirements/development.txt

print_status "Running backend tests with coverage..."
echo ""

# Run Django system checks
print_status "Running Django system checks..."
python manage.py check --deploy

# Run migrations
print_status "Running test migrations..."
python manage.py migrate --run-syncdb

# Run backend tests with coverage
print_status "Running backend test suite..."
pytest \
    --cov=apps \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    --cov-report=xml \
    --cov-fail-under=85 \
    --verbose \
    --tb=short \
    tests/

BACKEND_EXIT_CODE=$?

# Check backend coverage threshold
if [ $BACKEND_EXIT_CODE -eq 0 ]; then
    print_success "Backend tests passed with ≥85% coverage"
else
    print_error "Backend tests failed or coverage below 85%"
fi

# Run critical path tests with higher threshold
print_status "Running critical path tests (95% coverage requirement)..."
pytest \
    tests/test_critical_paths.py \
    --cov=apps \
    --cov-report=term-missing \
    --cov-fail-under=95 \
    --verbose \
    -m critical

CRITICAL_EXIT_CODE=$?

if [ $CRITICAL_EXIT_CODE -eq 0 ]; then
    print_success "Critical path tests passed with ≥95% coverage"
else
    print_error "Critical path tests failed or coverage below 95%"
fi

# Move to frontend directory
cd ../frontend

print_status "Installing frontend dependencies..."
npm ci

print_status "Running frontend linting..."
npm run lint || print_warning "Frontend linting issues found"

print_status "Running frontend tests with coverage..."
npm run test:coverage

FRONTEND_EXIT_CODE=$?

if [ $FRONTEND_EXIT_CODE -eq 0 ]; then
    print_success "Frontend tests passed with ≥80% coverage"
else
    print_error "Frontend tests failed or coverage below 80%"
fi

# Go back to root
cd ../..

# Generate coverage report summary
print_status "Generating coverage summary..."

echo ""
echo "📊 Test Coverage Summary"
echo "========================"

# Backend coverage summary
if [ -f "sarkaribot/backend/coverage.xml" ]; then
    BACKEND_COVERAGE=$(python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('sarkaribot/backend/coverage.xml')
root = tree.getroot()
coverage = root.attrib.get('line-rate', '0')
print(f'{float(coverage) * 100:.1f}%')
")
    echo "Backend Coverage: $BACKEND_COVERAGE"
else
    echo "Backend Coverage: Unable to calculate"
fi

# Frontend coverage summary
if [ -f "sarkaribot/frontend/coverage/lcov.info" ]; then
    FRONTEND_COVERAGE=$(grep -E "^LF:|^LH:" sarkaribot/frontend/coverage/lcov.info | \
        awk 'BEGIN{lf=0;lh=0} /^LF:/{lf+=$2} /^LH:/{lh+=$2} END{if(lf>0) print (lh/lf)*100"%"; else print "0%"}')
    echo "Frontend Coverage: $FRONTEND_COVERAGE"
else
    echo "Frontend Coverage: Unable to calculate"
fi

# Critical paths coverage
echo "Critical Paths: ≥95% (required)"

echo ""
echo "📁 Coverage Reports Generated:"
echo "  Backend HTML: sarkaribot/backend/htmlcov/index.html"
echo "  Backend XML: sarkaribot/backend/coverage.xml"
echo "  Frontend HTML: sarkaribot/frontend/coverage/lcov-report/index.html"

# Final status
echo ""
TOTAL_FAILURES=0

if [ $BACKEND_EXIT_CODE -ne 0 ]; then
    print_error "❌ Backend tests failed"
    TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
else
    print_success "✅ Backend tests passed"
fi

if [ $CRITICAL_EXIT_CODE -ne 0 ]; then
    print_error "❌ Critical path tests failed"
    TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
else
    print_success "✅ Critical path tests passed"
fi

if [ $FRONTEND_EXIT_CODE -ne 0 ]; then
    print_error "❌ Frontend tests failed"
    TOTAL_FAILURES=$((TOTAL_FAILURES + 1))
else
    print_success "✅ Frontend tests passed"
fi

echo ""
if [ $TOTAL_FAILURES -eq 0 ]; then
    print_success "🎉 All tests passed with required coverage thresholds!"
    echo ""
    echo "Coverage Requirements Met:"
    echo "  ✅ Backend: ≥85% coverage"
    echo "  ✅ Frontend: ≥80% coverage"
    echo "  ✅ Critical Paths: ≥95% coverage"
    exit 0
else
    print_error "💥 $TOTAL_FAILURES test suite(s) failed"
    echo ""
    echo "Please fix the failing tests and ensure coverage thresholds are met:"
    echo "  🎯 Backend: ≥85% coverage required"
    echo "  🎯 Frontend: ≥80% coverage required"
    echo "  🎯 Critical Paths: ≥95% coverage required"
    exit 1
fi