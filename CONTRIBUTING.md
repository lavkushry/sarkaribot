# Contributing to SarkariBot

Thank you for your interest in contributing to SarkariBot! This document provides guidelines and information for contributors.

## 🌟 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](../.github/CODE_OF_CONDUCT.md). Please read it before contributing.

## 🚀 Getting Started

### Prerequisites

Before you begin contributing, make sure you have:

- **Python 3.12+** installed
- **Node.js 18+** installed
- **PostgreSQL 14+** (for database testing)
- **Redis 6+** (for caching and Celery)
- **Git** for version control

### Setting Up Development Environment

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/sarkaribot.git
   cd sarkaribot
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements/dev.txt
   
   # Copy environment file and configure
   cp .env.example .env
   # Edit .env with your local settings
   
   # Run migrations
   python manage.py migrate
   python manage.py createsuperuser
   python create_sample_data.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Start Development Servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python manage.py runserver
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   
   # Terminal 3 - Celery (optional for scraping)
   cd backend
   celery -A config worker -l info
   ```

## 🔄 Development Workflow

### Branch Strategy

We use a simplified Git flow:

- **`main`**: Production-ready code
- **`develop`**: Integration branch for features
- **`feature/feature-name`**: Feature development
- **`bugfix/bug-description`**: Bug fixes
- **`hotfix/critical-fix`**: Critical production fixes

### Making Changes

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

2. **Make Your Changes**
   - Write clean, readable code
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   python manage.py test
   
   # Frontend tests
   cd frontend
   npm test
   
   # Run linting
   cd backend
   flake8 .
   black . --check
   
   cd frontend
   npm run lint
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

5. **Push and Create Pull Request**
   ```bash
   git push origin feature/amazing-new-feature
   # Create PR on GitHub
   ```

## 📝 Commit Message Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear commit history:

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples
```bash
feat(jobs): add job search functionality
fix(scraping): handle timeout errors gracefully
docs(api): update endpoint documentation
test(jobs): add unit tests for job filtering
```

## 🧪 Testing Guidelines

### Backend Testing

We use Django's built-in testing framework with additional tools:

```python
# tests/test_jobs.py
from django.test import TestCase
from django.urls import reverse
from apps.jobs.models import JobPosting

class JobAPITestCase(TestCase):
    def setUp(self):
        self.job = JobPosting.objects.create(
            title="Test Job 2025",
            status="announced"
        )
    
    def test_job_list_api(self):
        """Test job listing API endpoint."""
        url = reverse('jobposting-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Job 2025")
    
    def test_job_search(self):
        """Test job search functionality."""
        url = reverse('jobposting-list')
        response = self.client.get(url, {'search': 'Test'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 1)
```

### Frontend Testing

We use Jest and React Testing Library:

```typescript
// src/components/__tests__/JobCard.test.tsx
import { render, screen } from '@testing-library/react';
import { JobCard } from '../JobCard';

const mockJob = {
  id: 1,
  title: 'Test Job 2025',
  status: 'announced',
  source_name: 'Test Commission',
  total_posts: 100,
  application_end_date: '2025-12-31',
  days_remaining: 30
};

describe('JobCard', () => {
  test('renders job information correctly', () => {
    render(<JobCard job={mockJob} />);
    
    expect(screen.getByText('Test Job 2025')).toBeInTheDocument();
    expect(screen.getByText('Test Commission')).toBeInTheDocument();
    expect(screen.getByText('100 Posts')).toBeInTheDocument();
  });
  
  test('shows correct status badge', () => {
    render(<JobCard job={mockJob} />);
    
    expect(screen.getByText('Latest Job')).toBeInTheDocument();
  });
});
```

### Integration Testing

Test API endpoints with real data:

```python
# tests/test_integration.py
from django.test import TransactionTestCase
from django.test.utils import override_settings
from apps.scraping.tasks import scrape_source

@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class ScrapingIntegrationTest(TransactionTestCase):
    def test_full_scraping_workflow(self):
        """Test complete scraping workflow."""
        # Create test source
        source = GovernmentSource.objects.create(
            name="Test Source",
            base_url="https://example.gov.in"
        )
        
        # Run scraping task
        result = scrape_source.delay(source.id)
        
        # Verify results
        self.assertTrue(result.successful())
        self.assertTrue(JobPosting.objects.filter(source=source).exists())
```

## 🎨 Code Style Guidelines

### Python Style

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Imports**: Use isort for import sorting
- **Formatting**: Use Black for code formatting
- **Type hints**: Use type hints for function parameters and returns

```python
from typing import List, Optional, Dict, Any
from django.db import models

def process_job_data(
    job_data: Dict[str, Any], 
    source: models.Model
) -> Optional[JobPosting]:
    """
    Process scraped job data and create JobPosting instance.
    
    Args:
        job_data: Raw job data from scraper
        source: Government source instance
        
    Returns:
        Created JobPosting instance or None if invalid
        
    Raises:
        ValidationError: If job data is invalid
    """
    if not job_data.get('title'):
        return None
        
    job = JobPosting.objects.create(
        title=job_data['title'],
        source=source,
        status='announced'
    )
    
    return job
```

### TypeScript Style

We use ESLint with TypeScript support:

```typescript
// Use interfaces for type definitions
interface JobPostingData {
  id: number;
  title: string;
  status: JobStatus;
  source_name: string;
  total_posts: number;
  application_end_date: string;
  days_remaining: number;
}

// Use descriptive function names and type annotations
const fetchJobPostings = async (
  filters: JobFilters = {}
): Promise<PaginatedResponse<JobPostingData>> => {
  try {
    const response = await api.get('/jobs/', { params: filters });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch job postings:', error);
    throw new Error('Unable to load job postings');
  }
};

// Use React functional components with proper typing
const JobCard: React.FC<JobCardProps> = ({ job, onApply }) => {
  const handleApplyClick = useCallback(() => {
    onApply?.(job.id);
  }, [job.id, onApply]);

  return (
    <div className="job-card">
      <h3>{job.title}</h3>
      <p>{job.source_name}</p>
      <button onClick={handleApplyClick}>
        Apply Now
      </button>
    </div>
  );
};
```

### Django Best Practices

- Use class-based views for complex logic
- Implement proper serializers for API endpoints
- Use select_related/prefetch_related for database optimization
- Add proper indexes to models
- Use Django's built-in validators

```python
# models.py
class JobPosting(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='announced',
        db_index=True
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['source', 'status']),
        ]

# serializers.py
class JobPostingSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'slug', 'status', 'source_name', 
            'category_name', 'total_posts', 'days_remaining'
        ]
    
    def get_days_remaining(self, obj):
        if obj.application_end_date:
            delta = obj.application_end_date - timezone.now().date()
            return max(0, delta.days)
        return None

# views.py
class JobPostingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = JobPostingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'source', 'category']
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        return JobPosting.objects.select_related(
            'source', 'category'
        ).filter(
            status__in=['announced', 'admit_card', 'answer_key', 'result']
        )
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment details**:
   - OS and version
   - Python version
   - Node.js version
   - Browser (for frontend issues)

2. **Steps to reproduce**:
   - Clear, numbered steps
   - Expected vs actual behavior
   - Screenshots if applicable

3. **Additional context**:
   - Error logs/stack traces
   - Relevant configuration
   - Related issues

### Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python: [e.g. 3.12.0]
- Node.js: [e.g. 18.17.0]
- Browser: [e.g. Chrome 91.0]

**Additional Context**
Add any other context about the problem.
```

## 💡 Feature Requests

We welcome feature suggestions! Please:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** you're trying to solve
3. **Propose a solution** with implementation details
4. **Consider alternatives** and explain why your solution is best

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Implementation Details**
Technical details about how this could be implemented.

**Additional Context**
Screenshots, mockups, or other context.
```

## 🏗️ Architecture Guidelines

### Backend Architecture

- **Apps structure**: One app per major functionality
- **Models**: Keep models focused and use proper relationships
- **Views**: Use DRF viewsets for API endpoints
- **Tasks**: Use Celery for background processing
- **Services**: Extract complex business logic to service classes

### Frontend Architecture

- **Components**: Small, reusable, single-purpose components
- **Pages**: Top-level page components
- **Hooks**: Custom hooks for shared logic
- **Services**: API interaction layer
- **Types**: TypeScript interfaces for data structures

### Database Guidelines

- Use proper indexes for query optimization
- Implement database constraints
- Use migrations for schema changes
- Consider read replicas for scaling

## 📚 Documentation

### Code Documentation

- **Python**: Use Google-style docstrings
- **TypeScript**: Use JSDoc comments for complex functions
- **API**: Document all endpoints with DRF schema

### User Documentation

- Keep documentation up-to-date with code changes
- Include examples and code snippets
- Use clear, concise language
- Add screenshots for UI changes

## 🚢 Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1.  Update version numbers
2.  Update CHANGELOG.md
3.  Run full test suite
4.  Update documentation
5.  Create release PR
6.  Tag release after merge
7.  Deploy to staging
8.  Deploy to production

## 🙋 Getting Help

If you need help with contribution:

1.  **Check documentation** in the `docs/` folder
2.  **Search existing issues** for similar questions
3.  **Join discussions** on GitHub Discussions
4.  **Ask questions** in new issues with the "question" label

## 🎉 Recognition

Contributors are recognized in:

- README.md contributors section
- Release notes for significant contributions
- Special mentions for outstanding contributions

Thank you for contributing to SarkariBot! 🚀

---

**Happy coding!** 💻
