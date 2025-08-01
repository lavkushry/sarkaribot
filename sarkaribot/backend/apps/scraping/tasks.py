"""
Celery tasks for automated web scraping operations.

Implements background tasks for scheduled scraping,
job data processing, and maintenance operations.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from celery import shared_task
from celery.exceptions import Retry
from django.conf import settings
from django.utils import timezone
from django.db import transaction

# Internal imports
from .engine import scrape_source, scrape_all_active_sources
from .models import ScrapeLog, ScrapedData, SourceStatistics
from apps.sources.models import GovernmentSource
from apps.jobs.models import JobPosting, JobCategory
from apps.seo.engine import seo_engine

logger = logging.getLogger(__name__)
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def scrape_government_source(self, source_id: int) -> Dict[str, Any]:
    """
    Scrape a specific government source for job postings.
    
    Args:
        source_id: ID of the GovernmentSource to scrape
        
    Returns:
        Dictionary with scraping results
    """
    try:
        logger.info(f"Starting scraping task for source ID: {source_id}")
        
        # Perform the scraping
        result = scrape_source(source_id)
        
        if result['success']:
            # Process the scraped data
            processing_result = process_scraped_data.delay(result['scrape_log_id'])
            result['processing_task_id'] = processing_result.id
            
            logger.info(f"Scraping completed for source {source_id}: {result}")
        else:
            logger.error(f"Scraping failed for source {source_id}: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as exc:
        logger.error(f"Scraping task failed for source {source_id}: {str(exc)}")
        raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)


@shared_task
def scheduled_scraping() -> Dict[str, Any]:
    """
    Scheduled task to scrape all sources that are due for scraping.
    
    Returns:
        Dictionary with scheduling results
    """
    try:
        now = timezone.now()
        sources_to_scrape = []
        
        # Find sources that need scraping
        active_sources = GovernmentSource.objects.filter(active=True)
        
        for source in active_sources:
            if source.last_scraped is None:
                # Never scraped before
                sources_to_scrape.append(source)
            else:
                # Check if enough time has passed
                time_since_last_scrape = now - source.last_scraped
                scrape_interval = timedelta(hours=source.scrape_frequency)
                
                if time_since_last_scrape >= scrape_interval:
                    sources_to_scrape.append(source)
        
        # Schedule scraping tasks
        scheduled_tasks = []
        for source in sources_to_scrape:
            task = scrape_government_source.delay(source.id)
            scheduled_tasks.append({
                'source_id': source.id,
                'source_name': source.name,
                'task_id': task.id
            })
            
            logger.info(f"Scheduled scraping for source: {source.name}")
        
        return {
            'success': True,
            'scheduled_count': len(scheduled_tasks),
            'scheduled_tasks': scheduled_tasks
        }
        
    except Exception as e:
        error_msg = f"Scheduled scraping failed: {str(e)}"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}


@shared_task(bind=True, max_retries=3)
def scrape_single_source(self, source_id: int):
    """
    Scrape a specific government source for job postings.
    
    Args:
        source_id: ID of the GovernmentSource to scrape
        
    Returns:
        Dict with scraping results
    """
    from apps.sources.models import GovernmentSource
    from apps.scraping.models import ScrapeLog
    from apps.scraping.scrapers.base import ScraperFactory, DataProcessor
    from apps.core.utils import PerformanceMonitor
    
    source = None
    scrape_log = None
    
    try:
        # Get the source
        source = GovernmentSource.objects.get(id=source_id)
        
        with PerformanceMonitor(f"scrape_source_{source.name}") as monitor:
            logger.info(f"Starting scrape for source: {source.name}")
            
            # Create scrape log
            scrape_log = ScrapeLog.objects.create(
                source=source,
                task_id=self.request.id,
                started_at=timezone.now(),
                status='running',
                config_snapshot=source.get_scraping_config()
            )
            
            # Mark scraping started
            source.mark_scrape_started()
            
            # Create appropriate scraper
            scraper_config = source.get_scraping_config()
            scraper_config['base_url'] = source.base_url
            scraper = ScraperFactory.create_scraper(scraper_config)
            
            # Update scrape log with scraper type
            scrape_log.scraper_engine = scraper.__class__.__name__.lower().replace('scraper', '')
            scrape_log.save()
            
            # Perform scraping
            raw_data_list = scraper.scrape()
            
            # Update scrape log with scraping stats
            scraper_stats = scraper.get_stats()
            scrape_log.pages_scraped = scraper_stats.get('pages_scraped', 0)
            scrape_log.requests_made = scraper_stats.get('requests_made', 0)
            scrape_log.average_response_time = scraper_stats.get('average_response_time')
            scrape_log.save()
            
            # Process scraped data
            processor = DataProcessor()
            processing_results = process_scraped_data.delay(
                source_id, 
                scrape_log.id, 
                raw_data_list
            )
            
            # Wait for processing results
            processing_result = processing_results.get(timeout=180)  # 3 minutes
            
            # Update scrape log with final results
            jobs_stats = {
                'found': len(raw_data_list),
                'created': processing_result.get('jobs_created', 0),
                'updated': processing_result.get('jobs_updated', 0),
                'skipped': processing_result.get('jobs_skipped', 0)
            }
            
            scrape_log.mark_completed(jobs_stats)
            source.mark_scrape_completed(jobs_stats['found'])
            
            result = {
                'success': True,
                'source_name': source.name,
                'jobs_found': jobs_stats['found'],
                'jobs_created': jobs_stats['created'],
                'jobs_updated': jobs_stats['updated'],
                'jobs_skipped': jobs_stats['skipped'],
                'duration': monitor.duration,
                'scraper_type': scrape_log.scraper_engine
            }
            
            logger.info(f"Completed scraping {source.name}: {result}")
            return result
            
    except Exception as exc:
        error_message = str(exc)
        logger.error(f"Scraping failed for source {source_id}: {error_message}")
        
        if source:
            source.mark_scrape_error(error_message)
        
        if scrape_log:
            scrape_log.mark_failed(error_message)
        
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        else:
            return {
                'success': False,
                'source_id': source_id,
                'error': error_message
            }


@shared_task(bind=True, max_retries=2)
def process_scraped_data(self, source_id: int, scrape_log_id: int, raw_data_list: List[Dict[str, Any]]):
    """
    Process raw scraped data into job postings.
    
    Args:
        source_id: ID of the source
        scrape_log_id: ID of the scrape log
        raw_data_list: List of raw scraped data
        
    Returns:
        Dict with processing results
    """
    from apps.sources.models import GovernmentSource
    from apps.scraping.models import ScrapeLog, ScrapedData
    from apps.jobs.models import JobPosting, JobCategory
    from apps.scraping.scrapers.base import DataProcessor
    from apps.core.utils import generate_unique_slug
    import hashlib
    
    try:
        source = GovernmentSource.objects.get(id=source_id)
        scrape_log = ScrapeLog.objects.get(id=scrape_log_id)
        
        logger.info(f"Processing {len(raw_data_list)} scraped items for {source.name}")
        
        processor = DataProcessor()
        results = {
            'jobs_created': 0,
            'jobs_updated': 0,
            'jobs_skipped': 0,
            'errors': []
        }
        
        # Get default category (Latest Jobs)
        default_category, _ = JobCategory.objects.get_or_create(
            slug='latest-jobs',
            defaults={
                'name': 'Latest Jobs',
                'position': 1
            }
        )
        
        for raw_data in raw_data_list:
            try:
                # Process the raw data
                processed_data = processor.process_item(raw_data)
                
                # Create ScrapedData record
                scraped_data = ScrapedData.objects.create(
                    source=source,
                    scrape_log=scrape_log,
                    raw_data=raw_data,
                    source_url=processed_data.get('source_url', ''),
                    content_hash=processed_data.get('content_hash', ''),
                    processing_status='processing'
                )
                
                # Check for duplicates
                existing_job = JobPosting.objects.filter(
                    source=source,
                    title=processed_data.get('title', ''),
                    source_url=processed_data.get('source_url', '')
                ).first()
                
                if existing_job:
                    # Update existing job if content has changed
                    if existing_job.version != processed_data.get('content_hash'):
                        existing_job = update_job_posting(existing_job, processed_data)
                        scraped_data.mark_processed(existing_job)
                        results['jobs_updated'] += 1
                    else:
                        scraped_data.processing_status = 'skipped'
                        scraped_data.save()
                        results['jobs_skipped'] += 1
                else:
                    # Create new job posting
                    job_posting = create_job_posting(processed_data, source, default_category)
                    scraped_data.mark_processed(job_posting)
                    results['jobs_created'] += 1
                    
            except Exception as e:
                error_msg = f"Failed to process item: {e}"
                results['errors'].append(error_msg)
                logger.warning(error_msg)
                
                # Mark scraped data as failed
                if 'scraped_data' in locals():
                    scraped_data.mark_failed(error_msg)
        
        logger.info(f"Processing completed for {source.name}: {results}")
        return results
        
    except Exception as exc:
        logger.error(f"Data processing failed: {exc}")
        raise self.retry(countdown=30 * (self.request.retries + 1))


def create_job_posting(processed_data: Dict[str, Any], source, category) -> 'JobPosting':
    """
    Create a new job posting from processed data.
    
    Args:
        processed_data: Processed job data
        source: GovernmentSource instance
        category: JobCategory instance
        
    Returns:
        Created JobPosting instance
    """
    from apps.jobs.models import JobPosting
    from apps.core.utils import generate_unique_slug
    
    # Generate unique slug
    title = processed_data.get('title', '')
    slug = generate_unique_slug(title, JobPosting)
    
    # Create job posting
    job_posting = JobPosting.objects.create(
        title=title,
        description=processed_data.get('description', ''),
        source=source,
        category=category,
        slug=slug,
        
        # Job details
        department=processed_data.get('department', ''),
        total_posts=processed_data.get('total_posts'),
        qualification=processed_data.get('qualification', ''),
        
        # Dates
        notification_date=processed_data.get('notification_date'),
        application_end_date=processed_data.get('application_end_date'),
        exam_date=processed_data.get('exam_date'),
        
        # Financial info
        application_fee=processed_data.get('application_fee'),
        salary_min=processed_data.get('salary_min'),
        salary_max=processed_data.get('salary_max'),
        
        # Age limits
        min_age=processed_data.get('min_age'),
        max_age=processed_data.get('max_age'),
        
        # Links
        application_link=processed_data.get('application_link', ''),
        notification_pdf=processed_data.get('notification_pdf', ''),
        source_url=processed_data.get('source_url', ''),
        
        # Status
        status='announced',
        published_at=timezone.now()
    )
    
    logger.info(f"Created job posting: {job_posting.title}")
    return job_posting


def update_job_posting(job_posting, processed_data: Dict[str, Any]) -> 'JobPosting':
    """
    Update an existing job posting with new data.
    
    Args:
        job_posting: Existing JobPosting instance
        processed_data: New processed data
        
    Returns:
        Updated JobPosting instance
    """
    # Update fields that might have changed
    fields_to_update = [
        'description', 'department', 'total_posts', 'qualification',
        'application_end_date', 'exam_date', 'application_fee',
        'salary_min', 'salary_max', 'min_age', 'max_age',
        'application_link', 'notification_pdf'
    ]
    
    updated_fields = []
    for field in fields_to_update:
        new_value = processed_data.get(field)
        if new_value and getattr(job_posting, field) != new_value:
            setattr(job_posting, field, new_value)
            updated_fields.append(field)
    
    if updated_fields:
        job_posting.version += 1
        job_posting.save(update_fields=updated_fields + ['version'])
        logger.info(f"Updated job posting {job_posting.title}: {updated_fields}")
    
    return job_posting


@shared_task
def cleanup_old_scrape_logs():
    """
    Clean up old scrape logs to prevent database bloat.
    
    Removes scrape logs older than 30 days and related scraped data.
    """
    from apps.scraping.models import ScrapeLog, ScrapedData
    from datetime import timedelta
    
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # Delete old scraped data first (foreign key constraint)
        old_scraped_data = ScrapedData.objects.filter(created_at__lt=cutoff_date)
        scraped_data_count = old_scraped_data.count()
        old_scraped_data.delete()
        
        # Delete old scrape logs
        old_logs = ScrapeLog.objects.filter(started_at__lt=cutoff_date)
        logs_count = old_logs.count()
        old_logs.delete()
        
        logger.info(f"Cleaned up {logs_count} old scrape logs and {scraped_data_count} scraped data records")
        
        return {
            'scrape_logs_deleted': logs_count,
            'scraped_data_deleted': scraped_data_count
        }
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise


@shared_task
def update_source_statistics():
    """
    Update daily statistics for all government sources.
    
    This task should run daily to calculate and store performance
    metrics for each source.
    """
    from apps.sources.models import GovernmentSource, SourceStatistics
    from apps.scraping.models import ScrapeLog
    from datetime import date, timedelta
    from django.db.models import Count, Avg
    
    try:
        yesterday = date.today() - timedelta(days=1)
        
        sources = GovernmentSource.objects.all()
        stats_created = 0
        
        for source in sources:
            # Get scraping logs for yesterday
            logs = ScrapeLog.objects.filter(
                source=source,
                started_at__date=yesterday
            )
            
            if logs.exists():
                # Calculate statistics
                stats = logs.aggregate(
                    scrapes_attempted=Count('id'),
                    scrapes_successful=Count('id', filter=models.Q(status='completed')),
                    scrapes_failed=Count('id', filter=models.Q(status='failed')),
                    total_jobs_found=models.Sum('jobs_found'),
                    total_jobs_created=models.Sum('jobs_created'),
                    total_jobs_updated=models.Sum('jobs_updated'),
                    avg_response_time=Avg('average_response_time'),
                    total_pages=models.Sum('pages_scraped')
                )
                
                # Create or update statistics record
                source_stats, created = SourceStatistics.objects.get_or_create(
                    source=source,
                    date=yesterday,
                    defaults={
                        'scrapes_attempted': stats['scrapes_attempted'] or 0,
                        'scrapes_successful': stats['scrapes_successful'] or 0,
                        'scrapes_failed': stats['scrapes_failed'] or 0,
                        'jobs_found': stats['total_jobs_found'] or 0,
                        'jobs_updated': stats['total_jobs_updated'] or 0,
                        'average_response_time': stats['avg_response_time'],
                        'total_pages_scraped': stats['total_pages'] or 0
                    }
                )
                
                if created:
                    stats_created += 1
        
        logger.info(f"Updated statistics for {stats_created} sources")
        return {'statistics_created': stats_created}
        
    except Exception as e:
        logger.error(f"Statistics update failed: {e}")
        raise


@shared_task
def test_source_configuration(source_id: int):
    """
    Test scraping configuration for a source without saving data.
    
    Args:
        source_id: ID of the source to test
        
    Returns:
        Dict with test results
    """
    from apps.sources.models import GovernmentSource
    from apps.scraping.scrapers.base import ScraperFactory
    
    try:
        source = GovernmentSource.objects.get(id=source_id)
        
        logger.info(f"Testing configuration for source: {source.name}")
        
        # Create scraper with test configuration
        scraper_config = source.get_scraping_config()
        scraper_config['base_url'] = source.base_url
        scraper_config['max_pages'] = 1  # Limit to one page for testing
        
        scraper = ScraperFactory.create_scraper(scraper_config)
        
        # Perform test scraping
        raw_data_list = scraper.scrape()
        
        # Get statistics
        stats = scraper.get_stats()
        
        result = {
            'success': True,
            'source_name': source.name,
            'scraper_type': scraper.__class__.__name__,
            'items_found': len(raw_data_list),
            'pages_scraped': stats.get('pages_scraped', 0),
            'requests_made': stats.get('requests_made', 0),
            'errors': stats.get('errors', 0),
            'sample_data': raw_data_list[:3] if raw_data_list else []  # First 3 items
        }
        
        logger.info(f"Test completed for {source.name}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Configuration test failed for source {source_id}: {e}")
        return {
            'success': False,
            'source_id': source_id,
            'error': str(e)
        }
