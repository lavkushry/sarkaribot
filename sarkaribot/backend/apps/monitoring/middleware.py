"""
Custom middleware for monitoring and error tracking.
"""
import time
import logging
from typing import Any, Callable, Optional
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from .models import ErrorLog, PerformanceMetric

logger = logging.getLogger(__name__)


class RequestTrackingMiddleware(MiddlewareMixin):
    """Track request performance and errors."""
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Record request start time."""
        request._monitoring_start_time = time.time()
        request._monitoring_db_queries_start = len(connection.queries)
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Record request metrics."""
        try:
            if hasattr(request, '_monitoring_start_time'):
                # Calculate response time
                response_time = (time.time() - request._monitoring_start_time) * 1000
                
                # Calculate database queries
                db_queries = len(connection.queries) - request._monitoring_db_queries_start
                
                # Record performance metrics
                if response_time > 100:  # Only record slow requests
                    PerformanceMetric.objects.create(
                        metric_type='response_time',
                        value=response_time,
                        unit='ms',
                        component=f"{request.method} {request.path}",
                        metadata={
                            'status_code': response.status_code,
                            'db_queries': db_queries,
                            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        }
                    )
                
                # Add performance headers
                response['X-Response-Time'] = f"{response_time:.2f}ms"
                response['X-DB-Queries'] = str(db_queries)
                
        except Exception as e:
            logger.error(f"Error in RequestTrackingMiddleware: {e}")
        
        return response
    
    def process_exception(self, request: HttpRequest, exception: Exception) -> Optional[HttpResponse]:
        """Log exceptions."""
        try:
            ErrorLog.log_error(
                level='error',
                source='django',
                message=str(exception),
                traceback=self._get_traceback(),
                request=request,
                metadata={
                    'exception_type': exception.__class__.__name__,
                }
            )
        except Exception as e:
            logger.error(f"Error logging exception: {e}")
        
        return None
    
    def _get_traceback(self) -> str:
        """Get current traceback as string."""
        import traceback
        return traceback.format_exc()


class RateLimitMiddleware(MiddlewareMixin):
    """Basic rate limiting middleware."""
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Check rate limits."""
        try:
            if not settings.DEBUG:  # Only apply in production
                client_ip = self._get_client_ip(request)
                cache_key = f"rate_limit:{client_ip}"
                
                # Get current request count
                current_requests = cache.get(cache_key, 0)
                
                # Check limit (100 requests per minute)
                if current_requests >= 100:
                    from django.http import JsonResponse
                    return JsonResponse(
                        {'error': 'Rate limit exceeded'}, 
                        status=429
                    )
                
                # Increment counter
                cache.set(cache_key, current_requests + 1, 60)
                
        except Exception as e:
            logger.error(f"Error in RateLimitMiddleware: {e}")
        
        return None
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to responses."""
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Add security headers."""
        try:
            # Add security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Add CSP header for HTML responses
            if response.get('Content-Type', '').startswith('text/html'):
                response['Content-Security-Policy'] = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data: https:; "
                    "font-src 'self' https:; "
                    "connect-src 'self' https:;"
                )
            
        except Exception as e:
            logger.error(f"Error in SecurityHeadersMiddleware: {e}")
        
        return response


class HealthCheckMiddleware(MiddlewareMixin):
    """Handle health check requests efficiently."""
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Handle health check requests."""
        if request.path in ['/health/', '/health', '/healthz']:
            from django.http import JsonResponse
            from django.utils import timezone
            
            try:
                # Quick health check
                health_data = {
                    'status': 'healthy',
                    'timestamp': timezone.now().isoformat(),
                    'service': 'sarkaribot-backend',
                }
                
                return JsonResponse(health_data)
            except Exception as e:
                return JsonResponse(
                    {
                        'status': 'unhealthy',
                        'error': str(e),
                        'timestamp': timezone.now().isoformat(),
                    },
                    status=500
                )
        
        return None