# Django Settings Structure

This document explains the Django settings structure for SarkariBot and how to use it for different environments.

## Overview

SarkariBot uses environment-specific Django settings to ensure proper configuration across development, staging, and production environments. The settings are organized using a modular approach that promotes consistency and maintainability.

## Settings Structure

```
config/
├── settings/
│   ├── __init__.py           # Settings package documentation
│   ├── base.py              # Common settings for all environments
│   ├── development.py       # Local development settings
│   └── production.py        # Production deployment settings
├── settings_local.py        # Quick local setup (minimal config)
├── settings_legacy_*.py     # Legacy settings (for reference only)
└── .env.example            # Environment variables template
```

## Environment Configuration

### 1. Development Environment (Recommended)

Use this for local development with full functionality:

```bash
# Set environment
export DJANGO_SETTINGS_MODULE=config.settings.development

# Or run commands directly
python manage.py runserver --settings=config.settings.development
```

**Features:**
- SQLite database (no setup required)
- Console email backend (emails printed to console)
- Debug mode enabled
- Dummy cache (no Redis required)
- Synchronous Celery tasks
- Django Debug Toolbar (if installed)
- Detailed logging

### 2. Production Environment

Use this for production deployment:

```bash
# Set environment
export DJANGO_SETTINGS_MODULE=config.settings.production

# Or in your deployment scripts
python manage.py migrate --settings=config.settings.production
```

**Features:**
- PostgreSQL database
- Redis cache and message broker
- Security headers and SSL enforcement
- File-based logging with rotation
- Sentry error tracking
- Static file compression
- Rate limiting

### 3. Quick Local Setup

Use this for minimal setup and testing:

```bash
# Use local settings directly
python manage.py runserver --settings=config.settings_local
```

**Features:**
- Minimal configuration
- SQLite database
- No external dependencies
- Perfect for quick testing

## Environment Variables

All settings use environment variables for configuration. Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
# Edit .env with your specific values
```

### Key Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `False` |
| `SECRET_KEY` | Django secret key | Required |
| `DB_ENGINE` | Database engine | `sqlite3` |
| `DB_NAME` | Database name | `db_dev.sqlite3` |
| `CACHE_BACKEND` | Cache backend | `dummy` |
| `EMAIL_BACKEND` | Email backend | `console` |

See `.env.example` for a complete list of available variables.

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
python setup_dev.py

# Start development server
python manage.py runserver
```

### Option 2: Manual Setup

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Create directories
mkdir -p logs media static staticfiles

# 3. Run migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Start server
python manage.py runserver
```

## Switching Between Environments

### Using Environment Variables

```bash
# Development
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py runserver

# Production
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py migrate
```

### Using Command Line

```bash
# Development
python manage.py runserver --settings=config.settings.development

# Production
python manage.py migrate --settings=config.settings.production

# Quick local
python manage.py shell --settings=config.settings_local
```

## Common Tasks

### Running Migrations

```bash
# Development
python manage.py makemigrations
python manage.py migrate

# Production
python manage.py migrate --settings=config.settings.production
```

### Collecting Static Files

```bash
# Development (optional)
python manage.py collectstatic

# Production (required)
python manage.py collectstatic --settings=config.settings.production
```

### Running Tests

```bash
# Use development settings for testing
python manage.py test
```

## Deployment Configuration

### Production Checklist

1. **Required Environment Variables:**
   - `SECRET_KEY` - Strong secret key
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Database credentials
   - `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` - Email settings
   - `CACHE_URL` - Redis cache URL
   - `CELERY_BROKER_URL` - Redis broker URL

2. **Security Settings:**
   - Set `DEBUG=False`
   - Configure proper `ALLOWED_HOSTS`
   - Enable SSL settings
   - Set secure cookie flags

3. **Performance Settings:**
   - Configure database connection pooling
   - Set up Redis cache
   - Configure static file serving
   - Set up log rotation

### Docker Deployment

```bash
# Use production settings in Docker
ENV DJANGO_SETTINGS_MODULE=config.settings.production
```

## Troubleshooting

### Common Issues

1. **Import Error:** Make sure you're using the correct settings module
2. **Database Issues:** Check your database configuration in `.env`
3. **Cache Issues:** Verify Redis is running for production
4. **Static Files:** Run `collectstatic` for production deployment

### Debug Commands

```bash
# Check configuration
python manage.py check

# Show current settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)

# Validate database
python manage.py dbshell
```

## Legacy Files

The following files are kept for reference but should not be used:

- `settings_legacy_*.py` - Old settings files
- `settings.py` - Old monolithic settings

These files may be removed in future versions.

## Best Practices

1. **Always use environment variables** for sensitive data
2. **Never commit `.env` files** to version control
3. **Use development settings** for local development
4. **Test with production settings** before deployment
5. **Keep settings DRY** by using the base settings
6. **Document custom settings** in your `.env` file

## Need Help?

- Check the `.env.example` file for available options
- Run `python setup_dev.py` for automated setup
- Review the settings files for configuration details
- Check Django documentation for advanced configuration