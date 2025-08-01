=# .copilot-instructions.md

## 🤖 GitHub Copilot Instructions for SarkariBot

### Primary Context
You are developing **SarkariBot** - a sophisticated, fully-automated government job portal system. This project eliminates manual content management through advanced web scraping, NLP-powered SEO automation, and intelligent content lifecycle management.

**CRITICAL**: Always reference the `Knowledge.md` file in this repository before generating any code. It contains comprehensive architectural specifications, implementation patterns, and project requirements that must be followed exactly.

---

## 🏗️ Architecture Overview

### Core System Design
- **Backend**: Django 4.2+ with DRF, PostgreSQL, Celery + Redis
- **Scraping**: Multi-engine approach (Scrapy + Playwright + Requests)
- **AI/NLP**: spaCy for SEO automation and content analysis
- **Frontend**: React 18+ with functional components
- **Infrastructure**: Docker, AWS, CloudFlare CDN

### Finite State Machine Pattern
Job postings flow through states: `ANNOUNCED` → `ADMIT_CARD` → `ANSWER_KEY` → `RESULT` → `ARCHIVED`

---

## 📁 Project Structure

```
sarkaribot/
├── backend/
│   ├── apps/
│   │   ├── jobs/              # Core job management
│   │   ├── scraping/          # Web scraping engine
│   │   ├── seo/               # SEO automation
│   │   ├── sources/           # Government source management
│   │   └── core/              # Shared utilities
│   ├── config/                # Django settings
│   ├── requirements/          # Dependencies
│   └── tests/                 # Test suites
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API layer
│   │   └── styles/            # Styling
├── docker/                    # Container configs
└── scripts/                   # Deployment scripts
```

---

## 🎯 Code Generation Rules

### 1. Python Code Standards
```python
# ALWAYS include:
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Function template:
def function_name(
    param1: Type,
    param2: Optional[Type] = None
) -> ReturnType:
    """
    Brief description.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description
        
    Raises:
        ExceptionType: When this happens
    """
    try:
        # Implementation
        logger.info(f"Operation started: {operation_name}")
        return result
    except SpecificException as e:
        logger.error(f"Error in {function_name}: {e}")
        raise
```

### 2. Django Model Pattern
```python
# Model template:
class ModelName(models.Model):
    """Model description."""
    
    # Core fields
    field_name = models.CharField(max_length=255)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['field_name']),
        ]
    
    def __str__(self) -> str:
        return self.field_name
```

### 3. React Component Pattern
```jsx
// Component template:
import React from 'react';
import PropTypes from 'prop-types';

const ComponentName = ({ prop1, prop2 }) => {
  // Component logic
  
  return (
    <div className="component-name">
      {/* JSX content */}
    </div>
  );
};

ComponentName.propTypes = {
  prop1: PropTypes.string.required,
  prop2: PropTypes.number
};

export default ComponentName;
```

---

## 🗄️ Database Schema (Key Models)

### Government Sources
```python
# Store configuration for each government website
class GovernmentSource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_url = models.URLField()
    active = models.BooleanField(default=True)
    scrape_frequency = models.IntegerField(default=24)  # hours
    config_json = models.JSONField()  # Scraping configuration
    last_scraped = models.DateTimeField(null=True, blank=True)
```

### Job Postings (Core Entity)
```python
class JobPosting(models.Model):
    STATUS_CHOICES = [
        ('announced', 'Latest Job'),
        ('admit_card', 'Admit Card'),
        ('answer_key', 'Answer Key'),
        ('result', 'Result'),
        ('archived', 'Archived'),
    ]
    
    # Core fields
    title = models.CharField(max_length=255)
    description = models.TextField()
    source = models.ForeignKey(GovernmentSource, on_delete=models.CASCADE)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # SEO fields
    slug = models.SlugField(max_length=255, unique=True)
    seo_title = models.CharField(max_length=255)
    seo_description = models.TextField()
    keywords = models.TextField()
    structured_data = models.JSONField()
    
    # Indexes for performance
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['slug']),
        ]
```

---

## 🕷️ Web Scraping Implementation

### Source Configuration System
```python
# Government source configuration example
GOVERNMENT_SOURCES = {
    'SSC': {
        'base_url': 'https://ssc.nic.in',
        'scrape_frequency': 6,  # hours
        'selectors': {
            'title': '//h2[@class="job-title"]/text()',
            'description': '//div[@class="job-desc"]',
            'last_date': '//span[@class="last-date"]/text()',
        },
        'pagination': {
            'next_page': '//a[@class="next-page"]/@href',
            'max_pages': 3
        }
    }
}
```

### Multi-Engine Scraping
```python
# Scraper selection logic
def get_scraper(source_config: Dict) -> BaseScraper:
    """Select appropriate scraper based on site characteristics."""
    if source_config.get('requires_js'):
        return PlaywrightScraper(source_config)
    elif source_config.get('complex_structure'):
        return ScrapyScraper(source_config)
    else:
        return RequestsScraper(source_config)
```

---

## 🎨 SEO Automation System

### NLP-Powered Metadata Generation
```python
import spacy

nlp = spacy.load("en_core_web_sm")

def generate_seo_metadata(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate SEO-optimized metadata using NLP."""
    
    # Extract keywords using spaCy
    doc = nlp(job_data['title'] + " " + job_data.get('description', ''))
    keywords = [chunk.text.lower() for chunk in doc.noun_chunks 
                if len(chunk.text) > 3][:7]
    
    # Generate SEO title (50-60 chars)
    current_year = datetime.now().year
    seo_title = f"{job_data['title']} {current_year} - Apply Online | SarkariBot"
    
    # Generate meta description (150-160 chars)
    last_date = job_data.get('last_date', 'TBD')
    seo_description = (
        f"Apply for {job_data['title']}. Last date: {last_date}. "
        f"Eligibility, syllabus, and direct apply link. {current_year} government job."
    )
    
    return {
        'seo_title': seo_title[:60],
        'seo_description': seo_description[:160],
        'keywords': keywords,
        'structured_data': generate_job_schema(job_data)
    }
```

---

## 🎭 Frontend Design Requirements

### SarkariExam.com Replication
The frontend must exactly replicate the design of SarkariExam.com with these sections:

```jsx
// Homepage layout structure
const HomePage = () => (
  <div className="page-container">
    <Header />
    <main className="content-grid">
      <section className="main-content">
        <CategorySection category="Latest Jobs" />
        <CategorySection category="Admit Card" />
        <CategorySection category="Answer Key" />
        <CategorySection category="Result" />
      </section>
      <aside className="sidebar">
        <PopularJobs />
        <QuickLinks />
      </aside>
    </main>
    <Footer />
  </div>
);
```

### Component Patterns
```jsx
// Job listing component
const JobCard = ({ job }) => (
  <div className="job-card">
    <h3 className="job-title">
      <Link to={`/jobs/${job.slug}`}>{job.title}</Link>
    </h3>
    <div className="job-meta">
      <span className="source">{job.source.name}</span>
      <span className="date">{formatDate(job.last_date)}</span>
    </div>
  </div>
);
```

---

## 🔄 Background Tasks (Celery)

### Task Patterns
```python
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def scrape_government_source(self, source_id: int) -> Dict[str, Any]:
    """Scrape a specific government source for job postings."""
    try:
        source = GovernmentSource.objects.get(id=source_id)
        scraper = get_scraper(source.config_json)
        
        logger.info(f"Starting scrape for {source.name}")
        jobs_data = scraper.scrape()
        
        # Process and save jobs
        created_count = 0
        updated_count = 0
        
        for job_data in jobs_data:
            job, created = process_job_data(job_data, source)
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        return {
            'source': source.name,
            'jobs_found': len(jobs_data),
            'created': created_count,
            'updated': updated_count
        }
        
    except Exception as exc:
        logger.error(f"Scraping failed for source {source_id}: {exc}")
        raise self.retry(countdown=60 * (self.request.retries + 1))
```

---

## 🌐 API Design Patterns

### DRF ViewSet Pattern
```python
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

class JobPostingViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for job postings."""
    
    queryset = JobPosting.objects.filter(status__in=['announced', 'admit_card', 'answer_key', 'result'])
    serializer_class = JobPostingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'last_date']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Apply additional filtering based on query parameters."""
        queryset = super().get_queryset()
        
        # Category-based filtering
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
            
        return queryset.select_related('source', 'category')
```

---

## 🧪 Testing Patterns

### Unit Test Template
```python
import pytest
from django.test import TestCase
from unittest.mock import patch, MagicMock

class TestJobPosting(TestCase):
    """Test job posting functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.source = GovernmentSource.objects.create(
            name='Test Source',
            base_url='https://test.gov.in'
        )
        
    def test_job_creation(self):
        """Test job posting creation."""
        job = JobPosting.objects.create(
            title='Test Job 2025',
            source=self.source,
            status='announced'
        )
        
        self.assertEqual(job.slug, 'test-job-2025')
        self.assertIn('2025', job.seo_title)
```

---

## 🎯 Common Implementation Requests

### When I ask for:

#### "Create Django models"
- Follow the exact schema from Knowledge.md
- Include all indexes and relationships
- Add proper Meta classes and string representations
- Include validation and custom methods

#### "Build scraping functionality"
- Use the multi-engine approach (Scrapy/Playwright/Requests)
- Implement source configuration system
- Add comprehensive error handling and retry logic
- Include duplicate detection and change tracking

#### "Add SEO automation"
- Implement spaCy-based NLP pipeline
- Generate metadata using the specified patterns
- Create structured data (schema.org JobPosting)
- Add sitemap generation and search engine pinging

#### "Create React components"
- Match SarkariExam.com design exactly
- Use functional components with hooks
- Include PropTypes for type checking
- Implement responsive design
- Add proper error boundaries and loading states

#### "Set up API endpoints"
- Use DRF viewsets with proper filtering
- Include pagination and search functionality
- Add comprehensive serializers
- Implement proper error handling and validation

---

## 🚀 Performance Requirements

### Database Optimization
- Always use select_related/prefetch_related for foreign keys
- Add database indexes for all frequently queried fields
- Use bulk operations for multiple database writes
- Implement proper caching with appropriate TTL values

### Frontend Performance
- Implement lazy loading for images and components
- Use React.memo for expensive components
- Add code splitting for different routes
- Implement service worker for caching

---

## 🔒 Security Implementation

### Always Include:
- Input validation and sanitization
- Rate limiting on API endpoints
- Proper CORS configuration
- SQL injection prevention through ORM
- XSS protection for rendered content
- Comprehensive logging for security events

---

## 📊 Monitoring and Logging

### Logging Pattern
```python
import logging

logger = logging.getLogger(__name__)

# Use throughout the codebase:
logger.info("Operation started")
logger.debug("Processing details")
logger.warning("Potential issue detected")
logger.error("Error occurred", exc_info=True)
logger.critical("System critical error")
```

---

## ✅ Quality Checklist

Before completing any implementation, ensure:
- [ ] Follows Knowledge.md specifications exactly
- [ ] Includes comprehensive error handling
- [ ] Has proper type hints and docstrings
- [ ] Includes relevant tests
- [ ] Implements proper logging
- [ ] Follows security best practices
- [ ] Optimized for performance
- [ ] Includes proper validation
- [ ] Has clean, readable code
- [ ] Follows project structure conventions

---

## 🎯 Success Criteria

Your code is successful when it:
- ✅ Perfectly aligns with Knowledge.md specifications
- ✅ Is production-ready with proper error handling
- ✅ Includes comprehensive logging and monitoring
- ✅ Follows all coding standards and best practices
- ✅ Is properly tested and documented
- ✅ Integrates seamlessly with other components
- ✅ Is optimized for performance and scalability

**Remember**: Every implementation should be enterprise-grade, production-ready code that can operate 24/7 with minimal human intervention.