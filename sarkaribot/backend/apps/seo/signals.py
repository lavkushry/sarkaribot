"""
SEO automation signals for SarkariBot.

Automatically generates and updates SEO metadata including structured data,
OpenGraph, and Twitter Card metadata when job postings are created or updated.
"""

import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from typing import Dict, Any

from apps.jobs.models import JobPosting
from apps.seo.engine import seo_engine

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=JobPosting)
def generate_seo_metadata_on_save(sender, instance: JobPosting, **kwargs):
    """
    Generate comprehensive SEO metadata when a job posting is saved.
    
    This signal ensures that every job posting has complete structured data,
    OpenGraph, and Twitter Card metadata for optimal SEO performance.
    
    Args:
        sender: The JobPosting model class
        instance: The JobPosting instance being saved
        **kwargs: Additional signal arguments
    """
    try:
        # Skip if this is not a new job and SEO metadata exists and is recent
        if (instance.pk and instance.structured_data and 
            instance.seo_title and instance.open_graph_tags):
            
            # Check if significant fields have changed that require SEO regeneration
            significant_fields = [
                'title', 'description', 'department', 'qualification',
                'total_posts', 'salary_min', 'salary_max', 'application_end_date'
            ]
            
            try:
                old_instance = JobPosting.objects.get(pk=instance.pk)
                has_significant_changes = any(
                    getattr(instance, field) != getattr(old_instance, field)
                    for field in significant_fields
                )
                
                if not has_significant_changes:
                    logger.debug(f"Skipping SEO generation for job {instance.pk} - no significant changes")
                    return
                    
            except JobPosting.DoesNotExist:
                pass  # New instance, continue with generation
        
        # Prepare job data for SEO generation
        job_data = _prepare_job_data_for_seo(instance)
        
        # Generate comprehensive metadata
        logger.info(f"Generating SEO metadata for job: {instance.title}")
        
        metadata = seo_engine.generate_comprehensive_metadata(
            job_data, 
            request_url=f"/jobs/{instance.slug or slugify(instance.title)}/"
        )
        
        # Update instance with generated metadata
        instance.seo_title = metadata.get('seo_title', '')[:60]
        instance.seo_description = metadata.get('seo_description', '')[:160]
        instance.keywords = ', '.join(metadata.get('keywords', []))
        instance.structured_data = metadata.get('structured_data', {})
        instance.open_graph_tags = metadata.get('open_graph', {})
        instance.meta_tags = metadata.get('twitter_card', {})
        
        # Update breadcrumbs
        if metadata.get('breadcrumb_schema'):
            instance.breadcrumbs = metadata['breadcrumb_schema']['itemListElement']
        
        # Update canonical URL
        if metadata.get('canonical_url'):
            instance.canonical_url = metadata['canonical_url']
        
        logger.info(f"Generated SEO metadata with quality score: {metadata.get('quality_score', 0)}")
        
    except Exception as e:
        logger.error(f"Error generating SEO metadata for job {instance.title}: {e}")
        # Don't fail the save operation, just log the error


@receiver(post_save, sender=JobPosting)
def update_seo_metadata_after_save(sender, instance: JobPosting, created: bool, **kwargs):
    """
    Perform additional SEO tasks after a job posting is saved.
    
    Args:
        sender: The JobPosting model class
        instance: The JobPosting instance that was saved
        created: Whether this is a new instance
        **kwargs: Additional signal arguments
    """
    try:
        if created:
            logger.info(f"New job posting created: {instance.title} (ID: {instance.pk})")
            
            # Update SEO audit log
            from apps.seo.models import SEOAuditLog
            
            SEOAuditLog.objects.create(
                audit_type='metadata_generation',
                content_type='job_posting',
                content_id=instance.pk,
                status='success',
                details={
                    'job_title': instance.title,
                    'seo_title_length': len(instance.seo_title or ''),
                    'description_length': len(instance.seo_description or ''),
                    'has_structured_data': bool(instance.structured_data),
                    'has_open_graph': bool(instance.open_graph_tags),
                    'generation_method': 'auto_signal'
                },
                processing_time=0.0,  # Would need to track actual time
                items_processed=1
            )
        
        # Update sitemap entry if needed
        _update_sitemap_entry(instance)
        
    except Exception as e:
        logger.error(f"Error in post-save SEO processing for job {instance.pk}: {e}")


def _prepare_job_data_for_seo(instance: JobPosting) -> Dict[str, Any]:
    """
    Prepare job posting data for SEO metadata generation.
    
    Args:
        instance: JobPosting instance
        
    Returns:
        Dictionary containing job data formatted for SEO engine
    """
    return {
        'id': instance.pk,
        'title': instance.title,
        'description': instance.description,
        'slug': instance.slug or slugify(instance.title),
        'department': instance.department,
        'qualification': instance.qualification,
        'total_posts': instance.total_posts,
        'min_age': instance.min_age,
        'max_age': instance.max_age,
        'salary_min': float(instance.salary_min) if instance.salary_min else None,
        'salary_max': float(instance.salary_max) if instance.salary_max else None,
        'application_fee': float(instance.application_fee) if instance.application_fee else None,
        'notification_date': instance.notification_date.isoformat() if instance.notification_date else None,
        'application_start_date': instance.application_start_date.isoformat() if instance.application_start_date else None,
        'last_date': instance.application_end_date.isoformat() if instance.application_end_date else None,
        'exam_date': instance.exam_date.isoformat() if instance.exam_date else None,
        'application_link': instance.application_link,
        'notification_pdf': instance.notification_pdf,
        'source_url': instance.source_url,
        'source_name': instance.source.name if instance.source else None,
        'category': instance.category.name if instance.category else None,
        'category_slug': instance.category.slug if instance.category else None,
        'status': instance.status,
        'posted_date': instance.published_at.isoformat() if instance.published_at else instance.created_at.isoformat(),
        'updated_at': instance.updated_at.isoformat() if instance.updated_at else None,
        'keywords': instance.keywords.split(', ') if instance.keywords else [],
    }


def _update_sitemap_entry(instance: JobPosting) -> None:
    """
    Update or create sitemap entry for the job posting.
    
    Args:
        instance: JobPosting instance
    """
    try:
        from apps.seo.models import SitemapEntry
        
        # Determine URL and priority based on job status and importance
        url = f"/jobs/{instance.slug}/"
        priority = 0.8  # Default priority for job postings
        
        # Increase priority for important jobs
        if instance.is_featured or (instance.total_posts and instance.total_posts > 100):
            priority = 0.9
        
        # Determine change frequency based on job status
        change_frequency = 'weekly'
        if instance.status == 'announced':
            change_frequency = 'daily'
        elif instance.status in ['admit_card', 'answer_key']:
            change_frequency = 'weekly'
        elif instance.status == 'result':
            change_frequency = 'monthly'
        
        # Update or create sitemap entry
        SitemapEntry.objects.update_or_create(
            url=url,
            defaults={
                'change_frequency': change_frequency,
                'priority': priority,
                'last_modified': timezone.now(),
                'is_active': instance.status in ['announced', 'admit_card', 'answer_key', 'result']
            }
        )
        
        logger.debug(f"Updated sitemap entry for job: {instance.title}")
        
    except Exception as e:
        logger.error(f"Error updating sitemap entry for job {instance.pk}: {e}")