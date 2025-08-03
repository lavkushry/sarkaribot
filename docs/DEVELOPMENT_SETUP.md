# Docker Development Environment Setup Guide

## 🎯 Quick Start (30 seconds)

1. **Clone and Start**
   ```bash
   git clone https://github.com/lavkushry/sarkaribot.git
   cd sarkaribot
   ./scripts/dev.sh start
   ```

2. **Access Application**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - Admin: http://localhost:8000/admin

## 🛠️ Available Commands

### Using Scripts
```bash
# Linux/macOS
./scripts/dev.sh start
./scripts/dev.sh stop
./scripts/dev.sh logs

# Windows
scripts\dev.bat start
scripts\dev.bat stop
scripts\dev.bat logs
```

### Using Makefile (Linux/macOS)
```bash
make start
make stop
make logs
make help  # See all commands
```

## 📋 Development Workflow

### 1. Daily Development
```bash
# Start your day
make start

# View logs while developing
make logs

# Stop when done
make stop
```

### 2. Database Operations
```bash
# Run migrations
make migrate

# Create superuser
make createsuperuser

# Access database shell
make shell-db
```

### 3. Testing
```bash
# Backend tests
make test-backend

# Frontend tests
make test-frontend
```

### 4. Debugging
```bash
# View specific service logs
make logs-backend
make logs-frontend
make logs-celery

# Access Django shell
make shell-backend

# Check service status
make status
```

### 5. When Things Go Wrong
```bash
# Restart everything
make restart

# Complete rebuild
make rebuild

# Nuclear option (reset everything)
make reset
```

## 🔧 Service Architecture

The development environment includes:

- **PostgreSQL**: Database on port 5432
- **Redis**: Cache and message broker on port 6379
- **Django Backend**: API server on port 8000
- **React Frontend**: Development server on port 3000
- **Celery Worker**: Background task processor
- **Celery Beat**: Task scheduler
- **PgAdmin**: Database admin (optional) on port 8080

## 📁 File Structure

```
sarkaribot/
├── docker-compose.dev.yml    # Main development config
├── .env.dev                  # Development environment variables
├── Makefile                  # Convenient commands
├── scripts/
│   ├── dev.sh               # Linux/macOS helper script
│   ├── dev.bat              # Windows helper script
│   └── init-db.sql          # Database initialization
├── sarkaribot/
│   ├── backend/             # Django application
│   ├── frontend/            # React application
│   └── docker/              # Docker configuration
└── docs/
    └── DOCKER_TROUBLESHOOTING.md
```

## 🚀 First Time Setup

1. **Prerequisites**
   - Docker Desktop (Windows/macOS) or Docker Engine (Linux)
   - Git

2. **Clone Repository**
   ```bash
   git clone https://github.com/lavkushry/sarkaribot.git
   cd sarkaribot
   ```

3. **Start Development Environment**
   ```bash
   make start
   # or
   ./scripts/dev.sh start
   ```

4. **Create Superuser**
   ```bash
   make createsuperuser
   ```

5. **Access Application**
   - Frontend: http://localhost:3000
   - Admin: http://localhost:8000/admin

## 💡 Tips

### Hot Reloading
- **Frontend**: React dev server automatically reloads on changes
- **Backend**: Django dev server automatically reloads on Python changes

### Environment Variables
- Development settings are in `docker-compose.dev.yml`
- Additional environment variables can be added to `.env.dev`

### Database
- Data persists between container restarts
- To reset database: `make reset`

### Adding Packages
```bash
# Backend (Python packages)
docker compose -f docker-compose.dev.yml exec backend pip install package-name
# Then add to requirements/development.txt

# Frontend (npm packages)
docker compose -f docker-compose.dev.yml exec frontend npm install package-name
```

### Performance
- First build takes 5-10 minutes (downloads dependencies)
- Subsequent starts take 30-60 seconds
- Hot reloading is immediate

## 🆘 Troubleshooting

If you encounter issues, see the [Docker Troubleshooting Guide](DOCKER_TROUBLESHOOTING.md).

Quick fixes:
```bash
# Most common fix
make restart

# If containers are corrupted
make rebuild

# If everything is broken
make reset
```

## 🌟 Production Deployment

This setup is for **development only**. For production deployment:

1. Use production Docker files
2. Configure proper environment variables
3. Use production database settings
4. Enable HTTPS
5. Set up monitoring and logging

See deployment documentation for production setup.

## ❤️ Contributing

When contributing:

1. Start development environment: `make start`
2. Make your changes with hot reloading
3. Run tests: `make test-backend test-frontend`
4. Ensure services work: `make status`
5. Submit your PR

The Docker environment ensures all contributors work in identical setups!