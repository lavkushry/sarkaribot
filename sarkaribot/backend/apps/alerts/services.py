"""
Advanced Job Alert Services for SarkariBot
Handles job alert processing, notifications, and delivery.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from celery import shared_task
from .models import JobAlert, JobAlertLog, JobBookmark, JobApplication

logger = logging.getLogger(__name__)


class JobAlertService:
    """
    Service for managing job alerts and notifications.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_alert(self, user, alert_data: Dict[str, Any]) -> JobAlert:
        """
        Create a new job alert for a user.
        
        Args:
            user: User instance
            alert_data: Dictionary containing alert configuration
            
        Returns:
            JobAlert instance
        """
        try:
            alert = JobAlert.objects.create(
                user=user,
                name=alert_data.get('name'),
                keywords=alert_data.get('keywords', ''),
                locations=alert_data.get('locations', ''),
                qualifications=alert_data.get('qualifications', ''),
                min_salary=alert_data.get('min_salary'),
                max_salary=alert_data.get('max_salary'),
                min_age=alert_data.get('min_age'),
                max_age=alert_data.get('max_age'),
                frequency=alert_data.get('frequency', 'daily'),
                delivery_method=alert_data.get('delivery_method', 'email'),
                delivery_email=alert_data.get('delivery_email', user.email),
                delivery_phone=alert_data.get('delivery_phone', ''),
                webhook_url=alert_data.get('webhook_url', ''),
                is_active=alert_data.get('is_active', True)
            )
            
            # Add categories and sources
            if 'category_ids' in alert_data:
                alert.categories.set(alert_data['category_ids'])
            
            if 'source_ids' in alert_data:
                alert.sources.set(alert_data['source_ids'])
            
            self.logger.info(f"Created job alert '{alert.name}' for user {user.username}")
            return alert
            
        except Exception as e:
            self.logger.error(f"Error creating job alert for user {user.username}: {e}")
            raise
    
    def process_alerts(self, frequency: str = None) -> Dict[str, int]:
        """
        Process job alerts based on frequency.
        
        Args:
            frequency: Optional frequency filter (instant, daily, weekly, monthly)
            
        Returns:
            Dictionary with processing statistics
        """
        stats = {'processed': 0, 'sent': 0, 'failed': 0}
        
        try:
            alerts_query = JobAlert.objects.filter(is_active=True)
            
            if frequency:
                alerts_query = alerts_query.filter(frequency=frequency)
            
            for alert in alerts_query:
                try:
                    if self._should_process_alert(alert):
                        result = self._process_single_alert(alert)
                        stats['processed'] += 1
                        
                        if result['success']:
                            stats['sent'] += 1
                        else:
                            stats['failed'] += 1
                            
                except Exception as e:
                    self.logger.error(f"Error processing alert {alert.id}: {e}")
                    stats['failed'] += 1
            
            self.logger.info(f"Processed {stats['processed']} alerts, sent {stats['sent']}, failed {stats['failed']}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error in process_alerts: {e}")
            return stats
    
    def _should_process_alert(self, alert: JobAlert) -> bool:
        """
        Determine if an alert should be processed based on frequency and last sent time.
        """
        if not alert.is_active:
            return False
        
        now = timezone.now()
        
        # For instant alerts, always process
        if alert.frequency == 'instant':
            return True
        
        # Check last sent time
        if not alert.last_sent:
            return True
        
        time_diff = now - alert.last_sent
        
        if alert.frequency == 'daily' and time_diff >= timedelta(days=1):
            return True
        elif alert.frequency == 'weekly' and time_diff >= timedelta(weeks=1):
            return True
        elif alert.frequency == 'monthly' and time_diff >= timedelta(days=30):
            return True
        
        return False
    
    def _process_single_alert(self, alert: JobAlert) -> Dict[str, Any]:
        """
        Process a single job alert and send notifications.
        """
        try:
            # Get time window for new jobs
            since = alert.last_sent or (timezone.now() - timedelta(days=1))
            matching_jobs = alert.get_matching_jobs(since=since)
            
            if not matching_jobs.exists():
                self.logger.debug(f"No matching jobs for alert {alert.id}")
                return {'success': True, 'jobs_count': 0, 'message': 'No new jobs'}
            
            # Send notification based on delivery method
            if alert.delivery_method == 'email':
                success = self._send_email_alert(alert, matching_jobs)
            elif alert.delivery_method == 'sms':
                success = self._send_sms_alert(alert, matching_jobs)
            elif alert.delivery_method == 'push':
                success = self._send_push_alert(alert, matching_jobs)
            elif alert.delivery_method == 'webhook':
                success = self._send_webhook_alert(alert, matching_jobs)
            else:
                success = False
            
            # Log the alert delivery
            log_entry = JobAlertLog.objects.create(
                alert=alert,
                jobs_count=matching_jobs.count(),
                delivery_method=alert.delivery_method,
                status='sent' if success else 'failed',
                error_message='' if success else 'Delivery failed'
            )
            
            # Update last sent time if successful
            if success:
                alert.last_sent = timezone.now()
                alert.save(update_fields=['last_sent'])
            
            return {
                'success': success,
                'jobs_count': matching_jobs.count(),
                'log_id': log_entry.id
            }
            
        except Exception as e:
            self.logger.error(f"Error processing alert {alert.id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _send_email_alert(self, alert: JobAlert, jobs) -> bool:
        """
        Send email notification for job alert.
        """
        try:
            subject = f"SarkariBot Alert: {jobs.count()} new jobs matching '{alert.name}'"
            
            context = {
                'alert': alert,
                'jobs': jobs[:10],  # Limit to first 10 jobs
                'total_count': jobs.count(),
                'unsubscribe_url': f"{settings.FRONTEND_URL}/alerts/unsubscribe/{alert.id}/"
            }
            
            html_message = render_to_string('alerts/email_alert.html', context)
            plain_message = render_to_string('alerts/email_alert.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[alert.delivery_email],
                html_message=html_message,
                fail_silently=False
            )
            
            self.logger.info(f"Email alert sent to {alert.delivery_email} for alert {alert.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email alert {alert.id}: {e}")
            return False
    
    def _send_sms_alert(self, alert: JobAlert, jobs) -> bool:
        """
        Send SMS notification for job alert.
        """
        try:
            # This would integrate with SMS service like Twilio
            message = f"SarkariBot Alert: {jobs.count()} new jobs matching '{alert.name}'. Visit sarkaribot.com for details."
            
            # TODO: Implement SMS sending logic
            self.logger.info(f"SMS alert would be sent to {alert.delivery_phone} for alert {alert.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending SMS alert {alert.id}: {e}")
            return False
    
    def _send_push_alert(self, alert: JobAlert, jobs) -> bool:
        """
        Send push notification for job alert.
        """
        try:
            # This would integrate with push notification service
            title = f"New Jobs Available!"
            body = f"{jobs.count()} new jobs matching '{alert.name}'"
            
            # TODO: Implement push notification logic
            self.logger.info(f"Push notification would be sent for alert {alert.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending push alert {alert.id}: {e}")
            return False
    
    def _send_webhook_alert(self, alert: JobAlert, jobs) -> bool:
        """
        Send webhook notification for job alert.
        """
        try:
            import requests
            
            payload = {
                'alert_id': str(alert.id),
                'alert_name': alert.name,
                'jobs_count': jobs.count(),
                'jobs': [
                    {
                        'id': job.id,
                        'title': job.title,
                        'source': job.source.name,
                        'category': job.category.name,
                        'created_at': job.created_at.isoformat()
                    }
                    for job in jobs[:5]  # Limit to first 5 jobs
                ],
                'timestamp': timezone.now().isoformat()
            }
            
            response = requests.post(
                alert.webhook_url,
                json=payload,
                timeout=30,
                headers={'User-Agent': 'SarkariBot/1.0'}
            )
            
            response.raise_for_status()
            self.logger.info(f"Webhook alert sent to {alert.webhook_url} for alert {alert.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending webhook alert {alert.id}: {e}")
            return False


class BookmarkService:
    """
    Service for managing job bookmarks.
    """
    
    def bookmark_job(self, user, job_id: int, notes: str = '') -> JobBookmark:
        """
        Bookmark a job for a user.
        """
        try:
            bookmark, created = JobBookmark.objects.get_or_create(
                user=user,
                job_id=job_id,
                defaults={'notes': notes}
            )
            
            if not created:
                bookmark.notes = notes
                bookmark.save()
            
            logger.info(f"Job {job_id} bookmarked by user {user.username}")
            return bookmark
            
        except Exception as e:
            logger.error(f"Error bookmarking job {job_id} for user {user.username}: {e}")
            raise
    
    def remove_bookmark(self, user, job_id: int) -> bool:
        """
        Remove a job bookmark for a user.
        """
        try:
            deleted_count, _ = JobBookmark.objects.filter(
                user=user,
                job_id=job_id
            ).delete()
            
            logger.info(f"Bookmark removed for job {job_id} by user {user.username}")
            return deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error removing bookmark for job {job_id} by user {user.username}: {e}")
            return False


class ApplicationTrackingService:
    """
    Service for tracking job applications.
    """
    
    def track_application(self, user, job_id: int, status: str = 'interested', **kwargs) -> JobApplication:
        """
        Track a job application for a user.
        """
        try:
            application, created = JobApplication.objects.get_or_create(
                user=user,
                job_id=job_id,
                defaults={
                    'status': status,
                    'application_date': kwargs.get('application_date'),
                    'notes': kwargs.get('notes', ''),
                    'application_id': kwargs.get('application_id', ''),
                    'documents_submitted': kwargs.get('documents_submitted', [])
                }
            )
            
            if not created:
                # Update existing application
                application.status = status
                application.notes = kwargs.get('notes', application.notes)
                application.application_date = kwargs.get('application_date', application.application_date)
                application.application_id = kwargs.get('application_id', application.application_id)
                application.documents_submitted = kwargs.get('documents_submitted', application.documents_submitted)
                application.save()
            
            logger.info(f"Application tracked for job {job_id} by user {user.username} with status {status}")
            return application
            
        except Exception as e:
            logger.error(f"Error tracking application for job {job_id} by user {user.username}: {e}")
            raise


# Celery tasks for background processing
@shared_task
def process_job_alerts_task(frequency: str = None):
    """
    Celery task to process job alerts.
    """
    service = JobAlertService()
    return service.process_alerts(frequency=frequency)


@shared_task
def send_instant_alert_task(alert_id: str):
    """
    Celery task to send instant job alert.
    """
    try:
        alert = JobAlert.objects.get(id=alert_id, is_active=True)
        service = JobAlertService()
        return service._process_single_alert(alert)
    except JobAlert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
        return {'success': False, 'error': 'Alert not found'}


@shared_task
def cleanup_old_alert_logs_task(days: int = 90):
    """
    Celery task to clean up old alert logs.
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = JobAlertLog.objects.filter(sent_at__lt=cutoff_date).delete()
        logger.info(f"Cleaned up {deleted_count} old alert logs")
        return {'deleted_count': deleted_count}
    except Exception as e:
        logger.error(f"Error cleaning up alert logs: {e}")
        return {'success': False, 'error': str(e)}
