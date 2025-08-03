#!/bin/bash

# SarkariBot Development Tools Setup
# Sets up linting, testing, and quality assurance tools
# Follows Knowledge.md standards for code quality

set -e

echo "🔧 SarkariBot Development Tools Setup"
echo "====================================="

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

print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

# Backend Tools Setup
echo ""
echo "🐍 Setting up Backend Development Tools..."

cd "$BACKEND_DIR"

# Ensure virtual environment is activated
if [ -d "venv" ]; then
    source venv/bin/activate
    print_status "Virtual environment activated"
else
    print_warning "Virtual environment not found. Run setup_dev.sh first."
    exit 1
fi

# Install/upgrade development tools
print_info "Installing development and testing tools..."
pip install --upgrade \
    black==23.7.0 \
    flake8==6.0.0 \
    isort==5.12.0 \
    mypy==1.5.1 \
    bandit==1.7.5 \
    pytest==7.4.2 \
    pytest-django==4.5.2 \
    pytest-cov==4.1.0 \
    factory-boy==3.3.0 \
    faker==19.6.2

print_status "Backend development tools installed"

# Create .flake8 configuration
print_info "Creating .flake8 configuration..."
cat > .flake8 << 'EOF'
[flake8]
max-line-length = 88
extend-ignore = E203, E266, E501, W503
max-complexity = 10
exclude = 
    migrations,
    __pycache__,
    venv,
    .git,
    .tox,
    .eggs,
    *.egg
per-file-ignores =
    __init__.py:F401
    settings*.py:E501
EOF

# Create pyproject.toml for Black and isort
print_info "Creating pyproject.toml configuration..."
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 88
target-version = ['py312']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | venv
  | _build
  | buck-out
  | build
  | dist
  | migrations
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_django = "django"
known_first_party = "apps,config"
sections = ["FUTURE","STDLIB","THIRDPARTY","DJANGO","FIRSTPARTY","LOCALFOLDER"]

[tool.mypy]
python_version = "3.12"
check_untyped_defs = true
ignore_missing_imports = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_unused_configs = true
exclude = [
    "migrations/",
    "venv/",
]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
addopts = "--cov=apps --cov-report=html --cov-report=term-missing"
testpaths = ["tests"]
EOF

# Create pytest configuration
print_info "Creating pytest.ini configuration..."
cat > pytest.ini << 'EOF'
[tool:pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
addopts = 
    --cov=apps 
    --cov-report=html 
    --cov-report=term-missing
    --cov-fail-under=80
    --verbose
testpaths = tests
EOF

# Create bandit configuration
print_info "Creating .bandit configuration..."
cat > .bandit << 'EOF'
[bandit]
exclude = /tests/,/venv/,/migrations/
skips = B101,B601
EOF

# Frontend Tools Setup
echo ""
echo "⚛️ Setting up Frontend Development Tools..."

cd "$FRONTEND_DIR"

# Install development dependencies
print_info "Installing frontend development tools..."
npm install --save-dev \
    @typescript-eslint/eslint-plugin \
    @typescript-eslint/parser \
    eslint \
    eslint-config-react-app \
    eslint-plugin-react \
    eslint-plugin-react-hooks \
    prettier \
    husky \
    lint-staged

# Create ESLint configuration
print_info "Creating .eslintrc.json configuration..."
cat > .eslintrc.json << 'EOF'
{
  "extends": [
    "react-app",
    "react-app/jest"
  ],
  "plugins": [
    "react",
    "react-hooks",
    "@typescript-eslint"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": 2021,
    "sourceType": "module",
    "ecmaFeatures": {
      "jsx": true
    }
  },
  "rules": {
    "react/jsx-uses-react": "error",
    "react/jsx-uses-vars": "error",
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "@typescript-eslint/no-unused-vars": "error",
    "no-console": "warn",
    "prefer-const": "error"
  },
  "settings": {
    "react": {
      "version": "detect"
    }
  }
}
EOF

# Create Prettier configuration
print_info "Creating .prettierrc configuration..."
cat > .prettierrc << 'EOF'
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
EOF

# Create Prettier ignore file
print_info "Creating .prettierignore..."
cat > .prettierignore << 'EOF'
build
node_modules
dist
coverage
public
*.md
package-lock.json
EOF

# Update package.json scripts
print_info "Adding scripts to package.json..."
npm pkg set scripts.lint="eslint src --ext .js,.jsx,.ts,.tsx"
npm pkg set scripts.lint:fix="eslint src --ext .js,.jsx,.ts,.tsx --fix"
npm pkg set scripts.format="prettier --write src/**/*.{js,jsx,ts,tsx,json,css,scss,md}"
npm pkg set scripts.format:check="prettier --check src/**/*.{js,jsx,ts,tsx,json,css,scss,md}"
npm pkg set scripts.type-check="tsc --noEmit"

# Setup Git hooks with Husky
print_info "Setting up Git hooks with Husky..."
npx husky install

# Create pre-commit hook
cat > .husky/pre-commit << 'EOF'
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

cd sarkaribot/frontend && npm run lint && npm run format:check
cd ../backend && source venv/bin/activate && black --check . && flake8 . && isort --check-only .
EOF

chmod +x .husky/pre-commit

# Setup lint-staged
cat > .lintstagedrc.json << 'EOF'
{
  "*.{js,jsx,ts,tsx}": [
    "eslint --fix",
    "prettier --write"
  ],
  "*.{json,css,scss,md}": [
    "prettier --write"
  ]
}
EOF

# Create comprehensive testing setup
echo ""
echo "🧪 Setting up Testing Framework..."

cd "$BACKEND_DIR"

# Create tests directory structure if it doesn't exist
mkdir -p tests/unit tests/integration tests/fixtures

# Create conftest.py for pytest
print_info "Creating pytest configuration..."
cat > tests/conftest.py << 'EOF'
"""
Pytest configuration and fixtures for SarkariBot tests.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.sources.models import GovernmentSource
from apps.jobs.models import JobCategory

User = get_user_model()

@pytest.fixture
def admin_user():
    """Create an admin user for tests."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='testpass123'
    )

@pytest.fixture
def government_source():
    """Create a test government source."""
    return GovernmentSource.objects.create(
        name='Test SSC',
        display_name='Staff Selection Commission',
        base_url='https://ssc.nic.in',
        active=True,
        scrape_frequency=24,
        config_json={
            'selectors': {
                'title': '.job-title',
                'description': '.job-desc'
            }
        }
    )

@pytest.fixture
def job_category():
    """Create a test job category."""
    return JobCategory.objects.create(
        name='Latest Jobs',
        slug='latest-jobs',
        description='Most recent job postings',
        position=1
    )
EOF

# Create a sample test file
print_info "Creating sample test file..."
cat > tests/test_example.py << 'EOF'
"""
Example test file to verify testing setup.
"""
import pytest
from django.test import TestCase


class TestDevelopmentSetup(TestCase):
    """Test that development environment is properly configured."""
    
    def test_django_settings(self):
        """Test that Django settings are accessible."""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'DEBUG'))
    
    def test_database_connection(self):
        """Test that database connection works."""
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)


@pytest.mark.django_db
def test_user_creation():
    """Test user creation functionality."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')
EOF

# Return to project root
cd "$PROJECT_ROOT"

# Create comprehensive development documentation
echo ""
echo "📚 Creating development documentation..."

# Create DEVELOPMENT.md
cat > docs/DEVELOPMENT.md << 'EOF'
# Development Guide

## Quick Start

1. **Setup Development Environment**
   ```bash
   ./scripts/setup_dev.sh
   ```

2. **Verify Setup**
   ```bash
   ./scripts/verify_setup.sh
   ```

3. **Setup Development Tools**
   ```bash
   ./scripts/setup_tools.sh
   ```

## Development Workflow

### Code Quality

Run these commands before committing:

```bash
# Backend
cd sarkaribot/backend
source venv/bin/activate
black .                    # Format code
flake8 .                   # Lint code
isort .                    # Sort imports
mypy .                     # Type checking
bandit -r apps/            # Security audit

# Frontend
cd sarkaribot/frontend
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
pytest -v tests/unit/      # Run specific test directory

# Frontend tests
cd sarkaribot/frontend
npm test                   # Run Jest tests
npm run test:coverage      # Run with coverage
```

### Running Services

```bash
# Start all services
./scripts/start_backend.sh    # Django development server
./scripts/start_frontend.sh   # React development server

# Or start individually
cd sarkaribot/backend && source venv/bin/activate && python manage.py runserver
cd sarkaribot/frontend && npm start
```

## Code Standards

### Python (Backend)
- Follow PEP 8 with Black formatter (88 character line limit)
- Use type hints for all function parameters and return values
- Comprehensive docstrings for modules, classes, and functions
- Import sorting with isort

### JavaScript/TypeScript (Frontend)
- ESLint with React and TypeScript rules
- Prettier for code formatting
- Functional components with hooks
- PropTypes or TypeScript interfaces for type checking

### Git Workflow
- Feature branches with descriptive names
- Conventional commit messages: `feat:`, `fix:`, `docs:`, etc.
- Pre-commit hooks run linting and formatting
- Pull request reviews required

## IDE Setup

### VS Code
Recommended extensions:
- Python
- Pylance
- Black Formatter
- ES7+ React/Redux/React-Native snippets
- Prettier
- ESLint

### PyCharm
- Configure Black as external tool
- Enable Django support
- Configure pytest as test runner

## Debugging

### Backend
```bash
# Django debug mode
DEBUG=True python manage.py runserver

# Database inspection
python manage.py shell
python manage.py dbshell

# Debug with breakpoints
import pdb; pdb.set_trace()
```

### Frontend
```bash
# React DevTools
# Chrome/Firefox extension for React debugging

# Console debugging
console.log(), console.error(), console.table()

# Source maps enabled in development
```

## Common Issues

### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/development.txt
```

### Database Issues
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
```

### Node.js Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```
EOF

print_status "Development documentation created"

echo ""
echo "🎉 Development Tools Setup Complete!"
echo ""
echo "📋 What's been configured:"
echo "   ✅ Backend: Black, Flake8, isort, mypy, bandit, pytest"
echo "   ✅ Frontend: ESLint, Prettier, TypeScript checking"
echo "   ✅ Git hooks: Pre-commit linting and formatting"
echo "   ✅ Testing framework: pytest with coverage"
echo "   ✅ Documentation: Development guide created"
echo ""
echo "🚀 Next steps:"
echo "   1. Run verification: ./scripts/verify_setup.sh"
echo "   2. Start development: ./scripts/start_backend.sh & ./scripts/start_frontend.sh"
echo "   3. Read docs/DEVELOPMENT.md for detailed workflow"
echo ""
echo "💡 Pro tip: Git hooks will automatically run linting before commits!"