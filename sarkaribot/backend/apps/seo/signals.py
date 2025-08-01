"""
Django signals for the SEO app.

This module contains signal handlers for automatic SEO metadata generation
and management triggered by job posting lifecycle events.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
import logging
from typing import Any

logger = logging.getLogger(__name__)


@receiver(post_save, sender='jobs.JobPosting')
def auto_generate_seo_metadata(sender: Any, instance: Any, created: bool, **kwargs):
    """
    Automatically generate SEO metadata when a job posting is created or updated.
    
    Args:
        sender: The model class that sent the signal
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    try:
        # Only proceed if SEO automation is enabled
        if not getattr(settings, 'SARKARIBOT_SETTINGS', {}).get('ENABLE_SEO_AUTOMATION', True):
            return
        
        # Skip if this is a save specifically to update SEO fields (prevent recursion)
        if hasattr(instance, '_updating_seo_metadata'):
            return
        
        # Check if SEO metadata needs generation
        needs_seo_update = (
            created or  # New job posting
            not instance.seo_title or  # Missing SEO title
            not instance.seo_description or  # Missing SEO description
            not instance.keywords  # Missing keywords
        )
        
        if needs_seo_update:
            logger.info(f"Triggering SEO metadata generation for job: {instance.id} - {instance.title}")
            
            # Import here to avoid circular imports
            from apps.seo.tasks import generate_seo_metadata
            
            # Queue SEO generation task asynchronously
            generate_seo_metadata.delay(
                job_posting_id=instance.id,
                force_update=not created  # Force update for existing jobs
            )
            
        elif created:
            logger.debug(f"SEO metadata already exists for job: {instance.id}")
            
    except Exception as e:
        logger.error(f"Failed to trigger SEO metadata generation for job {instance.id}: {e}")


@receiver(post_save, sender='jobs.JobPosting')
def update_sitemap_on_job_change(sender: Any, instance: Any, created: bool, **kwargs):
    """
    Update sitemap when a job posting is created or significantly updated.
    
    Args:
        sender: The model class that sent the signal
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    try:
        # Only proceed if sitemap generation is enabled
        if not getattr(settings, 'SARKARIBOT_SETTINGS', {}).get('GENERATE_SITEMAP', True):
            return
        
        # Check if this is a significant change that affects sitemap
        significant_change = (
            created or  # New job posting
            instance.status in ['announced', 'admit_card', 'answer_key', 'result']  # Active status
        )
        
        if significant_change:
            logger.debug(f"Triggering sitemap update for job: {instance.id}")
            
            # Import here to avoid circular imports
            from apps.seo.tasks import generate_sitemap_data
            
            # Queue sitemap generation (with a delay to batch multiple changes)
            generate_sitemap_data.apply_async(countdown=300)  # 5 minute delay
            
    except Exception as e:
        logger.error(f"Failed to trigger sitemap update for job {instance.id}: {e}")


@receiver(post_delete, sender='jobs.JobPosting')
def update_sitemap_on_job_delete(sender: Any, instance: Any, **kwargs):
    """
    Update sitemap when a job posting is deleted.
    
    Args:
        sender: The model class that sent the signal
        instance: The deleted instance
        **kwargs: Additional keyword arguments
    """
    try:
        # Only proceed if sitemap generation is enabled
        if not getattr(settings, 'SARKARIBOT_SETTINGS', {}).get('GENERATE_SITEMAP', True):
            return
        
        logger.debug(f"Triggering sitemap update after job deletion: {instance.id}")
        
        # Import here to avoid circular imports
        from apps.seo.tasks import generate_sitemap_data
        
        # Queue sitemap generation (with a delay to batch multiple changes)
        generate_sitemap_data.apply_async(countdown=300)  # 5 minute delay
        
    except Exception as e:
        logger.error(f"Failed to trigger sitemap update after job deletion {instance.id}: {e}")


@receiver(post_save, sender='seo.SEOMetadata')
def log_seo_metadata_update(sender: Any, instance: Any, created: bool, **kwargs):
    """
    Log SEO metadata updates for audit purposes.
    
    Args:
        sender: The model class that sent the signal
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    try:
        # Import here to avoid circular imports
        from apps.seo.models import SEOAuditLog
        
        # Create audit log entry
        SEOAuditLog.objects.create(
            audit_type='metadata_generation',
            content_type=instance.content_type,
            content_id=instance.content_id,
            status='success',
            details={
                'title_length': len(instance.title),
                'description_length': len(instance.description),
                'keywords_count': len(instance.keywords.split(',')) if instance.keywords else 0,
                'generation_method': instance.generation_method,
                'quality_score': float(instance.quality_score) if instance.quality_score else None,
                'created': created,
            }
        )
        
        logger.debug(f"SEO metadata audit logged for {instance.content_type}:{instance.content_id}")
        
    except Exception as e:
        logger.error(f"Failed to log SEO metadata update: {e}")


@receiver(post_save, sender='jobs.JobCategory')
def update_category_seo_metadata(sender: Any, instance: Any, created: bool, **kwargs):
    """
    Update SEO metadata for job postings when their category is updated.
    
    Args:
        sender: The model class that sent the signal
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    try:
        # Only proceed if this is an update to an existing category
        if created:
            return
        
        # Only proceed if SEO automation is enabled
        if not getattr(settings, 'SARKARIBOT_SETTINGS', {}).get('ENABLE_SEO_AUTOMATION', True):
            return
        
        # Import here to avoid circular imports
        from apps.seo.tasks import bulk_generate_seo_metadata
        
        # Queue SEO regeneration for all jobs in this category
        bulk_generate_seo_metadata.delay(
            category_slug=instance.slug,
            force_update=True
        )
        
        logger.info(f"Triggered SEO metadata update for category: {instance.name}")
        
    except Exception as e:
        logger.error(f"Failed to update SEO metadata for category {instance.id}: {e}")


@receiver(pre_save, sender='jobs.JobPosting')
def detect_significant_job_changes(sender: Any, instance: Any, **kwargs):
    """
    Detect significant changes to job postings that require SEO updates.
    
    Args:
        sender: The model class that sent the signal
        instance: The actual instance being saved
        **kwargs: Additional keyword arguments
    """
    try:
        # Skip for new instances
        if instance.pk is None:
            return
        
        # Get the current instance from database
        try:
            current = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        
        # Check for significant changes that affect SEO
        significant_changes = [
            instance.title != current.title,
            instance.description != current.description,
            instance.department != current.department,
            instance.qualification != current.qualification,
            instance.location != current.location,
            instance.status != current.status,
        ]
        
        if any(significant_changes):
            # Mark that SEO metadata should be regenerated
            instance._needs_seo_update = True
            logger.debug(f"Detected significant changes for job {instance.id}, marking for SEO update")
        
    except Exception as e:
        logger.error(f"Failed to detect job changes for {instance.id}: {e}")


# Signal for handling scheduled SEO tasks
def schedule_periodic_seo_tasks():
    """
    Schedule periodic SEO maintenance tasks.
    
    This function is called during app initialization to set up
    recurring SEO optimization tasks.
    """
    try:
        from django_celery_beat.models import PeriodicTask, CrontabSchedule
        import json
        
        # Daily SEO maintenance task
        daily_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='2',  # 2 AM
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )
        
        # Weekly SEO analysis task
        weekly_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='3',  # 3 AM
            day_of_week='1',  # Monday
            day_of_month='*',
            month_of_year='*',
        )
        
        # Create or update periodic tasks
        PeriodicTask.objects.update_or_create(
            name='Daily SEO Metadata Update',
            defaults={
                'crontab': daily_schedule,
                'task': 'apps.seo.tasks.update_outdated_seo_metadata',
                'args': json.dumps([]),
                'kwargs': json.dumps({}),
                'enabled': True,
            }
        )
        
        PeriodicTask.objects.update_or_create(
            name='Weekly SEO Performance Analysis',
            defaults={
                'crontab': weekly_schedule,
                'task': 'apps.seo.tasks.analyze_seo_performance',
                'args': json.dumps([]),
                'kwargs': json.dumps({}),
                'enabled': True,
            }
        )
        
        logger.info("Periodic SEO tasks scheduled successfully")
        
    except ImportError:
        logger.warning("django-celery-beat not installed, skipping periodic task setup")
    except Exception as e:
        logger.error(f"Failed to schedule periodic SEO tasks: {e}")