# SarkariBot - Automated Government Job Portal

A sophisticated, fully-automated government job portal that eliminates manual content management through advanced web scraping, NLP-powered SEO automation, and intelligent content lifecycle management.

## 🌟 Features

### Core Functionality
- **Zero-Touch Content Management**: Fully automated job posting discovery and management
- **Multi-Engine Web Scraping**: Scrapy, Playwright, and Requests-based scraping
- **NLP-Powered SEO**: spaCy-driven metadata generation and keyword optimization
- **Finite State Machine**: Automated job lifecycle management (Announced → Admit Card → Answer Key → Result → Archived)
- **Real-Time Updates**: Continuous monitoring and updating of government job portals

### Technical Excellence
- **Headless Architecture**: Decoupled Django REST API backend with React frontend
- **Production-Ready**: Comprehensive error handling, logging, and monitoring
- **Scalable Design**: Built for high-traffic with caching, CDN, and load balancing support
- **SEO Optimized**: Dynamic meta tags, structured data, and sitemap generation

## 🏗️ Architecture

### Backend (Django 4.2+)
- **Core Apps**: Jobs, Sources, Scraping, SEO, Core utilities
- **Database**: PostgreSQL with optimized indexing
- **Task Queue**: Celery with Redis for background processing
- **API**: Django REST Framework with comprehensive filtering and pagination

### Frontend (React 18+)
- **Design**: Pixel-perfect replication of SarkariExam.com
- **Components**: Functional components with hooks
- **Performance**: Lazy loading, code splitting, and optimization
- **SEO**: Dynamic metadata and structured data integration

### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Caching**: Multi-layer Redis caching strategy
- **Monitoring**: Comprehensive logging and error tracking
- **Deployment**: Production-ready with CI/CD pipeline

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sarkaribot
   ```

2. **Backend Setup**
   ```bash
   cd backend
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements/development.txt
   
   # Copy environment file
   cp .env.example .env
   # Edit .env with your configuration
   
   # Run database migrations
   python manage.py migrate
   
   # Create superuser
   python manage.py createsuperuser
   
   # Load initial data
   python manage.py loaddata fixtures/initial_data.json
   
   # Start development server
   python manage.py runserver
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   
   # Install dependencies
   npm install
   
   # Start development server
   npm start
   ```

4. **Start Background Services**
   ```bash
   # Terminal 1: Celery Worker
   cd backend
   celery -A config worker --loglevel=info
   
   # Terminal 2: Celery Beat (Scheduler)
   celery -A config beat --loglevel=info
   ```

### Docker Setup (Recommended)

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up --build

# Access the application
# Backend API: http://localhost:8000
# Frontend: http://localhost:3000
# Admin Panel: http://localhost:8000/admin
```

## 📊 Project Structure

```
sarkaribot/
├── backend/
│   ├── apps/
│   │   ├── jobs/              # Job posting management
│   │   ├── scraping/          # Web scraping engine
│   │   ├── seo/               # SEO automation
│   │   ├── sources/           # Government source management
│   │   └── core/              # Shared utilities
│   ├── config/                # Django configuration
│   ├── requirements/          # Python dependencies
│   └── tests/                 # Test suites
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API services
│   │   └── styles/            # Styling
├── docker/                    # Docker configurations
└── scripts/                   # Deployment scripts
```

## 🎯 Key Components

### Government Source Management
- Configurable scraping for multiple government websites
- JSON-based source configuration system
- Automatic error handling and retry logic
- Performance monitoring and statistics

### Job Lifecycle Management
- Finite State Machine implementation
- Automatic status transitions
- Milestone tracking and history
- Administrative workflow tools

### SEO Automation Engine
- spaCy-powered keyword extraction
- Automatic meta tag generation
- Structured data (schema.org) creation
- Sitemap generation and search engine pinging

### Multi-Engine Scraping
- **Scrapy**: For complex, structured scraping
- **Playwright**: For JavaScript-heavy sites
- **Requests**: For simple, fast scraping
- Automatic engine selection based on site characteristics

## 🔧 Configuration

### Government Sources
Add new government sources via Django admin or API:

```json
{
  "name": "SSC",
  "display_name": "Staff Selection Commission",
  "base_url": "https://ssc.nic.in",
  "scrape_frequency": 6,
  "config_json": {
    "scraper_type": "requests",
    "selectors": {
      "title": "//h2[@class='job-title']/text()",
      "description": "//div[@class='job-desc']",
      "last_date": "//span[@class='last-date']/text()"
    },
    "pagination": {
      "next_page": "//a[@class='next-page']/@href",
      "max_pages": 3
    }
  }
}
```

### Environment Variables
Key configuration options in `.env`:

```bash
# Database
DB_NAME=sarkaribot
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost

# Redis
CACHE_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0

# Scraping
SCRAPING_DEFAULT_DELAY=2
SCRAPING_MAX_RETRIES=3

# SEO
SITE_URL=https://yourdomain.com
GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID
```

## 📈 API Endpoints

### Core API Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/jobs/` | GET | List all jobs with filtering |
| `/api/v1/jobs/{slug}/` | GET | Job detail by slug |
| `/api/v1/categories/` | GET | Job categories |
| `/api/v1/sources/` | GET | Government sources |
| `/api/v1/search/` | GET | Search jobs |

### Admin API Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/scraping/trigger/` | POST | Trigger manual scraping |
| `/api/v1/scraping/status/` | GET | Scraping status |
| `/api/v1/analytics/` | GET | Performance analytics |

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Frontend tests
cd frontend
npm test
```

## 🚀 Deployment

### Production Deployment

1. **Server Setup**
   ```bash
   # Update server
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   ```

2. **Environment Configuration**
   ```bash
   # Copy production environment
   cp .env.example .env.production
   # Update with production values
   ```

3. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### CI/CD Pipeline
GitHub Actions workflow for automated testing and deployment:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Server
        run: |
          # Deployment commands
```

## 📊 Monitoring & Analytics

### Built-in Monitoring
- Comprehensive logging with structured formats
- Error tracking and alerting
- Performance metrics and statistics
- Health check endpoints

### External Integrations
- Sentry for error tracking
- Google Analytics for user behavior
- Custom dashboards for operational metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript
- Write comprehensive tests for new features
- Update documentation for API changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built following the comprehensive specifications in `Knowledge.md`
- Inspired by the design and functionality of SarkariExam.com
- Powered by Django, React, and modern web technologies

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the [documentation](docs/)
- Review the [Knowledge.md](/.github/knowledge.md) for detailed specifications

---

**SarkariBot** - Automating government job discovery for millions of aspirants across India. 🇮🇳
