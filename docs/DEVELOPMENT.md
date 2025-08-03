# Development Environment Setup Guide

This guide provides comprehensive instructions for setting up the SarkariBot development environment.

## Quick Start (Automated)

For automated setup, use the provided scripts:

```bash
# 1. Main development setup
./scripts/setup_dev.sh

# 2. Verify installation
./scripts/verify_setup.sh

# 3. Setup development tools (linting, testing)
./scripts/setup_tools.sh

# 4. Start development servers
./scripts/start_backend.sh    # Terminal 1
./scripts/start_frontend.sh   # Terminal 2
```

## Manual Setup (Network Issues or Custom Installation)

If automated scripts fail due to network issues, follow these manual steps:

### Prerequisites

- **Python 3.12+** - `python3 --version`
- **Node.js 18+** - `node --version`
- **npm** - `npm --version`
- **Git** - `git --version`

### Backend Setup

```bash
# 1. Navigate to backend directory
cd sarkaribot/backend

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install dependencies (try different approaches if network issues)
# Option A: Full development dependencies
pip install -r requirements/development.txt

# Option B: Core dependencies only (if network issues)
pip install Django==4.2.14
pip install djangorestframework==3.14.0
pip install django-cors-headers==4.3.1

# Option C: Install from local wheel files (if available)
pip install --find-links /path/to/wheels --no-index package_name

# 6. Create environment file
cp .env.example .env
# Edit .env file with appropriate settings

# 7. Run database migrations
python manage.py migrate

# 8. Create superuser (optional)
python manage.py createsuperuser
```

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd sarkaribot/frontend

# 2. Install dependencies
npm install

# If npm install fails due to network issues:
# - Use npm cache: npm install --cache /path/to/cache
# - Use offline mode: npm install --offline
# - Use different registry: npm install --registry https://registry.npmjs.org/
```

### NLP Dependencies

```bash
# In backend directory with activated virtual environment
pip install spacy==3.6.1
pip install nltk==3.8.1

# Download spaCy model
python -m spacy download en_core_web_sm

# Download NLTK data (optional)
python -c "
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
"
```

## Development Tools Setup

### Code Quality Tools

```bash
# In backend directory
pip install black flake8 isort mypy bandit pytest pytest-django pytest-cov

# In frontend directory  
npm install --save-dev eslint prettier @typescript-eslint/eslint-plugin
```

### Configuration Files

The setup scripts automatically create these configuration files:

- **Backend**: `.flake8`, `pyproject.toml`, `pytest.ini`, `.bandit`
- **Frontend**: `.eslintrc.json`, `.prettierrc`, `.prettierignore`

## Verification

Run the verification script to check your setup:

```bash
./scripts/verify_setup.sh
```

This will check:
- System requirements (Python, Node.js, npm, Git)
- Project structure
- Backend environment (virtual env, Django, packages)
- Frontend environment (node_modules, React, build process)
- Development tools (linting, testing)
- Documentation

## Starting Development

### Backend Server

```bash
# Method 1: Using script
./scripts/start_backend.sh

# Method 2: Manual
cd sarkaribot/backend
source venv/bin/activate
python manage.py runserver
```

Access:
- API: http://localhost:8000/api/v1/
- Admin: http://localhost:8000/admin/
- Documentation: http://localhost:8000/api/docs/

### Frontend Server

```bash
# Method 1: Using script
./scripts/start_frontend.sh

# Method 2: Manual
cd sarkaribot/frontend
npm start
```

Access: http://localhost:3000

## Development Workflow

### Code Quality

Before committing, run:

```bash
# Backend (in backend directory)
source venv/bin/activate
black .                    # Format code
flake8 .                   # Lint code
isort .                    # Sort imports
mypy .                     # Type checking
bandit -r apps/            # Security audit

# Frontend (in frontend directory)
npm run lint               # Lint JavaScript/TypeScript
npm run format             # Format code
npm run type-check         # TypeScript checking
```

### Testing

```bash
# Backend tests
cd sarkaribot/backend
source venv/bin/activate
pytest                     # Run all tests
pytest --cov              # Run with coverage
pytest -v tests/unit/      # Run specific directory

# Frontend tests
cd sarkaribot/frontend
npm test                   # Run Jest tests
npm run test:coverage      # Run with coverage
```

## Troubleshooting

### Common Issues

#### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

#### Database Issues
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
```

#### Node.js Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### Network/Proxy Issues
```bash
# Configure pip for proxy
pip install --proxy http://proxy.company.com:port package_name

# Configure npm for proxy
npm config set proxy http://proxy.company.com:port
npm config set https-proxy http://proxy.company.com:port

# Use different registry
pip install -i https://pypi.org/simple/ package_name
npm install --registry https://registry.npmjs.org/
```

#### Permission Issues (Linux/Mac)
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Fix ownership
sudo chown -R $USER:$USER .
```

### Environment Variables

Key environment variables in `.env`:

```env
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///sarkaribot_dev.db

# Redis (for production)
REDIS_URL=redis://localhost:6379/0

# Feature flags
SCRAPING_ENABLED=False
SEO_AUTOMATION=False
CELERY_ALWAYS_EAGER=True
```

## IDE Setup

### Visual Studio Code

Install recommended extensions:
- Python
- Pylance
- Black Formatter
- ES7+ React/Redux/React-Native snippets
- Prettier - Code formatter
- ESLint

### PyCharm

- Enable Django support
- Configure Black as external tool
- Set pytest as test runner
- Configure code style to match project settings

## Additional Resources

- [Project README](../README.md) - General project information
- [API Documentation](docs/API.md) - API endpoint details
- [Architecture Documentation](docs/ARCHITECTURE.md) - System architecture
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute

## Support

If you encounter issues:

1. Check this guide for common solutions
2. Run the verification script: `./scripts/verify_setup.sh`
3. Check the project issues on GitHub
4. Ask for help in project discussions

## Script Reference

- `setup_dev.sh` - Main development environment setup
- `setup_simple.sh` - Minimal setup for network-limited environments
- `setup_tools.sh` - Development tools and linting setup
- `setup_nlp.sh` - NLP dependencies installation
- `verify_setup.sh` - Comprehensive environment verification
- `start_backend.sh` - Start Django development server
- `start_frontend.sh` - Start React development server