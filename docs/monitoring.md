# Error Tracking and Monitoring Documentation

## Overview

This document describes the comprehensive error tracking and monitoring system implemented for SarkariBot. The system provides both backend and frontend monitoring capabilities to ensure system reliability and quick issue resolution.

## Backend Monitoring

### Components

#### 1. Monitoring App (`apps/monitoring/`)
- **Models**: Track system health, errors, performance metrics, and user feedback
- **Views**: API endpoints for health checks and status reporting
- **Middleware**: Request tracking, rate limiting, and security headers
- **Tasks**: Automated monitoring and cleanup tasks

#### 2. Sentry Integration
- Automatic error capture and reporting
- Performance monitoring with configurable sampling
- User feedback collection
- Environment-specific configuration

#### 3. Custom Middleware
- `RequestTrackingMiddleware`: Tracks response times and database queries
- `RateLimitMiddleware`: Basic rate limiting for API endpoints
- `SecurityHeadersMiddleware`: Adds security headers to responses
- `HealthCheckMiddleware`: Fast health check responses

### API Endpoints

#### Health Check
```
GET /api/v1/monitoring/health/
```
Returns comprehensive system health status including:
- Database connectivity
- Cache availability
- Disk space
- Memory usage
- Recent error count

#### Metrics
```
GET /api/v1/monitoring/metrics/
```
Returns Prometheus-style metrics for external monitoring systems.

#### System Status
```
GET /api/v1/monitoring/status/
```
Detailed system status for admin dashboard (requires authentication).

#### User Feedback
```
POST /api/v1/monitoring/feedback/
```
Allows users to submit error reports and feedback.

### Database Models

#### SystemHealth
Tracks component health status and details.

#### ErrorLog
Stores application errors with context:
- Error level (debug, info, warning, error, critical)
- Source (django, celery, scraping, frontend, api)
- Request information
- User agent and IP address
- Metadata for debugging

#### PerformanceMetric
Records performance measurements:
- Response times
- Memory usage
- Database query times
- CPU usage

#### UserFeedback
Stores user-submitted feedback and error reports.

### Celery Tasks

#### Scheduled Tasks
- `system_health_check`: Every 5 minutes
- `cleanup_old_monitoring_data`: Daily
- `generate_monitoring_report`: Daily
- `alert_on_critical_errors`: Every 5 minutes

## Frontend Monitoring

### Components

#### 1. Error Boundary (`ErrorBoundary.js`)
- Catches JavaScript errors in React components
- Reports errors to Sentry and backend
- Provides user-friendly error UI
- Collects user feedback

#### 2. Monitoring Service (`monitoring.js`)
- Global error tracking
- Performance monitoring (Web Vitals)
- User interaction tracking
- Network error detection

#### 3. Feedback Modal (`FeedbackModal.js`)
- User feedback collection interface
- Error context submission
- Contact information capture

### Features

#### Error Tracking
- Global error handlers for unhandled errors
- Promise rejection tracking
- Resource loading error detection
- Component-level error boundaries

#### Performance Monitoring
- Page load times
- Web Vitals (LCP, FID, CLS)
- API response times
- Resource loading times

#### User Feedback
- Error reporting interface
- Context preservation
- Contact information collection

### Sentry Integration
- Automatic error capture
- Performance monitoring
- User context tracking
- Environment-specific configuration

## Configuration

### Backend Environment Variables

```bash
# Sentry Configuration
SENTRY_DSN=your-sentry-dsn-here
SENTRY_TRACES_SAMPLE_RATE=0.1
ENVIRONMENT=production
RELEASE_VERSION=1.0.0

# Monitoring Configuration
MONITORING_ENABLED=True
MONITORING_PERFORMANCE_THRESHOLD=1000
MONITORING_ERROR_RETENTION_DAYS=30
```

### Frontend Environment Variables

```bash
# Sentry Configuration
REACT_APP_SENTRY_DSN=your-sentry-dsn-here
REACT_APP_SENTRY_DEBUG=false

# Feature Flags
REACT_APP_ENABLE_MONITORING=true
REACT_APP_ENABLE_PERFORMANCE_TRACKING=true
REACT_APP_ENABLE_ERROR_TRACKING=true

# Performance Configuration
REACT_APP_PERFORMANCE_SAMPLE_RATE=0.1
```

## Setup Instructions

### 1. Backend Setup

1. Install dependencies:
```bash
pip install sentry-sdk psutil
```

2. Add monitoring app to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    'apps.monitoring',
]
```

3. Add middleware to `MIDDLEWARE`:
```python
MIDDLEWARE = [
    # ...
    'apps.monitoring.middleware.SecurityHeadersMiddleware',
    'apps.monitoring.middleware.HealthCheckMiddleware',
    'apps.monitoring.middleware.RequestTrackingMiddleware',
    'apps.monitoring.middleware.RateLimitMiddleware',
]
```

4. Run migrations:
```bash
python manage.py makemigrations monitoring
python manage.py migrate
```

5. Configure Sentry in settings:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=True,
)
```

### 2. Frontend Setup

1. Install dependencies:
```bash
npm install @sentry/react @sentry/tracing
```

2. Initialize Sentry in `src/index.js`:
```javascript
import { initSentry } from './services/sentry';
initSentry();
```

3. Wrap components with error boundaries:
```javascript
import ErrorBoundary from './components/ErrorBoundary';

<ErrorBoundary name="ComponentName">
  <YourComponent />
</ErrorBoundary>
```

4. Initialize monitoring service:
```javascript
import monitor from './services/monitoring';
monitor.init();
```

## Usage

### Monitoring Dashboard

Access the Django admin interface to view:
- System health records
- Error logs with filtering and search
- Performance metrics
- User feedback

### Health Checks

Use the health check endpoint for:
- Load balancer health checks
- Monitoring system integration
- Automated alerting

### Error Tracking

Errors are automatically captured and include:
- Stack traces
- User context
- Request information
- Environment details

### Performance Monitoring

Track key metrics:
- API response times
- Page load performance
- Database query performance
- System resource usage

## Alerting

### Critical Error Alerts

The system automatically checks for critical errors and can be configured to:
- Send email notifications
- Post to Slack channels
- Create PagerDuty incidents
- Send SMS alerts

### Custom Alert Configuration

Extend the `alert_on_critical_errors` task to integrate with your preferred alerting system.

## Best Practices

### Error Handling
1. Use structured logging with context
2. Implement proper error boundaries
3. Provide meaningful error messages
4. Include debugging information

### Performance
1. Monitor key performance indicators
2. Set performance budgets
3. Use sampling for high-traffic applications
4. Regular performance reviews

### Security
1. Don't log sensitive information
2. Sanitize user inputs
3. Implement rate limiting
4. Use security headers

### Maintenance
1. Regular cleanup of old data
2. Monitor storage usage
3. Review error trends
4. Update alerting thresholds

## Troubleshooting

### Common Issues

#### High Error Rates
1. Check recent deployments
2. Review error patterns
3. Examine system resources
4. Verify external dependencies

#### Performance Degradation
1. Check database performance
2. Review recent changes
3. Monitor system resources
4. Analyze slow requests

#### Missing Data
1. Verify configuration
2. Check network connectivity
3. Review sampling rates
4. Examine error logs

### Debug Mode

Enable debug mode for detailed logging:
```bash
# Backend
DEBUG=True

# Frontend
REACT_APP_SENTRY_DEBUG=true
```

## Integration with External Services

### Sentry
- Error tracking and performance monitoring
- User feedback collection
- Release tracking
- Environment management

### Prometheus
- Metrics export endpoint
- Custom metrics collection
- Alerting integration

### Grafana
- Dashboard creation
- Metric visualization
- Alert management

## Future Enhancements

1. **Advanced Analytics**: Implement user behavior tracking
2. **Real-time Alerts**: WebSocket-based real-time notifications
3. **ML-based Anomaly Detection**: Automatic anomaly detection
4. **Custom Dashboards**: User-configurable monitoring dashboards
5. **Mobile App Monitoring**: Extend monitoring to mobile applications

## Support

For questions or issues related to the monitoring system:
1. Check the documentation
2. Review error logs
3. Contact the development team
4. Create an issue in the project repository