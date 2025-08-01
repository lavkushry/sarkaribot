"""
Core views for SarkariBot.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """
    Simple health check endpoint.
    
    Returns basic system health status.
    """
    
    def get(self, request):
        """
        Get health check status.
        
        Returns:
            Response with health status
        """
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            # Test cache connection
            cache.set('health_check', 'ok', 30)
            cache_status = cache.get('health_check')
            
            health_data = {
                'status': 'healthy',
                'database': 'connected',
                'cache': 'connected' if cache_status == 'ok' else 'disconnected',
                'timestamp': timezone.now().isoformat()
            }
            
            return Response(health_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return Response(
                {
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class SystemStatusView(APIView):
    """
    Detailed system status endpoint.
    
    Returns comprehensive system information.
    """
    
    def get(self, request):
        """
        Get detailed system status.
        
        Returns:
            Response with detailed system information
        """
        try:
            from django.conf import settings
            import sys
            import platform
            
            status_data = {
                'system': {
                    'python_version': sys.version,
                    'platform': platform.platform(),
                    'django_version': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
                },
                'database': self._check_database(),
                'cache': self._check_cache(),
                'settings': {
                    'debug': settings.DEBUG,
                    'timezone': str(settings.TIME_ZONE),
                    'allowed_hosts': settings.ALLOWED_HOSTS,
                },
                'timestamp': timezone.now().isoformat()
            }
            
            return Response(status_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"System status check failed: {e}")
            return Response(
                {
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _check_database(self):
        """Check database connectivity and status."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                db_version = cursor.fetchone()[0]
            
            return {
                'status': 'connected',
                'version': db_version
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_cache(self):
        """Check cache connectivity and status."""
        try:
            test_key = 'system_status_test'
            test_value = 'test_value'
            
            cache.set(test_key, test_value, 30)
            retrieved_value = cache.get(test_key)
            
            if retrieved_value == test_value:
                cache.delete(test_key)
                return {
                    'status': 'connected',
                    'type': 'redis'
                }
            else:
                return {
                    'status': 'error',
                    'error': 'Cache read/write test failed'
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
