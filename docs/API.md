# 📚 SarkariBot API Documentation

## Overview

The SarkariBot API provides comprehensive access to government job data, search functionality, and administrative features. Built with Django REST Framework, it offers a robust, scalable, and well-documented interface for all frontend operations.

**Base URL**: `http://localhost:8000/api/v1/` (Development)  
**Production URL**: `https://api.sarkaribot.com/v1/`

## Authentication

### Public Endpoints
Most endpoints are publicly accessible and don't require authentication:
- Job listings and search
- Categories and sources
- Basic statistics

### Admin Endpoints
Administrative operations require token authentication:

```bash
# Login to get token
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}

# Response
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "admin"
}

# Use token in subsequent requests
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Response Format

All API responses follow a consistent structure:

### Success Response
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/v1/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "SSC CHSL 2024",
      "status": "announced",
      "created_at": "2024-08-01T10:30:00Z"
    }
  ]
}
```

### Error Response
```json
{
  "error": "Invalid request",
  "message": "The specified job ID does not exist",
  "code": "JOB_NOT_FOUND",
  "details": {
    "job_id": 999,
    "available_ids": [1, 2, 3, 4, 5]
  }
}
```

## 📄 Jobs API

### List Jobs
Get paginated list of government job postings.

```http
GET /api/v1/jobs/
```

#### Query Parameters
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | string | Filter by job status | `announced`, `admit_card`, `answer_key`, `result` |
| `category` | string | Filter by category slug | `central-government`, `bank-finance` |
| `source` | string | Filter by source name | `SSC`, `UPSC`, `IBPS` |
| `search` | string | Search in title and description | `engineer`, `clerk` |
| `qualification` | string | Filter by qualification | `graduate`, `12th-pass` |
| `posted_after` | date | Jobs posted after date | `2024-08-01` |
| `deadline_before` | date | Application deadline before | `2024-09-15` |
| `min_posts` | integer | Minimum number of posts | `100` |
| `page` | integer | Page number | `1`, `2`, `3` |
| `page_size` | integer | Results per page (max 100) | `20`, `50` |
| `ordering` | string | Sort results | `-created_at`, `application_end_date` |

#### Example Requests

```bash
# Get latest jobs
GET /api/v1/jobs/?status=announced&page_size=20

# Search for engineering jobs
GET /api/v1/jobs/?search=engineer&qualification=graduate

# Get jobs with upcoming deadlines
GET /api/v1/jobs/?deadline_before=2024-08-15&ordering=application_end_date

# Filter by category and source
GET /api/v1/jobs/?category=central-government&source=SSC
```

#### Response
```json
{
  "count": 1247,
  "next": "http://localhost:8000/api/v1/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Staff Selection Commission Combined Higher Secondary Level Examination 2024",
      "slug": "ssc-chsl-2024",
      "status": "announced",
      "source_name": "SSC",
      "category_name": "Central Government",
      "category_slug": "central-government",
      "department": "Staff Selection Commission",
      "total_posts": 4500,
      "qualification": "12th Pass",
      "notification_date": "2024-07-15",
      "application_end_date": "2024-08-15",
      "application_link": "https://ssc.nic.in/apply",
      "days_remaining": 14,
      "is_new": true,
      "created_at": "2024-08-01T06:30:00Z",
      "updated_at": "2024-08-01T10:15:00Z"
    }
  ]
}
```

### Get Job Details
Get detailed information about a specific job posting.

```http
GET /api/v1/jobs/{id}/
```

#### Response
```json
{
  "id": 1,
  "title": "Staff Selection Commission Combined Higher Secondary Level Examination 2024",
  "slug": "ssc-chsl-2024",
  "description": "SSC CHSL 2024 notification for recruitment to various Group C posts...",
  "source": {
    "id": 1,
    "name": "SSC",
    "display_name": "Staff Selection Commission",
    "base_url": "https://ssc.nic.in"
  },
  "category": {
    "id": 1,
    "name": "Central Government",
    "slug": "central-government"
  },
  "status": "announced",
  "department": "Staff Selection Commission",
  "total_posts": 4500,
  "qualification": "12th Pass",
  
  "notification_date": "2024-07-15",
  "application_end_date": "2024-08-15",
  "exam_date": "2024-10-15",
  
  "application_fee": 100.00,
  "salary_min": 19900.00,
  "salary_max": 63200.00,
  
  "min_age": 18,
  "max_age": 27,
  
  "application_link": "https://ssc.nic.in/apply",
  "notification_pdf": "https://ssc.nic.in/chsl2024.pdf",
  "source_url": "https://ssc.nic.in/chsl2024",
  
  "is_featured": true,
  "priority": 5,
  "view_count": 15420,
  "apply_count": 3240,
  
  "seo_metadata": {
    "title": "SSC CHSL 2024 - Apply Online | SarkariBot",
    "description": "Apply for SSC CHSL 2024. Last date: 15 Aug 2024...",
    "keywords": ["ssc", "chsl", "central government", "12th pass"],
    "canonical_url": "https://sarkaribot.com/jobs/ssc-chsl-2024/",
    "structured_data": {...}
  },
  
  "breadcrumbs": [
    {"name": "Home", "url": "/"},
    {"name": "Jobs", "url": "/jobs/"},
    {"name": "Central Government", "url": "/jobs/category/central-government/"},
    {"name": "SSC CHSL 2024", "url": "/jobs/ssc-chsl-2024/"}
  ],
  
  "similar_jobs": [
    {
      "id": 2,
      "title": "SSC CGL 2024",
      "slug": "ssc-cgl-2024",
      "status": "announced"
    }
  ],
  
  "created_at": "2024-08-01T06:30:00Z",
  "updated_at": "2024-08-01T10:15:00Z"
}
```

### Search Jobs
Advanced job search with multiple filters and full-text search.

```http
GET /api/v1/jobs/search/
```

#### Query Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query (title, description, department) |
| `filters` | object | Advanced filter object |
| `location` | string | Job location filter |
| `salary_min` | integer | Minimum salary filter |
| `salary_max` | integer | Maximum salary filter |

#### Example Request
```bash
GET /api/v1/jobs/search/?q=engineer&filters={"status":["announced","admit_card"],"category":["central-government"]}&salary_min=50000
```

### Job Statistics
Get statistics for a specific job.

```http
GET /api/v1/jobs/{id}/stats/
```

#### Response
```json
{
  "job_id": 1,
  "view_count": 15420,
  "apply_count": 3240,
  "share_count": 156,
  "bookmark_count": 892,
  "daily_views": [
    {"date": "2024-08-01", "views": 1240},
    {"date": "2024-07-31", "views": 980}
  ],
  "application_trend": [
    {"date": "2024-08-01", "applications": 124},
    {"date": "2024-07-31", "applications": 98}
  ]
}
```

## 📂 Categories API

### List Categories
Get all job categories with job counts.

```http
GET /api/v1/categories/
```

#### Response
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "Central Government",
      "slug": "central-government",
      "description": "Jobs in central government departments and ministries",
      "position": 1,
      "job_count": 245,
      "latest_jobs_count": 12
    },
    {
      "id": 2,
      "name": "State Government",
      "slug": "state-government",
      "description": "Jobs in state government departments",
      "position": 2,
      "job_count": 156,
      "latest_jobs_count": 8
    }
  ]
}
```

### Get Category Jobs
Get jobs for a specific category.

```http
GET /api/v1/categories/{slug}/jobs/
```

#### Query Parameters
Same as jobs API plus category-specific filters.

#### Example
```bash
GET /api/v1/categories/central-government/jobs/?status=announced&page_size=10
```

## 🏛️ Sources API

### List Sources
Get all government sources with statistics.

```http
GET /api/v1/sources/
```

#### Response
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "SSC",
      "display_name": "Staff Selection Commission",
      "base_url": "https://ssc.nic.in",
      "active": true,
      "last_scraped": "2024-08-01T10:00:00Z",
      "total_jobs_found": 247,
      "stats": {
        "jobs_this_month": 15,
        "success_rate": 98.5,
        "avg_jobs_per_scrape": 3.2,
        "last_successful_scrape": "2024-08-01T10:00:00Z"
      }
    }
  ]
}
```

### Get Source Details
Get detailed information about a specific source.

```http
GET /api/v1/sources/{id}/
```

### Get Source Jobs
Get jobs from a specific source.

```http
GET /api/v1/sources/{id}/jobs/
```

### Source Statistics
Get detailed statistics for a source.

```http
GET /api/v1/sources/{id}/stats/
```

#### Response
```json
{
  "source_id": 1,
  "source_name": "SSC",
  "total_jobs": 247,
  "active_jobs": 45,
  "jobs_this_week": 3,
  "jobs_this_month": 15,
  "scraping_stats": {
    "last_scrape": "2024-08-01T10:00:00Z",
    "success_rate": 98.5,
    "avg_response_time": 2.3,
    "total_scrapes": 156,
    "failed_scrapes": 2
  },
  "monthly_trend": [
    {"month": "2024-08", "jobs": 15},
    {"month": "2024-07", "jobs": 23}
  ]
}
```

## 📊 Statistics API

### Overall Statistics
Get platform-wide statistics.

```http
GET /api/v1/stats/
```

#### Response
```json
{
  "total_jobs": 1247,
  "active_jobs": 456,
  "total_sources": 5,
  "active_sources": 5,
  "jobs_today": 12,
  "jobs_this_week": 45,
  "jobs_this_month": 178,
  "categories": [
    {
      "name": "Central Government",
      "count": 245,
      "percentage": 19.7
    }
  ],
  "top_sources": [
    {
      "name": "SSC",
      "jobs": 247
    }
  ],
  "status_distribution": {
    "announced": 456,
    "admit_card": 234,
    "answer_key": 178,
    "result": 289,
    "archived": 90
  },
  "last_updated": "2024-08-01T10:30:00Z"
}
```

### Trending Jobs
Get currently trending job postings.

```http
GET /api/v1/stats/trending/
```

#### Response
```json
{
  "trending_jobs": [
    {
      "id": 1,
      "title": "SSC CHSL 2024",
      "view_count": 15420,
      "trend_score": 95.6,
      "growth_rate": 23.4
    }
  ],
  "trending_keywords": [
    {"keyword": "engineer", "count": 45},
    {"keyword": "clerk", "count": 34}
  ],
  "trending_categories": [
    {"name": "Central Government", "growth": 15.6},
    {"name": "Banking", "growth": 12.3}
  ]
}
```

### Monthly Statistics
Get monthly job posting statistics.

```http
GET /api/v1/stats/monthly/
```

#### Query Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `year` | integer | Year for statistics (default: current) |
| `months` | integer | Number of months to include (default: 12) |

#### Response
```json
{
  "year": 2024,
  "monthly_data": [
    {
      "month": 8,
      "month_name": "August",
      "jobs_announced": 178,
      "admit_cards": 124,
      "results": 89,
      "total_applications": 45670
    }
  ],
  "yearly_total": 2156,
  "growth_rate": 15.6
}
```

## 🔍 Advanced Search API

### Multi-Filter Search
Perform complex searches with multiple criteria.

```http
POST /api/v1/search/advanced/
Content-Type: application/json
```

#### Request Body
```json
{
  "query": "software engineer",
  "filters": {
    "status": ["announced", "admit_card"],
    "categories": ["central-government", "psu"],
    "sources": ["ISRO", "DRDO"],
    "qualification": ["graduate", "post-graduate"],
    "experience": ["fresher", "1-3 years"],
    "salary_range": {
      "min": 50000,
      "max": 100000
    },
    "age_range": {
      "min": 21,
      "max": 30
    },
    "location": ["Delhi", "Mumbai", "Bangalore"],
    "application_deadline": {
      "from": "2024-08-01",
      "to": "2024-08-31"
    }
  },
  "sort": {
    "field": "application_end_date",
    "order": "asc"
  },
  "page": 1,
  "page_size": 20
}
```

#### Response
Standard paginated job listing with additional search metadata:

```json
{
  "count": 89,
  "next": "...",
  "previous": null,
  "search_metadata": {
    "query": "software engineer",
    "execution_time": 0.045,
    "total_matches": 89,
    "filters_applied": 8,
    "suggestions": ["software developer", "computer engineer"]
  },
  "results": [...]
}
```

### Search Suggestions
Get search suggestions and auto-complete.

```http
GET /api/v1/search/suggestions/?q=softw
```

#### Response
```json
{
  "suggestions": [
    "software engineer",
    "software developer",
    "software analyst"
  ],
  "popular_searches": [
    "ssc",
    "upsc",
    "bank jobs"
  ],
  "recent_searches": [
    "railway jobs",
    "teaching jobs"
  ]
}
```

## 📱 Mobile API

### Mobile-Optimized Endpoints
Optimized endpoints for mobile applications.

```http
GET /api/v1/mobile/jobs/
```

#### Features
- Reduced payload size
- Essential fields only
- Optimized images
- Compressed responses

## 🔔 Notifications API

### Job Alerts
Manage job alert subscriptions.

```http
POST /api/v1/alerts/
Content-Type: application/json
```

#### Request Body
```json
{
  "email": "user@example.com",
  "phone": "+91 9876543210",
  "filters": {
    "categories": ["central-government"],
    "keywords": ["engineer", "analyst"],
    "qualification": ["graduate"],
    "locations": ["Delhi", "Mumbai"]
  },
  "frequency": "daily",
  "active": true
}
```

### Newsletter Subscription
Subscribe to newsletter updates.

```http
POST /api/v1/newsletter/subscribe/
Content-Type: application/json
```

#### Request Body
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "preferences": {
    "job_updates": true,
    "weekly_digest": true,
    "exam_alerts": false
  }
}
```

## 🛠️ Admin API

### Source Management
Manage government sources (requires admin authentication).

```http
POST /api/v1/admin/sources/
Authorization: Token your-admin-token
Content-Type: application/json
```

#### Request Body
```json
{
  "name": "ISRO",
  "display_name": "Indian Space Research Organisation",
  "base_url": "https://isro.gov.in",
  "description": "India's space agency conducting recruitment...",
  "scrape_frequency": 12,
  "active": true,
  "config_json": {
    "selectors": {
      "job_container": ".career-listing",
      "title": ".title",
      "department": ".dept"
    },
    "pagination": {
      "next_page": ".next",
      "max_pages": 5
    }
  }
}
```

### Scraping Control
Control scraping operations.

```http
POST /api/v1/admin/scraping/trigger/
Authorization: Token your-admin-token
Content-Type: application/json
```

#### Request Body
```json
{
  "source_ids": [1, 2, 3],
  "force": false,
  "priority": "high"
}
```

### Content Moderation
Moderate job postings.

```http
PUT /api/v1/admin/jobs/{id}/moderate/
Authorization: Token your-admin-token
Content-Type: application/json
```

#### Request Body
```json
{
  "action": "approve",
  "status": "announced",
  "notes": "Verified and approved for publication",
  "featured": true
}
```

## 📈 Analytics API

### Page Views
Track and get page view analytics.

```http
POST /api/v1/analytics/pageview/
Content-Type: application/json
```

#### Request Body
```json
{
  "page": "/jobs/ssc-chsl-2024/",
  "job_id": 1,
  "referrer": "https://google.com",
  "user_agent": "Mozilla/5.0...",
  "timestamp": "2024-08-01T10:30:00Z"
}
```

### User Behavior
Get user behavior analytics.

```http
GET /api/v1/analytics/behavior/
Authorization: Token your-admin-token
```

#### Response
```json
{
  "popular_pages": [
    {
      "page": "/jobs/ssc-chsl-2024/",
      "views": 15420,
      "unique_visitors": 8970
    }
  ],
  "search_terms": [
    {"term": "ssc", "count": 2340},
    {"term": "bank jobs", "count": 1890}
  ],
  "bounce_rate": 34.5,
  "avg_session_duration": 345,
  "conversion_rate": 12.8
}
```

## ⚠️ Error Handling

### HTTP Status Codes
| Status | Description |
|--------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Server Error |

### Error Response Format
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid request parameters",
  "details": {
    "field": "status",
    "value": "invalid_status",
    "allowed_values": ["announced", "admit_card", "answer_key", "result"]
  },
  "timestamp": "2024-08-01T10:30:00Z",
  "request_id": "req_123456789"
}
```

## 🚦 Rate Limiting

### Limits
- **Anonymous users**: 1000 requests/hour
- **Authenticated users**: 5000 requests/hour
- **Admin users**: 10000 requests/hour

### Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1627814400
```

## 📊 Pagination

### Standard Pagination
```json
{
  "count": 1247,
  "next": "http://localhost:8000/api/v1/jobs/?page=3",
  "previous": "http://localhost:8000/api/v1/jobs/?page=1",
  "results": [...]
}
```

### Cursor Pagination
For real-time data feeds:
```json
{
  "next": "eyJjcmVhdGVkX2F0IjoiMjAyNC0wOC0wMVQxMDozMDowMFoifQ==",
  "previous": null,
  "results": [...]
}
```

## 🔧 API Client Examples

### Python
```python
import requests

class SarkariBotAPI:
    def __init__(self, base_url="http://localhost:8000/api/v1/"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_jobs(self, status=None, category=None, page=1):
        params = {"page": page}
        if status:
            params["status"] = status
        if category:
            params["category"] = category
        
        response = self.session.get(
            f"{self.base_url}jobs/",
            params=params
        )
        return response.json()
    
    def search_jobs(self, query, filters=None):
        data = {"q": query}
        if filters:
            data["filters"] = filters
        
        response = self.session.post(
            f"{self.base_url}search/advanced/",
            json=data
        )
        return response.json()

# Usage
api = SarkariBotAPI()
jobs = api.get_jobs(status="announced", page=1)
search_results = api.search_jobs("engineer", {"category": ["central-government"]})
```

### JavaScript
```javascript
class SarkariBotAPI {
  constructor(baseURL = 'http://localhost:8000/api/v1/') {
    this.baseURL = baseURL;
  }

  async getJobs(options = {}) {
    const params = new URLSearchParams(options);
    const response = await fetch(`${this.baseURL}jobs/?${params}`);
    return response.json();
  }

  async searchJobs(query, filters = {}) {
    const response = await fetch(`${this.baseURL}search/advanced/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, filters }),
    });
    return response.json();
  }

  async getJobDetails(jobId) {
    const response = await fetch(`${this.baseURL}jobs/${jobId}/`);
    return response.json();
  }
}

// Usage
const api = new SarkariBotAPI();
const jobs = await api.getJobs({ status: 'announced', page: 1 });
const searchResults = await api.searchJobs('engineer', { 
  category: ['central-government'] 
});
```

### cURL Examples
```bash
# Get latest jobs
curl "http://localhost:8000/api/v1/jobs/?status=announced&page_size=5"

# Search for engineering jobs
curl -X POST "http://localhost:8000/api/v1/search/advanced/" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "engineer",
       "filters": {
         "categories": ["central-government"],
         "qualification": ["graduate"]
       }
     }'

# Get job details
curl "http://localhost:8000/api/v1/jobs/1/"

# Get statistics
curl "http://localhost:8000/api/v1/stats/"
```

## 📞 Support

For API support and questions:
- **Documentation**: [Full API Docs](https://docs.sarkaribot.com/api/)
- **Support Email**: api-support@sarkaribot.com
- **Discord**: [Join our community](https://discord.gg/sarkaribot)
- **GitHub Issues**: [Report bugs](https://github.com/yourusername/sarkaribot/issues)

---

**API Version**: v1.0  
**Last Updated**: August 1, 2024  
**Documentation Version**: 1.0.0
