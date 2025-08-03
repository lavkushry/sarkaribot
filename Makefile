# SarkariBot Development Makefile
# This provides convenient shortcuts for Docker-based development

.PHONY: help start stop restart build logs test clean status urls

# Default target
help: ## Show this help message
	@echo "SarkariBot Development Commands"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

start: ## Start all development services
	@echo "🚀 Starting SarkariBot development environment..."
	docker compose -f docker-compose.dev.yml up -d
	@echo "✅ All services started!"
	@make urls

stop: ## Stop all services
	@echo "🛑 Stopping all services..."
	docker compose -f docker-compose.dev.yml down
	@echo "✅ All services stopped!"

restart: ## Restart all services
	@make stop
	@make start

build: ## Build all Docker images
	@echo "🔨 Building Docker images..."
	docker compose -f docker-compose.dev.yml build
	@echo "✅ All images built successfully!"

logs: ## Show logs from all services
	docker compose -f docker-compose.dev.yml logs -f

logs-backend: ## Show backend logs only
	docker compose -f docker-compose.dev.yml logs -f backend

logs-frontend: ## Show frontend logs only
	docker compose -f docker-compose.dev.yml logs -f frontend

logs-celery: ## Show Celery worker logs
	docker compose -f docker-compose.dev.yml logs -f celery_worker celery_beat

shell-backend: ## Open Django shell
	docker compose -f docker-compose.dev.yml exec backend python manage.py shell

shell-db: ## Open database shell
	docker compose -f docker-compose.dev.yml exec db psql -U postgres -d sarkaribot_dev

test-backend: ## Run backend tests
	@echo "🧪 Running backend tests..."
	docker compose -f docker-compose.dev.yml exec backend python manage.py test

test-frontend: ## Run frontend tests
	@echo "🧪 Running frontend tests..."
	docker compose -f docker-compose.dev.yml exec frontend npm test -- --coverage --watchAll=false

migrate: ## Run database migrations
	@echo "🗃️ Running database migrations..."
	docker compose -f docker-compose.dev.yml exec backend python manage.py migrate
	@echo "✅ Migrations completed!"

collectstatic: ## Collect static files
	@echo "📦 Collecting static files..."
	docker compose -f docker-compose.dev.yml exec backend python manage.py collectstatic --noinput
	@echo "✅ Static files collected!"

createsuperuser: ## Create Django superuser
	@echo "👤 Creating Django superuser..."
	docker compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser

clean: ## Clean up Docker resources
	@echo "🧹 Cleaning Docker resources..."
	docker system prune -f
	docker volume prune -f
	@echo "✅ Docker cleanup completed!"

status: ## Show status of all services
	@echo "📊 Service Status:"
	docker compose -f docker-compose.dev.yml ps

urls: ## Show access URLs
	@echo ""
	@echo "🌐 SarkariBot Development Environment Ready!"
	@echo ""
	@echo "📱 Frontend:      http://localhost:3000"
	@echo "🔧 Backend API:   http://localhost:8000/api/v1/"
	@echo "⚙️  Admin Panel:   http://localhost:8000/admin/"
	@echo "📖 API Docs:      http://localhost:8000/api/docs/"
	@echo ""
	@echo "🗄️  Database:      localhost:5432"
	@echo "🔴 Redis:         localhost:6379"
	@echo ""

pgadmin: ## Start with PgAdmin
	@echo "🚀 Starting with PgAdmin..."
	docker compose -f docker-compose.dev.yml --profile tools up -d
	@make urls
	@echo ""
	@echo "🔧 PgAdmin:       http://localhost:8080"
	@echo "   Username:      admin@sarkaribot.local"
	@echo "   Password:      admin123"

# Development workflow shortcuts
dev: start ## Alias for start

rebuild: ## Stop, clean, build, and start
	@make stop
	@make clean
	@make build
	@make start

reset: ## Nuclear option - reset everything
	@echo "💥 Resetting everything..."
	docker compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -a -f
	docker volume prune -f
	@make build
	@make start
	@make migrate
	@echo "✅ Environment reset complete!"