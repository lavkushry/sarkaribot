# Analytics App for SarkariBot

This app provides comprehensive analytics and reporting functionality for tracking user behavior, system performance, and business metrics.

## Features

- **Page View Tracking**: Track all page visits with user context
- **Job Analytics**: Monitor job posting views and engagement
- **Search Analytics**: Analyze search queries and performance
- **User Session Tracking**: Complete session analytics with device/browser info
- **Conversion Funnel**: Track user journey through the application
- **Performance Monitoring**: System performance metrics and monitoring
- **Real-time Stats**: Live dashboard metrics
- **Daily Statistics**: Automated daily aggregated reports

## Models

### Core Analytics Models
- `PageView`: Individual page view tracking
- `JobView`: Job posting specific views
- `SearchQuery`: Search query tracking with performance metrics
- `UserSession`: Complete user session data
- `ConversionFunnel`: User journey stage tracking
- `AlertEngagement`: Job alert engagement metrics
- `PerformanceMetric`: System performance tracking
- `DailyStats`: Daily aggregated statistics

## Services

### AnalyticsService
Core service for tracking user interactions:
- `track_page_view()`: Track page visits
- `track_job_view()`: Track job posting views
- `track_search_query()`: Track search queries
- `track_conversion()`: Track funnel conversions
- `track_performance_metric()`: Track system metrics

### ReportingService
Generate analytics reports and insights:
- `get_traffic_overview()`: Traffic analytics
- `get_job_analytics()`: Job-related metrics
- `get_search_analytics()`: Search insights
- `get_conversion_funnel()`: Funnel analysis

### DailyStatsService
Automated daily statistics generation:
- `generate_daily_stats()`: Generate daily aggregated data

## API Endpoints

### Analytics Overview (`/api/analytics/overview/`)
- `GET traffic_overview/`: Traffic analytics
- `GET job_analytics/`: Job analytics
- `GET search_analytics/`: Search analytics
- `GET conversion_funnel/`: Conversion funnel
- `GET realtime_stats/`: Real-time statistics
- `GET performance_metrics/`: Performance metrics
- `POST track_event/`: Track custom events

### Daily Statistics (`/api/analytics/daily-stats/`)
- `GET /`: List daily statistics
- `POST generate_stats/`: Generate stats for specific date

### User Sessions (`/api/analytics/sessions/`)
- `GET /`: List user sessions
- `GET device_breakdown/`: Device analytics

## Usage Examples

### Track Page View
```python
from apps.analytics.services import AnalyticsService

# In your view
def my_view(request):
    AnalyticsService.track_page_view(
        request, 
        path='/jobs/',
        page_title='Browse Jobs',
        metadata={'category': 'government'}
    )
    # ... rest of view logic
```

### Track Job View
```python
def job_detail_view(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    
    AnalyticsService.track_job_view(
        request,
        job=job,
        came_from_alert=request.GET.get('from_alert', False),
        search_query=request.GET.get('q', '')
    )
    # ... rest of view logic
```

### Generate Reports
```python
from apps.analytics.services import ReportingService

# Get 30-day traffic overview
traffic_data = ReportingService.get_traffic_overview(days=30)

# Get job analytics
job_data = ReportingService.get_job_analytics(days=7)
```

## Configuration

Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... other apps
    'apps.analytics',
]
```

Add to main `urls.py`:
```python
urlpatterns = [
    # ... other patterns
    path('analytics/', include('apps.analytics.urls')),
]
```

## Permissions

All analytics endpoints require admin permissions (`IsAdminUser`).

## Caching

Analytics reports are cached to improve performance:
- Traffic/Job/Search analytics: 15 minutes
- Real-time stats: 30 minutes
- Performance metrics: 1 hour

## Privacy Considerations

- IP addresses are stored for geolocation but can be anonymized
- User sessions are tracked but personal data is minimal
- GDPR compliance features can be added for data export/deletion
