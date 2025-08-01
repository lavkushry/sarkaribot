#!/bin/bash

# SarkariBot Development Helper Script
# This script provides convenient commands for Docker-based development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

show_help() {
    echo "SarkariBot Development Helper Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start         Start all development services"
    echo "  stop          Stop all services"
    echo "  restart       Restart all services"
    echo "  build         Build all Docker images"
    echo "  logs          Show logs from all services"
    echo "  logs-backend  Show backend logs only"
    echo "  logs-frontend Show frontend logs only"
    echo "  logs-celery   Show Celery worker logs"
    echo "  shell-backend Open backend shell"
    echo "  shell-db      Open database shell"
    echo "  test-backend  Run backend tests"
    echo "  test-frontend Run frontend tests"
    echo "  migrate       Run database migrations"
    echo "  collectstatic Collect static files"
    echo "  createsuperuser Create Django superuser"
    echo "  clean         Clean up Docker resources"
    echo "  status        Show status of all services"
    echo "  urls          Show access URLs"
    echo "  pgadmin       Start with PgAdmin"
    echo "  help          Show this help message"
    echo ""
}

start_services() {
    log_info "Starting SarkariBot development environment..."
    cd "$PROJECT_ROOT"
    check_docker
    docker compose -f docker-compose.dev.yml up -d
    log_success "All services started!"
    show_urls
}

start_with_pgadmin() {
    log_info "Starting SarkariBot development environment with PgAdmin..."
    cd "$PROJECT_ROOT"
    check_docker
    docker compose -f docker-compose.dev.yml --profile tools up -d
    log_success "All services started with PgAdmin!"
    show_urls
    echo ""
    log_info "PgAdmin is available at: http://localhost:8080"
    log_info "  Username: admin@sarkaribot.local"
    log_info "  Password: admin123"
}

stop_services() {
    log_info "Stopping all services..."
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev.yml down
    log_success "All services stopped!"
}

restart_services() {
    log_info "Restarting all services..."
    stop_services
    start_services
}

build_images() {
    log_info "Building Docker images..."
    cd "$PROJECT_ROOT"
    check_docker
    docker compose -f docker-compose.dev.yml build
    log_success "All images built successfully!"
}

show_logs() {
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev.yml logs -f "${@:2}"
}

show_backend_logs() {
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev.yml logs -f backend
}

show_frontend_logs() {
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev.yml logs -f frontend
}

show_celery_logs() {
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev.yml logs -f celery_worker celery_beat
}

backend_shell() {
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev.yml exec backend python manage.py shell
}

db_shell() {
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev.yml exec db psql -U postgres -d sarkaribot_dev
}

run_backend_tests() {
    log_info "Running backend tests..."
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev.yml exec backend python manage.py test
}

run_frontend_tests() {
    log_info "Running frontend tests..."
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev.yml exec frontend npm test -- --coverage --watchAll=false
}

run_migrations() {
    log_info "Running database migrations..."
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev.yml exec backend python manage.py migrate
    log_success "Migrations completed!"
}

collect_static() {
    log_info "Collecting static files..."
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev.yml exec backend python manage.py collectstatic --noinput
    log_success "Static files collected!"
}

create_superuser() {
    log_info "Creating Django superuser..."
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
}

clean_docker() {
    log_warning "This will remove all stopped containers, unused networks, images, and build cache."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning Docker resources..."
        docker system prune -f
        docker volume prune -f
        log_success "Docker cleanup completed!"
    else
        log_info "Cleanup cancelled."
    fi
}

show_status() {
    cd "$PROJECT_ROOT"
    echo "Service Status:"
    docker compose -f docker-compose.dev.yml ps
}

show_urls() {
    echo ""
    log_success "Development environment is ready!"
    echo ""
    echo "📱 Access URLs:"
    echo "  Frontend:     http://localhost:3000"
    echo "  Backend API:  http://localhost:8000/api/v1/"
    echo "  Admin Panel:  http://localhost:8000/admin/"
    echo "  API Docs:     http://localhost:8000/api/docs/"
    echo ""
    echo "🔧 Database:"
    echo "  PostgreSQL:   localhost:5432"
    echo "  Redis:        localhost:6379"
    echo ""
    echo "📋 Useful commands:"
    echo "  View logs:    ./scripts/dev.sh logs"
    echo "  Backend shell: ./scripts/dev.sh shell-backend"
    echo "  Run tests:    ./scripts/dev.sh test-backend"
    echo ""
}

# Main command handling
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    build)
        build_images
        ;;
    logs)
        show_logs "$@"
        ;;
    logs-backend)
        show_backend_logs
        ;;
    logs-frontend)
        show_frontend_logs
        ;;
    logs-celery)
        show_celery_logs
        ;;
    shell-backend)
        backend_shell
        ;;
    shell-db)
        db_shell
        ;;
    test-backend)
        run_backend_tests
        ;;
    test-frontend)
        run_frontend_tests
        ;;
    migrate)
        run_migrations
        ;;
    collectstatic)
        collect_static
        ;;
    createsuperuser)
        create_superuser
        ;;
    clean)
        clean_docker
        ;;
    status)
        show_status
        ;;
    urls)
        show_urls
        ;;
    pgadmin)
        start_with_pgadmin
        ;;
    help|*)
        show_help
        ;;
esac