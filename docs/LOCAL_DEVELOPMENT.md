# Local Development Guide

This guide helps you set up SarkariBot for local development without complex dependencies like PostgreSQL or Redis.

## Quick Setup (No PostgreSQL Required!)

### Option 1: Automated Setup (Recommended)

```bash
# From repository root
chmod +x scripts/setup_local_dev.sh
./scripts/setup_local_dev.sh
```

### Option 2: Manual Setup

```bash
# 1. Navigate to backend
cd sarkaribot/backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install development dependencies (no PostgreSQL!)
pip install -r requirements/development.txt

# 4. Copy environment file (pre-configured for SQLite)
cp .env.example .env

# 5. Run migrations
export DJANGO_SETTINGS_MODULE="config.settings_local"
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Start server
python manage.py runserver
```

## What's Different in Local Development?

| Component | Local Development | Production |
|-----------|------------------|------------|
| Database | SQLite (automatic) | PostgreSQL |
| Cache | Dummy cache | Redis |
| Task Queue | Synchronous | Celery + Redis |
| Dependencies | requirements/development.txt | requirements/production.txt |
| Settings | config.settings_local | config.settings.production |

## Configuration Files

### Local Development
- **Settings**: `config/settings_local.py`
- **Database**: SQLite (`sarkaribot_dev.sqlite3`)
- **Requirements**: `requirements/development.txt` (no PostgreSQL)
- **Env**: `.env` with `DB_ENGINE=sqlite3`

### Production
- **Settings**: `config/settings/production.py`
- **Database**: PostgreSQL
- **Requirements**: `requirements/production.txt` (includes PostgreSQL)
- **Env**: `.env` with `DB_ENGINE=postgresql`

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'psycopg2'"
**Solution**: You're using the wrong requirements file. Use `requirements/development.txt` for local development.

### Problem: Django can't find the database
**Solution**: Make sure you're using the correct settings module:
```bash
export DJANGO_SETTINGS_MODULE="config.settings_local"
```

### Problem: Permission denied for database
**Solution**: Local development uses SQLite - no database setup required. Check your `.env` file:
```
DB_ENGINE=sqlite3
DB_NAME=sarkaribot_dev.sqlite3
```

## Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests with local settings
export DJANGO_SETTINGS_MODULE="config.settings_local"
python manage.py test

# Or use pytest
pytest
```

## Adding New Features

1. **Models**: Add to appropriate app's `models.py`
2. **Migrations**: `python manage.py makemigrations`
3. **API**: Add serializers and viewsets
4. **Tests**: Add to `tests/` directory
5. **Run**: `python manage.py runserver`

## Moving to Production

When you're ready for production:

1. Install PostgreSQL and Redis
2. Update `.env` with production database settings
3. Install production requirements: `pip install -r requirements/production.txt`
4. Use production settings: `DJANGO_SETTINGS_MODULE=config.settings.production`

## Support

If you encounter issues with local development setup:
1. Check this guide
2. Review the automated setup script
3. Open an issue on GitHub with details about your environment