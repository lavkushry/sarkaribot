"""
Celery tasks for monitoring and maintenance.
"""
import logging
from typing import Dict, Any
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from celery import shared_task
from .models import ErrorLog, PerformanceMetric, SystemHealth, UserFeedback

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def cleanup_old_monitoring_data(self) -> Dict[str, Any]:
    """
    Clean up old monitoring data to prevent database bloat.
    """
    try:
        retention_days = getattr(settings, 'MONITORING_ERROR_RETENTION_DAYS', 30)
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        
        # Clean up old error logs
        old_errors = ErrorLog.objects.filter(created_at__lt=cutoff_date)
        error_count = old_errors.count()
        old_errors.delete()
        
        # Clean up old performance metrics (keep more recent data)
        perf_cutoff = timezone.now() - timedelta(days=7)
        old_metrics = PerformanceMetric.objects.filter(recorded_at__lt=perf_cutoff)
        metric_count = old_metrics.count()
        old_metrics.delete()
        
        # Clean up old resolved feedback
        feedback_cutoff = timezone.now() - timedelta(days=retention_days)
        old_feedback = UserFeedback.objects.filter(
            created_at__lt=feedback_cutoff,
            resolved=True
        )
        feedback_count = old_feedback.count()
        old_feedback.delete()
        
        result = {
            'errors_deleted': error_count,
            'metrics_deleted': metric_count,
            'feedback_deleted': feedback_count,
            'cleanup_date': timezone.now().isoformat()
        }
        
        logger.info(f"Monitoring cleanup completed: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Monitoring cleanup failed: {exc}")
        raise self.retry(countdown=60 * 5)  # Retry in 5 minutes


@shared_task(bind=True)
def system_health_check(self) -> Dict[str, Any]:
    """
    Perform comprehensive system health check.
    """
    try:
        import psutil
        from django.db import connection
        from django.core.cache import cache
        
        health_results = {
            'timestamp': timezone.now().isoformat(),
            'checks': {}
        }
        
        # Database health check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_results['checks']['database'] = {
                    'status': 'healthy',
                    'response_time': 'fast'
                }
        except Exception as e:
            health_results['checks']['database'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Cache health check
        try:
            cache.set('health_check_task', 'ok', 10)
            if cache.get('health_check_task') == 'ok':
                health_results['checks']['cache'] = {'status': 'healthy'}
            else:
                health_results['checks']['cache'] = {'status': 'unhealthy'}
        except Exception as e:
            health_results['checks']['cache'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # System resource checks
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            health_results['checks']['memory'] = {
                'status': 'healthy' if memory.percent < 90 else 'warning',
                'usage_percent': memory.percent,
                'available_gb': round(memory.available / (1024**3), 2)
            }
            
            # Disk space
            disk = psutil.disk_usage('/')
            free_percent = (disk.free / disk.total) * 100
            health_results['checks']['disk'] = {
                'status': 'healthy' if free_percent > 20 else 'warning',
                'free_percent': round(free_percent, 2),
                'free_gb': round(disk.free / (1024**3), 2)
            }
            
            # CPU usage (average over 1 second)
            cpu_percent = psutil.cpu_percent(interval=1)
            health_results['checks']['cpu'] = {
                'status': 'healthy' if cpu_percent < 80 else 'warning',
                'usage_percent': cpu_percent
            }
            
        except Exception as e:
            health_results['checks']['system_resources'] = {
                'status': 'unknown',
                'error': str(e)
            }
        
        # Recent error analysis
        try:
            recent_errors = ErrorLog.objects.filter(
                created_at__gte=timezone.now() - timedelta(minutes=5),
                level__in=['error', 'critical']
            ).count()
            
            health_results['checks']['recent_errors'] = {
                'status': 'healthy' if recent_errors < 5 else 'warning',
                'count': recent_errors
            }
        except Exception as e:
            health_results['checks']['recent_errors'] = {
                'status': 'unknown',
                'error': str(e)
            }
        
        # Determine overall status
        statuses = [check['status'] for check in health_results['checks'].values()]
        if 'unhealthy' in statuses:
            overall_status = 'unhealthy'
        elif 'warning' in statuses:
            overall_status = 'degraded'
        else:
            overall_status = 'healthy'
        
        health_results['overall_status'] = overall_status
        
        # Update SystemHealth record
        SystemHealth.objects.update_or_create(
            component='system_health_task',
            defaults={
                'status': overall_status,
                'details': health_results['checks']
            }
        )
        
        logger.info(f"System health check completed: {overall_status}")
        return health_results
        
    except Exception as exc:
        logger.error(f"System health check failed: {exc}")
        raise self.retry(countdown=60 * 2)  # Retry in 2 minutes


@shared_task(bind=True)
def generate_monitoring_report(self) -> Dict[str, Any]:
    """
    Generate daily monitoring report.
    """
    try:
        from django.db.models import Count, Avg
        
        end_time = timezone.now()
        start_time = end_time - timedelta(days=1)
        
        # Error statistics
        error_stats = ErrorLog.objects.filter(
            created_at__gte=start_time,
            created_at__lt=end_time
        ).values('level').annotate(count=Count('id'))
        
        # Performance statistics
        perf_stats = PerformanceMetric.objects.filter(
            recorded_at__gte=start_time,
            recorded_at__lt=end_time
        ).values('metric_type').annotate(
            avg_value=Avg('value'),
            count=Count('id')
        )
        
        # User feedback statistics
        feedback_stats = UserFeedback.objects.filter(
            created_at__gte=start_time,
            created_at__lt=end_time
        ).values('feedback_type').annotate(count=Count('id'))
        
        # System health summary
        health_records = SystemHealth.objects.filter(
            last_check__gte=start_time
        ).values('component', 'status').annotate(count=Count('id'))
        
        report = {
            'period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'error_statistics': list(error_stats),
            'performance_statistics': list(perf_stats),
            'feedback_statistics': list(feedback_stats),
            'health_summary': list(health_records),
            'generated_at': timezone.now().isoformat()
        }
        
        logger.info("Daily monitoring report generated successfully")
        return report
        
    except Exception as exc:
        logger.error(f"Failed to generate monitoring report: {exc}")
        raise self.retry(countdown=60 * 10)  # Retry in 10 minutes


@shared_task(bind=True)
def alert_on_critical_errors(self) -> Dict[str, Any]:
    """
    Check for critical errors and send alerts.
    """
    try:
        # Look for critical errors in the last 5 minutes
        recent_critical = ErrorLog.objects.filter(
            level='critical',
            created_at__gte=timezone.now() - timedelta(minutes=5),
            resolved=False
        ).order_by('-created_at')
        
        if recent_critical.exists():
            # In a real implementation, you would send emails, Slack notifications, etc.
            # For now, we'll just log the alert
            critical_count = recent_critical.count()
            
            logger.critical(
                f"ALERT: {critical_count} critical errors detected in the last 5 minutes"
            )
            
            # You could integrate with external services here:
            # - Send email notifications
            # - Post to Slack
            # - Create PagerDuty incidents
            # - Send SMS alerts
            
            return {
                'alert_triggered': True,
                'critical_error_count': critical_count,
                'timestamp': timezone.now().isoformat()
            }
        
        return {
            'alert_triggered': False,
            'critical_error_count': 0,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Failed to check for critical errors: {exc}")
        raise self.retry(countdown=60)  # Retry in 1 minute