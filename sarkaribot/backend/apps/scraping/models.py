"""
Models for tracking web scraping operations and results.

This module contains models that track scraping logs, scraped data,
and performance metrics for the scraping system.
"""

from django.db import models
from django.utils import timezone
from apps.core.models import TimestampedModel
from decimal import Decimal
import uuid
import logging

logger = logging.getLogger(__name__)


class ScrapeLog(TimestampedModel):
    """
    Tracks individual scraping operations.
    
    Records details about each scraping session including
    performance metrics, errors, and results.
    """
    
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    SCRAPER_ENGINE_CHOICES = [
        ('requests', 'Requests + BeautifulSoup'),
        ('playwright', 'Playwright Browser'),
        ('scrapy', 'Scrapy Framework'),
    ]
    
    # Unique identifier for this scrape session
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Related source
    source = models.ForeignKey(
        'sources.GovernmentSource',
        on_delete=models.CASCADE,
        related_name='scrape_logs'
    )
    
    # Task tracking
    task_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Timing information
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Status and configuration
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    scraper_engine = models.CharField(
        max_length=20, 
        choices=SCRAPER_ENGINE_CHOICES,
        null=True,
        blank=True
    )
    config_snapshot = models.JSONField(default=dict, help_text="Configuration used for this scrape")
    
    # Performance metrics
    pages_scraped = models.PositiveIntegerField(default=0)
    requests_made = models.PositiveIntegerField(default=0)
    average_response_time = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Average response time in seconds"
    )
    
    # Results
    jobs_found = models.PositiveIntegerField(default=0)
    jobs_created = models.PositiveIntegerField(default=0)
    jobs_updated = models.PositiveIntegerField(default=0)
    jobs_skipped = models.PositiveIntegerField(default=0)
    
    # Error information
    error_message = models.TextField(blank=True)
    error_count = models.PositiveIntegerField(default=0)
    warnings_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    user_agent = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['source', '-started_at']),
            models.Index(fields=['status', '-started_at']),
            models.Index(fields=['scraper_engine', '-started_at']),
            models.Index(fields=['-started_at']),
        ]
    
    def __str__(self) -> str:
        return f"Scrape {self.source.name} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"
    
    def mark_completed(self, jobs_stats: dict) -> None:
        """
        Mark the scrape as completed with final statistics.
        
        Args:
            jobs_stats: Dictionary containing job processing statistics
        """
        self.completed_at = timezone.now()
        self.status = 'completed'
        
        # Calculate duration
        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration_seconds = Decimal(str(duration.total_seconds()))
        
        # Update job statistics
        self.jobs_found = jobs_stats.get('found', 0)
        self.jobs_created = jobs_stats.get('created', 0)
        self.jobs_updated = jobs_stats.get('updated', 0)
        self.jobs_skipped = jobs_stats.get('skipped', 0)
        
        self.save()
    
    def mark_failed(self, error_message: str) -> None:
        """
        Mark the scrape as failed with error information.
        
        Args:
            error_message: Description of the error
        """
        self.completed_at = timezone.now()
        self.status = 'failed'
        self.error_message = error_message
        
        # Calculate duration
        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration_seconds = Decimal(str(duration.total_seconds()))
        
        self.save()
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate of processed items."""
        total_processed = self.jobs_created + self.jobs_updated + self.jobs_skipped
        if total_processed == 0:
            return 0.0
        return (self.jobs_created + self.jobs_updated) / total_processed * 100
    
    @property
    def is_running(self) -> bool:
        """Check if the scrape is currently running."""
        return self.status == 'running'
    
    @property
    def is_completed(self) -> bool:
        """Check if the scrape completed successfully."""
        return self.status == 'completed'
    
    @property
    def is_failed(self) -> bool:
        """Check if the scrape failed."""
        return self.status == 'failed'


class ScrapedData(TimestampedModel):
    """
    Stores individual scraped data items.
    
    Each record represents a single job posting or piece of
    information scraped from a government website.
    """
    
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Pending Processing'),
        ('processing', 'Being Processed'),
        ('processed', 'Successfully Processed'),
        ('skipped', 'Skipped (Duplicate)'),
        ('failed', 'Processing Failed'),
    ]
    
    # Unique identifier
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Related models
    source = models.ForeignKey(
        'sources.GovernmentSource',
        on_delete=models.CASCADE,
        related_name='scraped_data'
    )
    scrape_log = models.ForeignKey(
        ScrapeLog,
        on_delete=models.CASCADE,
        related_name='scraped_items'
    )
    job_posting = models.ForeignKey(
        'jobs.JobPosting',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scraped_data'
    )
    
    # Raw scraped data
    raw_data = models.JSONField(help_text="Raw scraped data as JSON")
    source_url = models.URLField(max_length=500)
    content_hash = models.CharField(
        max_length=32,
        help_text="Hash of the content for duplicate detection"
    )
    
    # Processing information
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default='pending'
    )
    processing_error = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Quality metrics
    data_quality_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Quality score from 0-100 based on data completeness"
    )
    field_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of non-empty fields in raw data"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['source', '-created_at']),
            models.Index(fields=['scrape_log', 'processing_status']),
            models.Index(fields=['content_hash']),
            models.Index(fields=['processing_status', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['source', 'content_hash'],
                name='unique_content_per_source'
            )
        ]
    
    def __str__(self) -> str:
        title = self.raw_data.get('title', 'Unknown') if self.raw_data else 'Unknown'
        return f"Scraped: {title[:50]}..."
    
    def mark_processed(self, job_posting) -> None:
        """
        Mark the scraped data as successfully processed.
        
        Args:
            job_posting: The JobPosting created from this data
        """
        self.processing_status = 'processed'
        self.processed_at = timezone.now()
        self.job_posting = job_posting
        self.save()
    
    def mark_failed(self, error_message: str) -> None:
        """
        Mark the scraped data as failed to process.
        
        Args:
            error_message: Description of the processing error
        """
        self.processing_status = 'failed'
        self.processing_error = error_message
        self.processed_at = timezone.now()
        self.save()
    
    def calculate_quality_score(self) -> float:
        """
        Calculate a quality score based on data completeness.
        
        Returns:
            Quality score from 0-100
        """
        if not self.raw_data:
            return 0.0
        
        # Define important fields and their weights
        field_weights = {
            'title': 20,
            'description': 15,
            'last_date': 15,
            'notification_date': 10,
            'posts': 10,
            'qualification': 10,
            'salary': 8,
            'age_limit': 7,
            'department': 5,
        }
        
        total_possible = sum(field_weights.values())
        earned_score = 0
        
        for field, weight in field_weights.items():
            if field in self.raw_data and self.raw_data[field]:
                # Check if the field has meaningful content
                value = str(self.raw_data[field]).strip()
                if len(value) > 3:  # Minimum meaningful length
                    earned_score += weight
        
        # Bonus points for additional fields
        additional_fields = len([k for k, v in self.raw_data.items() 
                               if k not in field_weights and v])
        bonus_score = min(additional_fields * 2, 10)  # Max 10 bonus points
        
        final_score = min((earned_score + bonus_score) / total_possible * 100, 100)
        
        # Update the score in the model
        self.data_quality_score = Decimal(str(round(final_score, 2)))
        self.field_count = len([v for v in self.raw_data.values() if v])
        
        return final_score
    
    @property
    def is_high_quality(self) -> bool:
        """Check if this scraped data is considered high quality."""
        if self.data_quality_score is None:
            self.calculate_quality_score()
        return self.data_quality_score >= 70
    
    @property
    def title(self) -> str:
        """Get the title from raw data."""
        if self.raw_data:
            return self.raw_data.get('title', 'No Title')
        return 'No Title'


class SourceStatistics(TimestampedModel):
    """
    Daily statistics for government sources.
    
    Tracks performance metrics and success rates for each
    source on a daily basis.
    """
    
    source = models.ForeignKey(
        'sources.GovernmentSource',
        on_delete=models.CASCADE,
        related_name='daily_statistics'
    )
    
    date = models.DateField()
    
    # Scraping statistics
    scrapes_attempted = models.PositiveIntegerField(default=0)
    scrapes_successful = models.PositiveIntegerField(default=0)
    scrapes_failed = models.PositiveIntegerField(default=0)
    
    # Job statistics
    jobs_found = models.PositiveIntegerField(default=0)
    jobs_created = models.PositiveIntegerField(default=0)
    jobs_updated = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    average_response_time = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True
    )
    total_pages_scraped = models.PositiveIntegerField(default=0)
    average_quality_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['source', 'date'],
                name='unique_source_date_stats'
            )
        ]
        indexes = [
            models.Index(fields=['source', '-date']),
            models.Index(fields=['-date']),
        ]
    
    def __str__(self) -> str:
        return f"{self.source.name} - {self.date}"
    
    @property
    def success_rate(self) -> float:
        """Calculate scraping success rate for the day."""
        if self.scrapes_attempted == 0:
            return 0.0
        return (self.scrapes_successful / self.scrapes_attempted) * 100
    
    @property
    def jobs_per_scrape(self) -> float:
        """Calculate average jobs found per successful scrape."""
        if self.scrapes_successful == 0:
            return 0.0
        return self.jobs_found / self.scrapes_successful
    
    @property
    def creation_rate(self) -> float:
        """Calculate percentage of found jobs that were new."""
        if self.jobs_found == 0:
            return 0.0
        return (self.jobs_created / self.jobs_found) * 100


class ScrapingError(TimestampedModel):
    """
    Tracks detailed error information from scraping operations.
    
    Helps in debugging and improving scraping reliability.
    """
    
    ERROR_TYPE_CHOICES = [
        ('network', 'Network Error'),
        ('parsing', 'Parsing Error'),
        ('validation', 'Data Validation Error'),
        ('timeout', 'Timeout Error'),
        ('auth', 'Authentication Error'),
        ('rate_limit', 'Rate Limiting Error'),
        ('javascript', 'JavaScript Execution Error'),
        ('other', 'Other Error'),
    ]
    
    # Related models
    scrape_log = models.ForeignKey(
        ScrapeLog,
        on_delete=models.CASCADE,
        related_name='errors'
    )
    
    # Error details
    error_type = models.CharField(max_length=20, choices=ERROR_TYPE_CHOICES)
    error_message = models.TextField()
    stack_trace = models.TextField(blank=True)
    
    # Context information
    url = models.URLField(max_length=500, blank=True)
    selector = models.CharField(max_length=500, blank=True)
    raw_html = models.TextField(blank=True, help_text="HTML content at time of error")
    
    # Error occurrence
    occurred_at = models.DateTimeField(auto_now_add=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Resolution tracking
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['scrape_log', '-occurred_at']),
            models.Index(fields=['error_type', '-occurred_at']),
            models.Index(fields=['resolved', '-occurred_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.error_type}: {self.error_message[:50]}..."


class ProxyConfiguration(TimestampedModel):
    """
    Proxy server configurations for web scraping.
    
    Manages proxy servers to avoid IP blocking
    and distribute scraping load.
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('disabled', 'Disabled'),
        ('blocked', 'Blocked'),
        ('testing', 'Testing'),
    ]
    
    TYPE_CHOICES = [
        ('http', 'HTTP'),
        ('https', 'HTTPS'),
        ('socks4', 'SOCKS4'),
        ('socks5', 'SOCKS5'),
    ]
    
    # Proxy Details
    host = models.CharField(
        max_length=255,
        help_text="Proxy server hostname or IP"
    )
    port = models.PositiveIntegerField(
        help_text="Proxy server port"
    )
    proxy_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='http'
    )
    
    # Authentication
    username = models.CharField(
        max_length=100,
        blank=True,
        help_text="Proxy username (if required)"
    )
    password = models.CharField(
        max_length=100,
        blank=True,
        help_text="Proxy password (if required)"
    )
    
    # Status and Performance
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='testing'
    )
    last_tested = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this proxy was tested"
    )
    success_rate = models.FloatField(
        default=0.0,
        help_text="Success rate percentage"
    )
    average_response_time = models.FloatField(
        default=0.0,
        help_text="Average response time in seconds"
    )
    
    # Usage Statistics
    requests_made = models.PositiveIntegerField(
        default=0,
        help_text="Total requests made through this proxy"
    )
    successful_requests = models.PositiveIntegerField(
        default=0,
        help_text="Successful requests"
    )
    failed_requests = models.PositiveIntegerField(
        default=0,
        help_text="Failed requests"
    )
    
    class Meta:
        unique_together = ['host', 'port']
        ordering = ['-success_rate', 'average_response_time']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['success_rate']),
        ]
        verbose_name = 'Proxy Configuration'
        verbose_name_plural = 'Proxy Configurations'
    
    def __str__(self) -> str:
        return f"{self.proxy_type.upper()}://{self.host}:{self.port}"
    
    @property
    def proxy_url(self) -> str:
        """Get the full proxy URL."""
        if self.username and self.password:
            return f"{self.proxy_type}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.proxy_type}://{self.host}:{self.port}"
    
    def update_stats(self, success: bool, response_time: float):
        """
        Update proxy statistics after a request.
        
        Args:
            success: Whether the request was successful
            response_time: Response time in seconds
        """
        self.requests_made += 1
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Calculate new success rate
        self.success_rate = (self.successful_requests / self.requests_made) * 100
        
        # Update average response time (exponential moving average)
        if self.average_response_time == 0:
            self.average_response_time = response_time
        else:
            self.average_response_time = (self.average_response_time * 0.9) + (response_time * 0.1)
        
        self.save(update_fields=[
            'requests_made', 'successful_requests', 'failed_requests',
            'success_rate', 'average_response_time'
        ])
