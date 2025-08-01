"""
Government source models for SarkariBot.

This module contains models for managing government websites
that will be scraped for job postings.
"""

from django.db import models
from django.core.validators import URLValidator
from django.utils import timezone
from apps.core.models import TimestampedModel
import logging

logger = logging.getLogger(__name__)


class GovernmentSource(TimestampedModel):
    """
    Model representing a government website source for job postings.
    
    Each source represents a different government department or agency
    website that publishes job notifications.
    """
    
    SCRAPE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('error', 'Error'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    # Basic Information
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Short name for the government source (e.g., 'SSC', 'UPSC')"
    )
    display_name = models.CharField(
        max_length=200,
        help_text="Full display name (e.g., 'Staff Selection Commission')"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the government department/agency"
    )
    
    # Website Configuration
    base_url = models.URLField(
        validators=[URLValidator()],
        help_text="Base URL of the government website"
    )
    logo_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to the official logo"
    )
    
    # Scraping Configuration
    active = models.BooleanField(
        default=True,
        help_text="Whether this source should be actively scraped"
    )
    scrape_frequency = models.PositiveIntegerField(
        default=24,
        help_text="Scraping frequency in hours"
    )
    status = models.CharField(
        max_length=20,
        choices=SCRAPE_STATUS_CHOICES,
        default='active',
        help_text="Current scraping status"
    )
    
    # Scraping Metadata
    last_scraped = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this source was successfully scraped"
    )
    last_error = models.TextField(
        blank=True,
        help_text="Last error message encountered during scraping"
    )
    total_jobs_found = models.PositiveIntegerField(
        default=0,
        help_text="Total number of jobs found from this source"
    )
    
    # Configuration JSON for scraping engine
    config_json = models.JSONField(
        default=dict,
        help_text="JSON configuration for scraping this source"
    )
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['active', 'status']),
            models.Index(fields=['last_scraped']),
        ]
        verbose_name = 'Government Source'
        verbose_name_plural = 'Government Sources'
    
    def __str__(self) -> str:
        return f"{self.display_name} ({self.name})"
    
    def is_due_for_scraping(self) -> bool:
        """
        Check if this source is due for scraping based on frequency.
        
        Returns:
            True if source should be scraped now, False otherwise
        """
        if not self.active or self.status != 'active':
            return False
        
        if not self.last_scraped:
            return True
        
        time_since_last_scrape = timezone.now() - self.last_scraped
        return time_since_last_scrape.total_seconds() >= (self.scrape_frequency * 3600)
    
    def mark_scrape_started(self):
        """Mark that scraping has started for this source."""
        self.status = 'active'
        self.last_error = ''
        self.save(update_fields=['status', 'last_error'])
        logger.info(f"Started scraping {self.name}")
    
    def mark_scrape_completed(self, jobs_found: int = 0):
        """
        Mark that scraping has completed successfully.
        
        Args:
            jobs_found: Number of jobs found in this scrape
        """
        self.last_scraped = timezone.now()
        self.status = 'active'
        self.last_error = ''
        self.total_jobs_found += jobs_found
        self.save(update_fields=['last_scraped', 'status', 'last_error', 'total_jobs_found'])
        logger.info(f"Completed scraping {self.name}: {jobs_found} jobs found")
    
    def mark_scrape_error(self, error_message: str):
        """
        Mark that scraping encountered an error.
        
        Args:
            error_message: Error message to store
        """
        self.status = 'error'
        self.last_error = error_message
        self.save(update_fields=['status', 'last_error'])
        logger.error(f"Scraping error for {self.name}: {error_message}")
    
    def get_scraping_config(self) -> dict:
        """
        Get the scraping configuration for this source.
        
        Returns:
            Dictionary containing scraping configuration
        """
        default_config = {
            'selectors': {},
            'pagination': {},
            'request_delay': 2,
            'max_pages': 5,
            'timeout': 30,
            'user_agent_rotation': True,
            'use_headless_browser': False,
        }
        
        if self.config_json:
            default_config.update(self.config_json)
        
        return default_config
    
    def get_jobs_count_last_30_days(self) -> int:
        """Get number of jobs found from this source in last 30 days."""
        from datetime import timedelta
        from apps.jobs.models import JobPosting
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return JobPosting.objects.filter(
            source=self,
            created_at__gte=thirty_days_ago
        ).count()
    
    def get_success_rate_last_30_days(self) -> float:
        """Get success rate for scraping in last 30 days."""
        from datetime import timedelta
        
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        stats = self.statistics.filter(date__gte=thirty_days_ago)
        
        total_attempts = sum(s.scrapes_attempted for s in stats)
        total_successful = sum(s.scrapes_successful for s in stats)
        
        if total_attempts == 0:
            return 0.0
        return (total_successful / total_attempts) * 100
    
    def get_avg_jobs_per_scrape(self) -> float:
        """Get average number of jobs found per scrape."""
        from datetime import timedelta
        
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        stats = self.statistics.filter(date__gte=thirty_days_ago)
        
        total_scrapes = sum(s.scrapes_successful for s in stats)
        total_jobs = sum(s.jobs_found for s in stats)
        
        if total_scrapes == 0:
            return 0.0
        return total_jobs / total_scrapes
    
    def last_successful_scrape_time(self):
        """Get the last successful scrape time."""
        return self.last_scraped


class SourceCategory(TimestampedModel):
    """
    Categories for organizing government sources.
    
    Examples: Central Government, State Government, PSU, etc.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly slug"
    )
    description = models.TextField(
        blank=True,
        help_text="Category description"
    )
    position = models.PositiveIntegerField(
        default=0,
        help_text="Display order position"
    )
    
    class Meta:
        ordering = ['position', 'name']
        verbose_name = 'Source Category'
        verbose_name_plural = 'Source Categories'
    
    def __str__(self) -> str:
        return self.name


class SourceStatistics(TimestampedModel):
    """
    Daily statistics for government sources.
    
    Tracks scraping performance and job discovery metrics.
    """
    
    source = models.ForeignKey(
        GovernmentSource,
        on_delete=models.CASCADE,
        related_name='statistics'
    )
    date = models.DateField(
        help_text="Date for these statistics"
    )
    
    # Scraping metrics
    scrapes_attempted = models.PositiveIntegerField(
        default=0,
        help_text="Number of scrape attempts"
    )
    scrapes_successful = models.PositiveIntegerField(
        default=0,
        help_text="Number of successful scrapes"
    )
    scrapes_failed = models.PositiveIntegerField(
        default=0,
        help_text="Number of failed scrapes"
    )
    
    # Job discovery metrics
    jobs_found = models.PositiveIntegerField(
        default=0,
        help_text="New jobs found"
    )
    jobs_updated = models.PositiveIntegerField(
        default=0,
        help_text="Existing jobs updated"
    )
    
    # Performance metrics
    average_response_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Average response time in seconds"
    )
    total_pages_scraped = models.PositiveIntegerField(
        default=0,
        help_text="Total pages scraped"
    )
    
    class Meta:
        unique_together = ['source', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['source', 'date']),
            models.Index(fields=['date']),
        ]
        verbose_name = 'Source Statistics'
        verbose_name_plural = 'Source Statistics'
    
    def __str__(self) -> str:
        return f"{self.source.name} - {self.date}"
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate for scraping attempts."""
        if self.scrapes_attempted == 0:
            return 0.0
        return (self.scrapes_successful / self.scrapes_attempted) * 100
