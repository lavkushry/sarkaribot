# 🤝 Contributing to SarkariBot

Welcome to SarkariBot! We're excited that you're interested in contributing to our automated government job portal. This guide will help you get started with contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## 📜 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
Examples of behavior that contributes to creating a positive environment include:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

### Enforcement
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at conduct@sarkaribot.com.

## 🚀 Getting Started

### Prerequisites
Before you begin, ensure you have the following installed:
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 14+** (or SQLite for development)
- **Redis 6+**
- **Git**
- **Docker** (optional but recommended)

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
```bash
git clone https://github.com/YOUR_USERNAME/sarkaribot.git
cd sarkaribot
```

3. **Add the upstream remote**:
```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/sarkaribot.git
```

## 🛠️ Development Setup

### Option 1: Docker Setup (Recommended)

1. **Start the development environment**:
```bash
docker-compose up -d
```

2. **Run migrations**:
```bash
docker-compose exec backend python manage.py migrate
```

3. **Create a superuser**:
```bash
docker-compose exec backend python manage.py createsuperuser
```

4. **Load sample data**:
```bash
docker-compose exec backend python manage.py loaddata fixtures/sample_data.json
```

### Option 2: Manual Setup

#### Backend Setup

1. **Create virtual environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements/development.txt
```

3. **Setup environment variables**:
```bash
cp .env.example .env
# Edit .env with your local settings
```

4. **Run migrations**:
```bash
python manage.py migrate
```

5. **Create superuser**:
```bash
python manage.py createsuperuser
```

6. **Start the development server**:
```bash
python manage.py runserver
```

#### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Start the development server**:
```bash
npm start
```

### Verify Setup

Visit the following URLs to verify your setup:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1/
- **Admin Interface**: http://localhost:8000/admin/

## 🤝 How to Contribute

### 1. Find an Issue

- Browse our [GitHub Issues](https://github.com/yourusername/sarkaribot/issues)
- Look for issues labeled `good first issue` or `help wanted`
- Check our [Project Board](https://github.com/yourusername/sarkaribot/projects) for planned work

### 2. Create a Branch

```bash
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name
```

### Branch Naming Convention
- **Feature**: `feature/job-search-enhancement`
- **Bug Fix**: `bugfix/api-response-error`
- **Documentation**: `docs/update-contributing-guide`
- **Refactor**: `refactor/user-service-cleanup`

### 3. Make Changes

- Write clean, readable code
- Follow our [Code Standards](#code-standards)
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test

# Integration tests
npm run test:e2e
```

### 5. Commit Your Changes

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```bash
git add .
git commit -m "feat(jobs): add advanced search filters

- Add qualification filter
- Add salary range filter
- Add location-based search
- Update API documentation

Closes #123"
```

#### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 📝 Code Standards

### Python (Backend)

#### Style Guide
We follow [PEP 8](https://pep8.org/) with the following tools:
- **Formatter**: `black`
- **Linter**: `flake8`
- **Import sorter**: `isort`
- **Type checker**: `mypy`

#### Code Formatting
```bash
# Format code
black backend/

# Sort imports
isort backend/

# Check linting
flake8 backend/

# Type checking
mypy backend/
```

#### Best Practices

```python
# Good: Clear function names and docstrings
def get_active_job_postings(category_id: Optional[int] = None) -> QuerySet[JobPosting]:
    """
    Retrieve active job postings, optionally filtered by category.
    
    Args:
        category_id: Optional category ID to filter jobs
        
    Returns:
        QuerySet of active JobPosting objects
    """
    queryset = JobPosting.objects.filter(status='announced')
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    return queryset

# Good: Use type hints
from typing import Optional, List, Dict, Any

def process_scraped_data(
    raw_data: List[Dict[str, Any]], 
    source_id: int
) -> List[JobPosting]:
    """Process scraped job data and return JobPosting objects."""
    pass

# Good: Use constants for magic strings
class JobStatus:
    ANNOUNCED = 'announced'
    ADMIT_CARD = 'admit_card'
    ANSWER_KEY = 'answer_key'
    RESULT = 'result'
    ARCHIVED = 'archived'
```

### JavaScript/TypeScript (Frontend)

#### Style Guide
We use ESLint and Prettier with these configurations:

```json
// .eslintrc.json
{
  "extends": [
    "react-app",
    "react-app/jest",
    "@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

#### Best Practices

```typescript
// Good: Use TypeScript interfaces
interface JobPosting {
  id: number;
  title: string;
  status: JobStatus;
  category: Category;
  source: Source;
  createdAt: string;
}

// Good: Use React functional components with hooks
const JobCard: React.FC<{ job: JobPosting }> = ({ job }) => {
  const [isBookmarked, setIsBookmarked] = useState(false);
  
  const handleBookmark = useCallback(() => {
    setIsBookmarked(!isBookmarked);
  }, [isBookmarked]);
  
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">{job.title}</Typography>
        <Button onClick={handleBookmark}>
          {isBookmarked ? 'Remove Bookmark' : 'Bookmark'}
        </Button>
      </CardContent>
    </Card>
  );
};

// Good: Use custom hooks for business logic
const useJobSearch = () => {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [loading, setLoading] = useState(false);
  
  const searchJobs = useCallback(async (query: string) => {
    setLoading(true);
    try {
      const response = await api.searchJobs(query);
      setJobs(response.data.results);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  }, []);
  
  return { jobs, loading, searchJobs };
};
```

### Database Migrations

```python
# Good: Descriptive migration names
class Migration(migrations.Migration):
    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobposting',
            name='application_fee',
            field=models.DecimalField(
                max_digits=10, 
                decimal_places=2, 
                null=True, 
                blank=True,
                help_text="Application fee in INR"
            ),
        ),
    ]
```

## 🧪 Testing Guidelines

### Backend Testing

#### Test Structure
```
backend/tests/
├── unit/                 # Unit tests for individual functions
├── integration/          # Integration tests for APIs
├── fixtures/             # Test data fixtures
└── factories.py          # Factory classes for test objects
```

#### Writing Tests
```python
# tests/test_job_service.py
import pytest
from django.test import TestCase
from factories import JobPostingFactory, CategoryFactory
from apps.jobs.services import JobService

class TestJobService(TestCase):
    def setUp(self):
        self.category = CategoryFactory(name="Central Government")
        self.job_service = JobService()
    
    def test_create_job_posting_success(self):
        """Test successful job posting creation."""
        job_data = {
            'title': 'Software Engineer',
            'category': self.category,
            'status': 'announced'
        }
        job = self.job_service.create_job_posting(job_data)
        
        self.assertEqual(job.title, 'Software Engineer')
        self.assertEqual(job.category, self.category)
        self.assertTrue(job.slug)
    
    def test_create_job_posting_duplicate_title(self):
        """Test handling of duplicate job titles."""
        JobPostingFactory(title="Existing Job")
        
        with pytest.raises(ValidationError):
            self.job_service.create_job_posting({
                'title': 'Existing Job',
                'category': self.category
            })
```

#### API Testing
```python
# tests/test_job_api.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from factories import JobPostingFactory

User = get_user_model()

class TestJobAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.job = JobPostingFactory()
    
    def test_get_job_list(self):
        """Test job listing endpoint."""
        response = self.client.get('/api/v1/jobs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.job.id)
    
    def test_get_job_detail(self):
        """Test job detail endpoint."""
        response = self.client.get(f'/api/v1/jobs/{self.job.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.job.title)
```

### Frontend Testing

#### Component Testing
```typescript
// src/components/__tests__/JobCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { JobCard } from '../JobCard';
import { mockJob } from '../../__mocks__/jobData';

describe('JobCard', () => {
  it('renders job information correctly', () => {
    render(<JobCard job={mockJob} />);
    
    expect(screen.getByText(mockJob.title)).toBeInTheDocument();
    expect(screen.getByText(mockJob.category.name)).toBeInTheDocument();
    expect(screen.getByText('Bookmark')).toBeInTheDocument();
  });
  
  it('handles bookmark toggle', () => {
    const onBookmark = jest.fn();
    render(<JobCard job={mockJob} onBookmark={onBookmark} />);
    
    fireEvent.click(screen.getByText('Bookmark'));
    
    expect(onBookmark).toHaveBeenCalledWith(mockJob.id);
  });
});
```

#### Integration Testing
```typescript
// src/pages/__tests__/JobSearch.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { JobSearch } from '../JobSearch';
import { store } from '../../store';
import { mockApiResponse } from '../../__mocks__/api';

// Mock API
jest.mock('../../services/api');

describe('JobSearch Page', () => {
  it('displays search results', async () => {
    render(
      <Provider store={store}>
        <JobSearch />
      </Provider>
    );
    
    await waitFor(() => {
      expect(screen.getByText('Search Results')).toBeInTheDocument();
      expect(screen.getByText(mockApiResponse.results[0].title)).toBeInTheDocument();
    });
  });
});
```

### Test Coverage

Maintain minimum test coverage:
- **Backend**: 85% overall coverage
- **Frontend**: 80% overall coverage
- **Critical paths**: 95% coverage

```bash
# Check backend coverage
cd backend
pytest --cov=apps --cov-report=html

# Check frontend coverage
cd frontend
npm run test:coverage
```

## 📤 Pull Request Process

### PR Checklist

Before submitting a pull request, ensure:

- [ ] Code follows the project style guidelines
- [ ] Tests pass locally (`npm test` and `pytest`)
- [ ] New tests added for new functionality
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow conventional format
- [ ] PR description clearly explains the changes
- [ ] Related issues are referenced
- [ ] Screenshots included for UI changes

### PR Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Related Issues
Fixes #(issue number)

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for UI changes.

## Deployment Notes
Any special deployment considerations.
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and checks
2. **Code Review**: At least one maintainer reviews the code
3. **Testing**: Reviewer tests the changes locally
4. **Approval**: PR is approved and merged

### Review Criteria

Reviewers will check for:
- **Functionality**: Does the code work as intended?
- **Code Quality**: Is the code clean and maintainable?
- **Performance**: Are there any performance implications?
- **Security**: Are there any security concerns?
- **Documentation**: Is the code well-documented?

## 🐛 Issue Guidelines

### Bug Reports

Use the bug report template:

```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g. Ubuntu 20.04]
- Browser: [e.g. Chrome 91]
- Version: [e.g. v1.0.0]

**Additional Context**
Any other context about the problem.
```

### Feature Requests

Use the feature request template:

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Describe the use case and why this feature would be valuable.

**Proposed Solution**
If you have ideas for implementation, describe them here.

**Alternatives Considered**
Describe any alternative solutions you've considered.

**Additional Context**
Any other context about the feature request.
```

## 📚 Documentation

### Types of Documentation

1. **Code Documentation**: Inline comments and docstrings
2. **API Documentation**: OpenAPI/Swagger specs
3. **User Documentation**: End-user guides
4. **Developer Documentation**: Setup and contributing guides

### Writing Guidelines

- Use clear, concise language
- Include code examples
- Keep documentation up-to-date with code changes
- Use proper markdown formatting

### Documentation Structure

```
docs/
├── README.md              # Project overview
├── CONTRIBUTING.md        # This file
├── API.md                # API documentation
├── DEPLOYMENT.md         # Deployment guide
├── ARCHITECTURE.md       # System architecture
├── user-guide/           # End-user documentation
├── developer-guide/      # Developer documentation
└── api/                  # Generated API docs
```

## 🎯 Development Workflow

### Feature Development

1. **Planning Phase**
   - Create or pick an issue
   - Discuss approach in issue comments
   - Break down into smaller tasks

2. **Development Phase**
   - Create feature branch
   - Implement changes incrementally
   - Write tests as you go
   - Update documentation

3. **Review Phase**
   - Self-review your changes
   - Create pull request
   - Address review feedback
   - Ensure CI passes

4. **Deployment Phase**
   - Merge to main branch
   - Deploy to staging
   - Test in staging environment
   - Deploy to production

### Release Process

1. **Version Bumping**
   - Follow [Semantic Versioning](https://semver.org/)
   - Update version in package.json and setup.py

2. **Changelog**
   - Update CHANGELOG.md
   - Include all changes since last release

3. **Testing**
   - Run full test suite
   - Manual testing of critical paths

4. **Deployment**
   - Create release branch
   - Deploy to production
   - Tag release in git

## 🏷️ Labeling System

### Issue Labels

- **Type Labels**
  - `bug`: Something isn't working
  - `enhancement`: New feature or request
  - `documentation`: Improvements to documentation
  - `question`: Further information is requested

- **Priority Labels**
  - `priority-high`: High priority
  - `priority-medium`: Medium priority
  - `priority-low`: Low priority

- **Status Labels**
  - `status-pending`: Waiting for more information
  - `status-in-progress`: Currently being worked on
  - `status-ready`: Ready for development

- **Difficulty Labels**
  - `good-first-issue`: Good for newcomers
  - `help-wanted`: Extra attention is needed
  - `advanced`: Requires advanced knowledge

## 🌟 Recognition

### Contributors

We recognize contributors in several ways:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Annual contributor appreciation post
- Swag for significant contributions

### Hall of Fame

Outstanding contributors may be invited to join our Hall of Fame:
- Special recognition on website
- Direct communication channel with maintainers
- Input on project direction
- Mentorship opportunities

## 📞 Getting Help

### Communication Channels

- **GitHub Discussions**: For general questions and discussions
- **Discord**: Real-time chat with the community
- **Email**: contact@sarkaribot.com for private matters
- **Twitter**: @SarkariBot for updates and announcements

### Office Hours

Join our weekly office hours:
- **When**: Every Friday, 3:00 PM IST
- **Where**: Discord voice channel
- **What**: Q&A, discussions, pair programming

### Mentorship Program

New contributors can join our mentorship program:
- Paired with experienced contributor
- Guidance on first contributions
- Regular check-ins and support

## 🔄 Continuous Improvement

### Feedback

We continuously improve our contribution process:
- Regular surveys for contributors
- Retrospectives after major releases
- Open discussions about process improvements

### Process Updates

This contributing guide is updated regularly:
- Based on contributor feedback
- As project evolves
- To reflect best practices

## 📜 License

By contributing to SarkariBot, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Thank you for contributing to SarkariBot! Your efforts help make government job information more accessible to millions of job seekers across India. 🇮🇳

**Questions?** Don't hesitate to ask in our [GitHub Discussions](https://github.com/yourusername/sarkaribot/discussions) or join our [Discord community](https://discord.gg/sarkaribot).

---

**Contributing Guide Version**: 1.0  
**Last Updated**: August 1, 2024  
**Next Review**: November 1, 2024
