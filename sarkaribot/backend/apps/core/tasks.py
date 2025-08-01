"""
Core Celery tasks for SarkariBot.
"""

from celery import shared_task
from django.core.cache import cache
from django.db import connection
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def health_check(self):
    """
    Periodic health check task.
    
    Monitors system health and logs any issues.
    
    Returns:
        Dict with health check results
    """
    try:
        health_data = {
            'database': False,
            'cache': False,
            'timestamp': timezone.now().isoformat()
        }
        
        # Check database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_data['database'] = True
            logger.info("Database health check: OK")
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
        
        # Check cache
        try:
            cache.set('health_check_task', 'ok', 30)
            if cache.get('health_check_task') == 'ok':
                health_data['cache'] = True
                logger.info("Cache health check: OK")
            else:
                logger.error("Cache health check failed: read/write test failed")
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
        
        # Alert if any component is unhealthy
        if not all([health_data['database'], health_data['cache']]):
            logger.critical(f"System health check failed: {health_data}")
        
        return health_data
        
    except Exception as exc:
        logger.error(f"Health check task failed: {exc}")
        raise self.retry(countdown=60 * (self.request.retries + 1))
