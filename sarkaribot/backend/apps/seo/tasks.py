"""
Celery tasks for SEO automation.

This module contains background tasks for generating and updating
SEO metadata for job postings using NLP and automation.
"""

from celery import shared_task
from django.utils import timezone
from typing import Dict, List, Any, Optional
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def generate_seo_metadata(self, job_posting_id: int, force_update: bool = False):
    """
    Generate SEO metadata for a single job posting.
    
    Args:
        job_posting_id: ID of the job posting
        force_update: Whether to force update existing metadata
        
    Returns:
        Dict with generation results
    """
    from apps.jobs.models import JobPosting
    from apps.seo.engine import seo_engine
    
    try:
        # Get the job posting
        job_posting = JobPosting.objects.get(id=job_posting_id)
        
        # Check if metadata already exists and force_update is False
        if (job_posting.seo_title and job_posting.seo_description and 
            job_posting.keywords and not force_update):
            logger.info(f"SEO metadata already exists for job {job_posting_id}, skipping")
            return {
                'success': True,
                'job_id': job_posting_id,
                'action': 'skipped',
                'reason': 'metadata_exists'
            }
        
        # Initialize SEO engine - using the global instance
        # seo_engine is already initialized
        
        # Prepare job data for SEO generation
        job_data = {
            'id': job_posting.id,
            'title': job_posting.title,
            'description': job_posting.description,
            'department': job_posting.department,
            'total_posts': job_posting.total_posts,
            'qualification': job_posting.qualification,
            'notification_date': job_posting.notification_date,
            'application_end_date': job_posting.application_end_date,
            'exam_date': job_posting.exam_date,
            'salary_min': job_posting.salary_min,
            'salary_max': job_posting.salary_max,
            'min_age': job_posting.min_age,
            'max_age': job_posting.max_age,
            'location': job_posting.location,
            'source_url': job_posting.source_url,
            'application_link': job_posting.application_link,
            'slug': job_posting.slug,
            'category': {
                'name': job_posting.category.name if job_posting.category else None,
                'slug': job_posting.category.slug if job_posting.category else None,
            },
            'source': {
                'base_url': job_posting.source.base_url if job_posting.source else '',
            }
        }
        
        # Generate SEO metadata
        logger.info(f"Generating SEO metadata for job: {job_posting.title}")
        seo_metadata = seo_engine.generate_seo_metadata(job_data)
        
        # Update job posting with SEO metadata
        job_posting.seo_title = seo_metadata.get('seo_title', '')
        job_posting.seo_description = seo_metadata.get('seo_description', '')
        job_posting.keywords = ', '.join(seo_metadata.get('keywords', []))
        job_posting.structured_data = seo_metadata.get('structured_data', {})
        job_posting.meta_tags = seo_metadata.get('meta_tags', {})
        job_posting.open_graph_tags = seo_metadata.get('open_graph_tags', {})
        job_posting.canonical_url = seo_metadata.get('canonical_url', '')
        job_posting.breadcrumbs = seo_metadata.get('breadcrumbs', [])
        job_posting.seo_updated_at = timezone.now()
        
        job_posting.save(update_fields=[
            'seo_title', 'seo_description', 'keywords', 'structured_data',
            'meta_tags', 'open_graph_tags', 'canonical_url', 'breadcrumbs',
            'seo_updated_at'
        ])
        
        logger.info(f"SEO metadata generated successfully for job {job_posting_id}")
        
        return {
            'success': True,
            'job_id': job_posting_id,
            'action': 'updated',
            'seo_title_length': len(seo_metadata.get('seo_title', '')),
            'seo_description_length': len(seo_metadata.get('seo_description', '')),
            'keywords_count': len(seo_metadata.get('keywords', [])),
            'has_structured_data': bool(seo_metadata.get('structured_data')),
        }
        
    except JobPosting.DoesNotExist:
        logger.error(f"Job posting {job_posting_id} not found")
        return {
            'success': False,
            'job_id': job_posting_id,
            'error': 'job_not_found'
        }
        
    except Exception as exc:
        logger.error(f"SEO metadata generation failed for job {job_posting_id}: {exc}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        else:
            return {
                'success': False,
                'job_id': job_posting_id,
                'error': str(exc)
            }


@shared_task(bind=True)
def bulk_generate_seo_metadata(self, job_ids: List[int] = None, category_slug: str = None, 
                              days_back: int = None, force_update: bool = False):
    """
    Generate SEO metadata for multiple job postings.
    
    Args:
        job_ids: List of specific job IDs to process
        category_slug: Process jobs from specific category
        days_back: Process jobs from last N days
        force_update: Whether to force update existing metadata
        
    Returns:
        Dict with bulk processing results
    """
    from apps.jobs.models import JobPosting, JobCategory
    from datetime import timedelta
    
    try:
        # Build queryset based on parameters
        if job_ids:
            queryset = JobPosting.objects.filter(id__in=job_ids)
        elif category_slug:
            category = JobCategory.objects.get(slug=category_slug)
            queryset = JobPosting.objects.filter(category=category)
        elif days_back:
            cutoff_date = timezone.now() - timedelta(days=days_back)
            queryset = JobPosting.objects.filter(created_at__gte=cutoff_date)
        else:
            # Process jobs without SEO metadata
            queryset = JobPosting.objects.filter(
                models.Q(seo_title__isnull=True) | 
                models.Q(seo_title='') |
                models.Q(seo_description__isnull=True) |
                models.Q(seo_description='')
            )
        
        # Filter active jobs only
        queryset = queryset.filter(status__in=['announced', 'admit_card', 'answer_key', 'result'])
        
        total_jobs = queryset.count()
        logger.info(f"Starting bulk SEO metadata generation for {total_jobs} jobs")
        
        if total_jobs == 0:
            return {
                'success': True,
                'total_jobs': 0,
                'processed': 0,
                'skipped': 0,
                'failed': 0,
                'message': 'No jobs found to process'
            }
        
        # Process jobs in batches to avoid memory issues
        batch_size = 50
        processed = 0
        skipped = 0
        failed = 0
        
        for i in range(0, total_jobs, batch_size):
            batch = queryset[i:i + batch_size]
            
            for job in batch:
                try:
                    # Check if update needed
                    if (job.seo_title and job.seo_description and 
                        job.keywords and not force_update):
                        skipped += 1
                        continue
                    
                    # Generate metadata asynchronously
                    result = generate_seo_metadata.delay(job.id, force_update)
                    
                    # For bulk operations, we don't wait for individual results
                    # The tasks will run in background
                    processed += 1
                    
                except Exception as e:
                    logger.error(f"Failed to queue SEO generation for job {job.id}: {e}")
                    failed += 1
        
        logger.info(f"Bulk SEO generation queued: {processed} processed, "
                   f"{skipped} skipped, {failed} failed")
        
        return {
            'success': True,
            'total_jobs': total_jobs,
            'processed': processed,
            'skipped': skipped,
            'failed': failed,
        }
        
    except Exception as exc:
        logger.error(f"Bulk SEO metadata generation failed: {exc}")
        raise


@shared_task
def update_outdated_seo_metadata():
    """
    Update SEO metadata for job postings that haven't been updated recently.
    
    This task runs daily to keep SEO metadata fresh and up-to-date.
    """
    from apps.jobs.models import JobPosting
    from django.db import models
    
    try:
        # Find jobs with outdated SEO metadata (older than 30 days)
        cutoff_date = timezone.now() - timedelta(days=30)
        
        outdated_jobs = JobPosting.objects.filter(
            models.Q(seo_updated_at__lt=cutoff_date) |
            models.Q(seo_updated_at__isnull=True),
            status__in=['announced', 'admit_card', 'answer_key', 'result']
        ).order_by('-created_at')[:100]  # Limit to 100 jobs per run
        
        logger.info(f"Found {outdated_jobs.count()} jobs with outdated SEO metadata")
        
        if not outdated_jobs.exists():
            return {
                'success': True,
                'updated': 0,
                'message': 'No outdated SEO metadata found'
            }
        
        # Queue SEO generation for outdated jobs
        updated_count = 0
        for job in outdated_jobs:
            try:
                generate_seo_metadata.delay(job.id, force_update=True)
                updated_count += 1
            except Exception as e:
                logger.error(f"Failed to queue SEO update for job {job.id}: {e}")
        
        logger.info(f"Queued SEO updates for {updated_count} jobs")
        
        return {
            'success': True,
            'updated': updated_count,
        }
        
    except Exception as e:
        logger.error(f"Failed to update outdated SEO metadata: {e}")
        raise


@shared_task
def generate_sitemap_data():
    """
    Generate sitemap data for all active job postings.
    
    This task runs daily to update the sitemap with fresh URLs.
    """
    from apps.jobs.models import JobPosting
    from django.conf import settings
    import os
    
    try:
        # Get all active job postings
        active_jobs = JobPosting.objects.filter(
            status__in=['announced', 'admit_card', 'answer_key', 'result'],
            published_at__isnull=False
        ).order_by('-created_at')
        
        logger.info(f"Generating sitemap for {active_jobs.count()} active jobs")
        
        sitemap_entries = []
        
        for job in active_jobs:
            entry = {
                'url': f"https://sarkaribot.com/jobs/{job.slug}",
                'lastmod': job.updated_at.strftime('%Y-%m-%d'),
                'changefreq': 'weekly',
                'priority': '0.8'
            }
            sitemap_entries.append(entry)
        
        # Generate XML sitemap
        sitemap_xml = generate_sitemap_xml(sitemap_entries)
        
        # Save sitemap to file
        sitemap_path = os.path.join(settings.STATIC_ROOT or 'static', 'sitemap.xml')
        os.makedirs(os.path.dirname(sitemap_path), exist_ok=True)
        
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_xml)
        
        logger.info(f"Sitemap generated with {len(sitemap_entries)} URLs")
        
        return {
            'success': True,
            'urls_count': len(sitemap_entries),
            'sitemap_path': sitemap_path
        }
        
    except Exception as e:
        logger.error(f"Sitemap generation failed: {e}")
        raise


def generate_sitemap_xml(entries: List[Dict[str, str]]) -> str:
    """
    Generate XML sitemap from entries.
    
    Args:
        entries: List of sitemap entry dictionaries
        
    Returns:
        XML sitemap as string
    """
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    for entry in entries:
        xml_lines.extend([
            '  <url>',
            f'    <loc>{entry["url"]}</loc>',
            f'    <lastmod>{entry["lastmod"]}</lastmod>',
            f'    <changefreq>{entry["changefreq"]}</changefreq>',
            f'    <priority>{entry["priority"]}</priority>',
            '  </url>'
        ])
    
    xml_lines.append('</urlset>')
    
    return '\n'.join(xml_lines)


@shared_task
def analyze_seo_performance():
    """
    Analyze SEO performance metrics for job postings.
    
    This task runs weekly to generate SEO performance reports.
    """
    from apps.jobs.models import JobPosting
    from django.db import models
    
    try:
        # Get all active jobs with SEO metadata
        jobs_with_seo = JobPosting.objects.filter(
            status__in=['announced', 'admit_card', 'answer_key', 'result'],
            seo_title__isnull=False,
            seo_description__isnull=False
        ).exclude(
            seo_title='',
            seo_description=''
        )
        
        total_jobs = JobPosting.objects.filter(
            status__in=['announced', 'admit_card', 'answer_key', 'result']
        ).count()
        
        # Calculate metrics
        coverage_rate = (jobs_with_seo.count() / total_jobs * 100) if total_jobs > 0 else 0
        
        # Analyze title lengths
        titles_optimal = jobs_with_seo.filter(
            seo_title__regex=r'^.{40,60}$'
        ).count()
        
        # Analyze description lengths
        descriptions_optimal = jobs_with_seo.filter(
            seo_description__regex=r'^.{140,160}$'
        ).count()
        
        # Jobs with keywords
        jobs_with_keywords = jobs_with_seo.exclude(
            models.Q(keywords__isnull=True) | models.Q(keywords='')
        ).count()
        
        # Jobs with structured data
        jobs_with_structured_data = jobs_with_seo.exclude(
            structured_data__isnull=True
        ).count()
        
        metrics = {
            'total_jobs': total_jobs,
            'jobs_with_seo': jobs_with_seo.count(),
            'coverage_rate': round(coverage_rate, 2),
            'titles_optimal_length': titles_optimal,
            'descriptions_optimal_length': descriptions_optimal,
            'jobs_with_keywords': jobs_with_keywords,
            'jobs_with_structured_data': jobs_with_structured_data,
            'analysis_date': timezone.now().isoformat(),
        }
        
        logger.info(f"SEO performance analysis completed: {metrics}")
        
        # Store metrics (you could save to a SEOMetrics model)
        return {
            'success': True,
            'metrics': metrics
        }
        
    except Exception as e:
        logger.error(f"SEO performance analysis failed: {e}")
        raise


@shared_task
def optimize_existing_metadata():
    """
    Optimize existing SEO metadata based on performance data.
    
    This task identifies and improves poorly performing SEO metadata.
    """
    from apps.jobs.models import JobPosting
    from apps.seo.engine import seo_engine
    
    try:
        # Find jobs with suboptimal SEO metadata
        suboptimal_jobs = JobPosting.objects.filter(
            status__in=['announced', 'admit_card', 'answer_key', 'result'],
            models.Q(seo_title__regex=r'^.{0,39}$') |  # Title too short
            models.Q(seo_title__regex=r'^.{61,}$') |   # Title too long
            models.Q(seo_description__regex=r'^.{0,139}$') |  # Description too short
            models.Q(seo_description__regex=r'^.{161,}$') |   # Description too long
            models.Q(keywords__isnull=True) |
            models.Q(keywords='')
        )[:50]  # Limit to 50 jobs per run
        
        logger.info(f"Found {suboptimal_jobs.count()} jobs with suboptimal SEO metadata")
        
        optimized_count = 0
        
        for job in suboptimal_jobs:
            try:
                # Regenerate SEO metadata with optimization
                generate_seo_metadata.delay(job.id, force_update=True)
                optimized_count += 1
            except Exception as e:
                logger.error(f"Failed to queue SEO optimization for job {job.id}: {e}")
        
        logger.info(f"Queued SEO optimization for {optimized_count} jobs")
        
        return {
            'success': True,
            'optimized': optimized_count
        }
        
    except Exception as e:
        logger.error(f"SEO optimization failed: {e}")
        raise
