# Docker Development Environment Troubleshooting Guide

This guide helps resolve common issues when setting up and running the SarkariBot Docker development environment.

## Quick Start Commands

```bash
# Start development environment
./scripts/dev.sh start

# View logs if something goes wrong
./scripts/dev.sh logs

# Stop everything
./scripts/dev.sh stop

# Clean up and restart fresh
./scripts/dev.sh clean
./scripts/dev.sh build
./scripts/dev.sh start
```

## Common Issues and Solutions

### 1. Docker Not Running

**Error**: `Cannot connect to the Docker daemon`

**Solutions**:
- **Linux/macOS**: Start Docker service: `sudo systemctl start docker`
- **Windows/macOS**: Start Docker Desktop application
- **All platforms**: Check Docker is installed: `docker --version`

### 2. Port Already in Use

**Error**: `Port 3000/8000/5432 is already in use`

**Solutions**:
```bash
# Find what's using the port (Linux/macOS)
sudo lsof -i :3000
sudo lsof -i :8000
sudo lsof -i :5432

# Kill the process using the port
sudo kill -9 <PID>

# Or stop existing SarkariBot containers
./scripts/dev.sh stop
```

**Windows**:
```cmd
# Find what's using the port
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Kill the process
taskkill /PID <PID> /F
```

### 3. Frontend Not Loading

**Error**: Frontend shows blank page or connection refused

**Checks**:
1. Verify container is running: `./scripts/dev.sh status`
2. Check frontend logs: `./scripts/dev.sh logs-frontend`
3. Verify environment variables in docker-compose.dev.yml
4. Try rebuilding: `./scripts/dev.sh build`

**Common fixes**:
```bash
# Clear node_modules and reinstall
docker compose -f docker-compose.dev.yml exec frontend rm -rf node_modules
docker compose -f docker-compose.dev.yml exec frontend npm install

# Or rebuild the frontend container
docker compose -f docker-compose.dev.yml build frontend
docker compose -f docker-compose.dev.yml up -d frontend
```

### 4. Backend API Not Responding

**Error**: `502 Bad Gateway` or connection refused to backend

**Debugging steps**:
```bash
# Check backend logs
./scripts/dev.sh logs-backend

# Check if database is ready
./scripts/dev.sh shell-db

# Run migrations manually
./scripts/dev.sh migrate

# Check backend shell
./scripts/dev.sh shell-backend
```

**Common fixes**:
```bash
# Restart backend container
docker compose -f docker-compose.dev.yml restart backend

# Rebuild backend if needed
docker compose -f docker-compose.dev.yml build backend
```

### 5. Database Connection Issues

**Error**: `could not connect to server: Connection refused`

**Solutions**:
```bash
# Check database status
./scripts/dev.sh status

# Check database logs
docker compose -f docker-compose.dev.yml logs db

# Reset database volume (WARNING: destroys data)
./scripts/dev.sh stop
docker volume rm sarkaribot_postgres_dev_data
./scripts/dev.sh start
```

### 6. Celery Workers Not Starting

**Error**: Celery worker exits or doesn't process tasks

**Debugging**:
```bash
# Check Celery logs
./scripts/dev.sh logs-celery

# Check Redis connection
docker compose -f docker-compose.dev.yml exec redis redis-cli ping

# Restart Celery services
docker compose -f docker-compose.dev.yml restart celery_worker celery_beat
```

### 7. File Changes Not Reflected (Hot Reload Issues)

**Symptoms**: Code changes don't appear in the browser/application

**Frontend fixes**:
```bash
# Enable polling in docker-compose.dev.yml (already configured)
# WATCHPACK_POLLING=true is set

# If still not working, restart frontend
docker compose -f docker-compose.dev.yml restart frontend
```

**Backend fixes**:
```bash
# Django dev server should auto-reload, but if not:
docker compose -f docker-compose.dev.yml restart backend
```

### 8. Permission Issues (Linux/macOS)

**Error**: `Permission denied` when writing files

**Solutions**:
```bash
# Fix file permissions
sudo chown -R $USER:$USER ./sarkaribot

# Or use user namespace mapping in Docker (add to docker-compose.dev.yml):
user: "${UID:-1000}:${GID:-1000}"
```

### 9. Memory/Performance Issues

**Symptoms**: Slow build times, containers crashing

**Solutions**:
```bash
# Increase Docker memory (Docker Desktop settings)
# Recommended: 4GB+ RAM, 2GB+ swap

# Clean up Docker resources
./scripts/dev.sh clean

# Remove unused images
docker image prune -a

# Monitor resource usage
docker stats
```

### 10. SSL/HTTPS Issues

**Error**: HTTPS warnings or certificate issues

**Note**: Development environment uses HTTP only. For HTTPS:
```bash
# Use a reverse proxy like nginx-proxy or traefik
# Or access via HTTP: http://localhost:3000
```

## Platform-Specific Issues

### Windows with WSL2

**Common issues**:
- File watching problems: Ensure code is in WSL2 filesystem, not Windows filesystem
- Performance: Move project to WSL2 home directory (`/home/username/`)
- Line endings: Configure Git: `git config --global core.autocrlf false`

### macOS Apple Silicon (M1/M2)

**Build issues**:
```bash
# Force platform for compatibility
docker compose -f docker-compose.dev.yml build --build-arg BUILDPLATFORM=linux/amd64
```

### Linux Permission Issues

**Docker socket permission**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

## Environment Variables Issues

### Missing .env File

**Error**: Environment variables not loaded

**Solution**:
```bash
# Copy example file
cp sarkaribot/backend/.env.example sarkaribot/backend/.env

# Edit with your settings
nano sarkaribot/backend/.env
```

### Database URL Format

Ensure correct format in .env:
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/sarkaribot_dev
```

## Performance Optimization

### Speed Up Builds

```bash
# Use BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Cache package installations
# (Already configured in Dockerfiles)
```

### Reduce Resource Usage

```bash
# Run only essential services
docker compose -f docker-compose.dev.yml up db redis backend frontend

# Skip tools like PgAdmin unless needed
# (Use --profile tools to include)
```

## Reset Everything (Nuclear Option)

If all else fails, complete reset:

```bash
# Stop everything
./scripts/dev.sh stop

# Remove all containers and volumes
docker compose -f docker-compose.dev.yml down -v --remove-orphans

# Clean Docker system
docker system prune -a -f
docker volume prune -f

# Rebuild everything
./scripts/dev.sh build
./scripts/dev.sh start

# Recreate database and superuser
./scripts/dev.sh migrate
./scripts/dev.sh createsuperuser
```

## Getting Help

### Check Service Status
```bash
./scripts/dev.sh status
./scripts/dev.sh urls
```

### View Logs
```bash
# All services
./scripts/dev.sh logs

# Specific service
./scripts/dev.sh logs-backend
./scripts/dev.sh logs-frontend
./scripts/dev.sh logs-celery
```

### Access Service Shells
```bash
# Django shell
./scripts/dev.sh shell-backend

# Database shell
./scripts/dev.sh shell-db

# Container bash shell
docker compose -f docker-compose.dev.yml exec backend bash
docker compose -f docker-compose.dev.yml exec frontend sh
```

### Health Checks

Services include health checks. Check status:
```bash
docker compose -f docker-compose.dev.yml ps
```

Healthy services show `healthy` status.

## Support

If you're still having issues:

1. **Check logs**: Always check service logs first
2. **GitHub Issues**: Create an issue with logs and environment details
3. **Documentation**: Review the main README.md
4. **Community**: Ask in GitHub Discussions

### When Creating Issues

Include:
- Operating system and version
- Docker version: `docker --version`
- Error messages and logs
- Steps to reproduce
- Output of `./scripts/dev.sh status`