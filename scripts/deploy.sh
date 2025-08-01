#!/bin/bash
# SarkariBot Production Deployment Script
# This script sets up the complete SarkariBot system for production

set -e  # Exit on any error

echo "🚀 SarkariBot Production Deployment Starting..."
echo "================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is running"

# Start Docker services
print_info "Starting Docker services..."
cd /home/lavku/govt

if docker-compose up -d; then
    print_status "Docker services started successfully"
else
    print_error "Failed to start Docker services"
    exit 1
fi

# Wait for databases to be ready
print_info "Waiting for databases to initialize..."
sleep 10

# Check database health
print_info "Checking database health..."
if docker exec sarkaribot_postgres_dev pg_isready -U sarkaribot_user > /dev/null 2>&1; then
    print_status "Development database is ready"
else
    print_warning "Development database not ready, waiting longer..."
    sleep 5
fi

if docker exec sarkaribot_postgres_preprod pg_isready -U sarkaribot_user > /dev/null 2>&1; then
    print_status "Pre-production database is ready"
else
    print_warning "Pre-production database not ready, waiting longer..."
    sleep 5
fi

# Setup Python environment
print_info "Setting up Python environment..."
cd /home/lavku/govt/sarkaribot/backend

if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
print_status "Python virtual environment activated"

# Install/update dependencies
print_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt 2>/dev/null || {
    print_warning "requirements.txt not found, installing core dependencies..."
    pip install django djangorestframework psycopg2-binary django-redis redis \
                celery user-agents scikit-learn pandas numpy drf-spectacular \
                django-cors-headers django-filter
}

print_status "Dependencies installed"

# Run migrations for both environments
print_info "Running database migrations..."

# Development database
print_info "Migrating development database..."
if python manage.py migrate --settings=config.settings_dev_docker; then
    print_status "Development database migrated"
else
    print_error "Failed to migrate development database"
    exit 1
fi

# Pre-production database
print_info "Migrating pre-production database..."
if python manage.py migrate --settings=config.settings_preprod; then
    print_status "Pre-production database migrated"
else
    print_error "Failed to migrate pre-production database"
    exit 1
fi

# Create superuser for development (if not exists)
print_info "Creating development superuser..."
python manage.py shell --settings=config.settings_dev_docker << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@sarkaribot.com', 'admin123')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF

# Create sample data if not exists
print_info "Creating sample data..."
python manage.py create_sample_data --count=20 --settings=config.settings_dev_docker 2>/dev/null || {
    print_warning "Sample data already exists or creation failed"
}

# Collect static files
print_info "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings_dev_docker 2>/dev/null || {
    print_warning "Static files collection skipped"
}

# Start development server
print_info "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000 --settings=config.settings_dev_docker &
DEV_SERVER_PID=$!

# Wait for server to start
sleep 3

# Test API endpoints
print_info "Testing API endpoints..."
API_BASE="http://localhost:8000/api/v1"

# Test basic endpoints
if curl -s "${API_BASE}/jobs/" > /dev/null; then
    print_status "Jobs API working"
else
    print_error "Jobs API not responding"
fi

if curl -s "${API_BASE}/categories/" > /dev/null; then
    print_status "Categories API working"
else
    print_error "Categories API not responding"
fi

if curl -s "${API_BASE}/stats/" > /dev/null; then
    print_status "Stats API working"
else
    print_error "Stats API not responding"
fi

# Display final status
echo ""
echo "🎉 SarkariBot Deployment Complete!"
echo "=================================="
echo ""
print_status "Services Running:"
echo "  📊 Development Server: http://localhost:8000"
echo "  🗄️  Development DB: localhost:5432"
echo "  🗄️  Pre-prod DB: localhost:5433"
echo "  🔧 PgAdmin: http://localhost:8080"
echo "  📈 Redis: localhost:6379"
echo ""
print_status "API Endpoints:"
echo "  📋 Jobs: http://localhost:8000/api/v1/jobs/"
echo "  📁 Categories: http://localhost:8000/api/v1/categories/"
echo "  📊 Stats: http://localhost:8000/api/v1/stats/"
echo "  📚 API Docs: http://localhost:8000/api/docs/"
echo ""
print_status "Admin Access:"
echo "  👤 Username: admin"
echo "  🔑 Password: admin123"
echo "  🌐 Admin URL: http://localhost:8000/admin/"
echo ""
print_status "Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
print_info "Development server PID: $DEV_SERVER_PID"
print_info "To stop the server: kill $DEV_SERVER_PID"
echo ""
print_status "SarkariBot is ready for development and testing! 🚀"
