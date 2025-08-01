"""
Views for monitoring and health check endpoints.
"""
import logging
import psutil
from typing import Dict, Any
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db import connection
from django.conf import settings
from django.db import models
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import SystemHealth, ErrorLog, PerformanceMetric, UserFeedback

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
@cache_page(60)  # Cache for 1 minute
def health_check(request):
    """
    Comprehensive health check endpoint.
    
    Returns system health status including database, cache, and disk space.
    """
    try:
        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'service': 'sarkaribot-backend',
            'version': getattr(settings, 'VERSION', '1.0.0'),
            'checks': {}
        }
        
        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_data['checks']['database'] = {
                    'status': 'healthy',
                    'response_time': 'fast'
                }
        except Exception as e:
            health_data['checks']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_data['status'] = 'degraded'
        
        # Cache check
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                health_data['checks']['cache'] = {'status': 'healthy'}
            else:
                health_data['checks']['cache'] = {'status': 'unhealthy'}
                health_data['status'] = 'degraded'
        except Exception as e:
            health_data['checks']['cache'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_data['status'] = 'degraded'
        
        # Disk space check
        try:
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100
            
            if free_percent > 20:
                disk_status = 'healthy'
            elif free_percent > 10:
                disk_status = 'warning'
                health_data['status'] = 'degraded'
            else:
                disk_status = 'critical'
                health_data['status'] = 'unhealthy'
            
            health_data['checks']['disk_space'] = {
                'status': disk_status,
                'free_percent': round(free_percent, 2),
                'free_gb': round(disk_usage.free / (1024**3), 2)
            }
        except Exception as e:
            health_data['checks']['disk_space'] = {
                'status': 'unknown',
                'error': str(e)
            }
        
        # Memory check
        try:
            memory = psutil.virtual_memory()
            health_data['checks']['memory'] = {
                'status': 'healthy' if memory.percent < 90 else 'warning',
                'usage_percent': memory.percent,
                'available_gb': round(memory.available / (1024**3), 2)
            }
            if memory.percent >= 90:
                health_data['status'] = 'degraded'
        except Exception as e:
            health_data['checks']['memory'] = {
                'status': 'unknown',
                'error': str(e)
            }
        
        # Recent errors check
        try:
            recent_errors = ErrorLog.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(minutes=5),
                level__in=['error', 'critical']
            ).count()
            
            if recent_errors == 0:
                error_status = 'healthy'
            elif recent_errors < 5:
                error_status = 'warning'
                health_data['status'] = 'degraded'
            else:
                error_status = 'critical'
                health_data['status'] = 'unhealthy'
            
            health_data['checks']['recent_errors'] = {
                'status': error_status,
                'count': recent_errors
            }
        except Exception as e:
            health_data['checks']['recent_errors'] = {
                'status': 'unknown',
                'error': str(e)
            }
        
        # Update SystemHealth record
        SystemHealth.objects.update_or_create(
            component='overall_system',
            defaults={
                'status': health_data['status'],
                'details': health_data['checks']
            }
        )
        
        status_code = 200 if health_data['status'] == 'healthy' else 503
        return Response(health_data, status=status_code)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return Response(
            {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            },
            status=500
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def metrics(request):
    """
    Endpoint for Prometheus-style metrics.
    """
    try:
        metrics_data = []
        
        # Recent performance metrics
        recent_metrics = PerformanceMetric.objects.filter(
            recorded_at__gte=timezone.now() - timezone.timedelta(hours=1)
        ).values('metric_type').distinct()
        
        for metric in recent_metrics:
            avg_value = PerformanceMetric.objects.filter(
                metric_type=metric['metric_type'],
                recorded_at__gte=timezone.now() - timezone.timedelta(hours=1)
            ).aggregate(avg_value=models.Avg('value'))['avg_value']
            
            metrics_data.append({
                'name': f"sarkaribot_{metric['metric_type']}_avg",
                'value': round(avg_value or 0, 2),
                'timestamp': timezone.now().isoformat()
            })
        
        # Error counts
        error_counts = ErrorLog.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(hours=1)
        ).values('level').annotate(count=models.Count('id'))
        
        for error_count in error_counts:
            metrics_data.append({
                'name': f"sarkaribot_errors_{error_count['level']}_total",
                'value': error_count['count'],
                'timestamp': timezone.now().isoformat()
            })
        
        return Response({'metrics': metrics_data})
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def error_feedback(request):
    """
    Endpoint for users to submit feedback about errors.
    """
    try:
        data = request.data
        
        feedback = UserFeedback.objects.create(
            feedback_type=data.get('type', 'error_feedback'),
            message=data.get('message', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            page_url=data.get('page_url', ''),
            contact_info=data.get('contact_info', ''),
            metadata={
                'user_data': data.get('user_data', {}),
                'browser_info': data.get('browser_info', {}),
                'timestamp': timezone.now().isoformat()
            }
        )
        
        return Response({
            'success': True,
            'feedback_id': feedback.id,
            'message': 'Thank you for your feedback!'
        })
        
    except Exception as e:
        logger.error(f"Error feedback submission failed: {e}")
        return Response(
            {'error': 'Failed to submit feedback'},
            status=500
        )


@api_view(['GET'])
def system_status(request):
    """
    Get comprehensive system status for admin dashboard.
    """
    try:
        # Recent system health
        health_records = SystemHealth.objects.all()[:10]
        
        # Error statistics
        error_stats = {
            'total_errors_24h': ErrorLog.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=1)
            ).count(),
            'critical_errors_24h': ErrorLog.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=1),
                level='critical'
            ).count(),
            'unresolved_errors': ErrorLog.objects.filter(resolved=False).count(),
        }
        
        # Performance averages
        perf_stats = {}
        for metric_type in ['response_time', 'memory_usage', 'cpu_usage']:
            avg_value = PerformanceMetric.objects.filter(
                metric_type=metric_type,
                recorded_at__gte=timezone.now() - timezone.timedelta(hours=24)
            ).aggregate(avg_value=models.Avg('value'))['avg_value']
            perf_stats[f'avg_{metric_type}_24h'] = round(avg_value or 0, 2)
        
        # User feedback summary
        feedback_stats = {
            'total_feedback_7d': UserFeedback.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
            'unresolved_feedback': UserFeedback.objects.filter(resolved=False).count(),
        }
        
        return Response({
            'system_health': [
                {
                    'component': h.component,
                    'status': h.status,
                    'last_check': h.last_check,
                    'details': h.details
                }
                for h in health_records
            ],
            'error_statistics': error_stats,
            'performance_statistics': perf_stats,
            'feedback_statistics': feedback_stats,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"System status endpoint failed: {e}")
        return Response({'error': str(e)}, status=500)