"""
Django signals for the alerts app.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import JobAlert, UserNotificationPreference
from apps.jobs.models import JobPosting
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def create_user_notification_preferences(sender, instance, created, **kwargs):
    """
    Create default notification preferences when a new user is created.
    """
    if created:
        try:
            UserNotificationPreference.objects.create(user=instance)
            logger.info(f"Created notification preferences for user {instance.username}")
        except Exception as e:
            logger.error(f"Error creating notification preferences for user {instance.username}: {e}")


@receiver(post_save, sender=JobPosting)
def trigger_instant_alerts(sender, instance, created, **kwargs):
    """
    Trigger instant alerts when a new job is posted.
    """
    if created and instance.status == 'announced':
        try:
            # Get all active instant alerts
            instant_alerts = JobAlert.objects.filter(
                is_active=True,
                frequency='instant'
            )
            
            for alert in instant_alerts:
                # Check if this job matches the alert criteria
                matching_jobs = alert.get_matching_jobs()
                if matching_jobs.filter(id=instance.id).exists():
                    # Queue instant alert
                    from .services import send_instant_alert_task
                    send_instant_alert_task.delay(str(alert.id))
                    logger.info(f"Queued instant alert {alert.id} for new job {instance.id}")
                    
        except Exception as e:
            logger.error(f"Error triggering instant alerts for job {instance.id}: {e}")


@receiver(pre_delete, sender=JobAlert)
def cleanup_alert_logs(sender, instance, **kwargs):
    """
    Clean up alert logs when an alert is deleted.
    """
    try:
        log_count = instance.logs.count()
        instance.logs.all().delete()
        logger.info(f"Cleaned up {log_count} logs for deleted alert {instance.id}")
    except Exception as e:
        logger.error(f"Error cleaning up logs for alert {instance.id}: {e}")


@receiver(post_save, sender=JobAlert)
def validate_alert_configuration(sender, instance, created, **kwargs):
    """
    Validate alert configuration and log any issues.
    """
    try:
        issues = []
        
        # Check delivery method configuration
        if instance.delivery_method == 'email' and not instance.delivery_email:
            issues.append("Email delivery method requires email address")
        
        if instance.delivery_method == 'sms' and not instance.delivery_phone:
            issues.append("SMS delivery method requires phone number")
        
        if instance.delivery_method == 'webhook' and not instance.webhook_url:
            issues.append("Webhook delivery method requires webhook URL")
        
        # Check if alert has any criteria
        has_criteria = any([
            instance.keywords,
            instance.categories.exists(),
            instance.sources.exists(),
            instance.locations,
            instance.qualifications,
            instance.min_salary,
            instance.max_salary,
            instance.min_age,
            instance.max_age
        ])
        
        if not has_criteria:
            issues.append("Alert has no search criteria defined")
        
        if issues:
            logger.warning(f"Alert {instance.id} has configuration issues: {', '.join(issues)}")
        
    except Exception as e:
        logger.error(f"Error validating alert {instance.id}: {e}")
