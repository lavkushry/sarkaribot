"""
Signal handlers for monitoring app.
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.signals import request_finished
from .models import ErrorLog

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ErrorLog)
def handle_error_logged(sender, instance, created, **kwargs):
    """Handle new error logs."""
    if created and instance.level in ['error', 'critical']:
        logger.warning(f"New {instance.level} error logged: {instance.message}")
        
        # Here you could trigger alerts, notifications, etc.
        # For example, send to Slack, email, or PagerDuty
        
        # Example: Log critical errors immediately to console
        if instance.level == 'critical':
            logger.critical(f"CRITICAL ERROR: {instance.message}")


# You can add more signal handlers here for different monitoring events