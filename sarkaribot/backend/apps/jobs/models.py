"""
Job posting models for SarkariBot.

This module contains the core models for managing government job postings
and their lifecycle states.
"""

from django.db import models
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify
from apps.core.models import TimestampedModel
from apps.core.utils import generate_unique_slug, clean_html_text
import logging

logger = logging.getLogger(__name__)


class JobCategory(TimestampedModel):
    """
    Categories for job postings based on lifecycle stage.
    
    Examples: Latest Jobs, Admit Card, Answer Key, Result
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., 'Latest Jobs', 'Admit Card')"
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
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is active"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Icon class name for display"
    )
    
    class Meta:
        ordering = ['position', 'name']
        verbose_name = 'Job Category'
        verbose_name_plural = 'Job Categories'
    
    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = generate_unique_slug(self.name, JobCategory)
        super().save(*args, **kwargs)


class JobPosting(TimestampedModel):
    """
    Core model for government job postings.
    
    Represents a single job posting with all its details,
    SEO metadata, and lifecycle state.
    """
    
    STATUS_CHOICES = [
        ('announced', 'Latest Job'),
        ('admit_card', 'Admit Card'),
        ('answer_key', 'Answer Key'),
        ('result', 'Result'),
        ('archived', 'Archived'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Core Job Information
    title = models.CharField(
        max_length=255,
        help_text="Job posting title"
    )
    description = models.TextField(
        help_text="Detailed job description"
    )
    short_description = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief summary for listings"
    )
    
    # Relationships
    source = models.ForeignKey(
        'sources.GovernmentSource',
        on_delete=models.CASCADE,
        related_name='job_postings',
        help_text="Government source that published this job"
    )
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.CASCADE,
        related_name='job_postings',
        help_text="Current lifecycle category"
    )
    
    # Job Details
    department = models.CharField(
        max_length=200,
        blank=True,
        help_text="Government department/ministry"
    )
    total_posts = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Total number of available positions"
    )
    
    # Eligibility
    min_age = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(16), MaxValueValidator(70)],
        help_text="Minimum age requirement"
    )
    max_age = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(16), MaxValueValidator(70)],
        help_text="Maximum age requirement"
    )
    qualification = models.TextField(
        blank=True,
        help_text="Educational qualification requirements"
    )
    
    # Location Information
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Job location/posting location"
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        help_text="State where job is available"
    )
    
    # Important Dates
    notification_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when notification was published"
    )
    application_start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Application start date"
    )
    application_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Application deadline"
    )
    exam_date = models.DateField(
        null=True,
        blank=True,
        help_text="Examination date"
    )
    
    # Financial Information
    application_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Application fee amount"
    )
    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum salary/pay scale"
    )
    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum salary/pay scale"
    )
    
    # Links and Documents
    application_link = models.URLField(
        blank=True,
        validators=[URLValidator()],
        help_text="Direct application link"
    )
    notification_pdf = models.URLField(
        blank=True,
        validators=[URLValidator()],
        help_text="Official notification PDF link"
    )
    source_url = models.URLField(
        validators=[URLValidator()],
        help_text="Original source URL"
    )
    
    # Status and Lifecycle
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='announced',
        help_text="Current lifecycle status"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal',
        help_text="Display priority"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether this job should be featured"
    )
    
    # SEO and URL Management
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="URL-friendly slug"
    )
    seo_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="SEO optimized title"
    )
    seo_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="SEO meta description"
    )
    keywords = models.TextField(
        blank=True,
        help_text="Comma-separated keywords for SEO"
    )
    structured_data = models.JSONField(
        default=dict,
        help_text="JSON-LD structured data for search engines"
    )
    
    # Additional SEO fields
    canonical_url = models.URLField(
        blank=True,
        help_text="Canonical URL for SEO"
    )
    meta_tags = models.JSONField(
        default=dict,
        help_text="Additional meta tags"
    )
    open_graph_tags = models.JSONField(
        default=dict,
        help_text="Open Graph tags for social media"
    )
    breadcrumbs = models.JSONField(
        default=list,
        help_text="Breadcrumb navigation data"
    )
    
    # Metadata
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of page views"
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text="Version number for tracking updates"
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the job was published to the portal"
    )
    indexed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the job was indexed by search engines"
    )
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['source', 'status']),
            models.Index(fields=['category', 'status', '-published_at']),
            models.Index(fields=['application_end_date']),
            models.Index(fields=['is_featured', 'priority', '-published_at']),
        ]
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
    
    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        """Auto-generate slug and SEO metadata if not provided."""
        if not self.slug:
            self.slug = generate_unique_slug(self.title, JobPosting)
        
        # Auto-generate short description if not provided
        if not self.short_description and self.description:
            self.short_description = clean_html_text(self.description)[:500]
        
        # Set published_at for new jobs
        if not self.pk and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_application_open(self) -> bool:
        """Check if applications are currently open."""
        today = timezone.now().date()
        
        if self.application_end_date:
            return today <= self.application_end_date
        
        return self.status == 'announced'
    
    @property
    def days_remaining(self) -> int:
        """Calculate days remaining for application."""
        if not self.application_end_date:
            return 0
        
        today = timezone.now().date()
        if self.application_end_date >= today:
            return (self.application_end_date - today).days
        
        return 0
    
    @property
    def is_urgent(self) -> bool:
        """Check if this job posting is urgent (deadline approaching)."""
        return self.days_remaining <= 7 and self.days_remaining > 0
    
    def increment_view_count(self):
        """Increment the view count for this job posting."""
        JobPosting.objects.filter(pk=self.pk).update(view_count=models.F('view_count') + 1)
    
    def update_status(self, new_status: str, save: bool = True):
        """
        Update the job status and category.
        
        Args:
            new_status: New status from STATUS_CHOICES
            save: Whether to save the model immediately
        """
        if new_status not in dict(self.STATUS_CHOICES):
            raise ValueError(f"Invalid status: {new_status}")
        
        self.status = new_status
        self.version += 1
        
        # Update category based on status
        try:
            category = JobCategory.objects.get(slug=new_status.replace('_', '-'))
            self.category = category
        except JobCategory.DoesNotExist:
            logger.warning(f"Category not found for status: {new_status}")
        
        if save:
            self.save(update_fields=['status', 'category', 'version'])
        
        logger.info(f"Updated job {self.pk} status to {new_status}")


class JobMilestone(TimestampedModel):
    """
    Track important milestones in a job's lifecycle.
    
    Records key events like admit card release, result publication, etc.
    """
    
    MILESTONE_TYPES = [
        ('notification', 'Notification Published'),
        ('application_start', 'Applications Started'),
        ('application_end', 'Applications Closed'),
        ('admit_card', 'Admit Card Released'),
        ('exam_conducted', 'Exam Conducted'),
        ('answer_key', 'Answer Key Released'),
        ('result', 'Result Published'),
        ('interview', 'Interview Scheduled'),
        ('final_result', 'Final Result'),
        ('document_verification', 'Document Verification'),
    ]
    
    job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='milestones'
    )
    milestone_type = models.CharField(
        max_length=30,
        choices=MILESTONE_TYPES,
        help_text="Type of milestone"
    )
    milestone_date = models.DateField(
        help_text="Date when this milestone occurred"
    )
    title = models.CharField(
        max_length=200,
        help_text="Milestone title"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the milestone"
    )
    asset_url = models.URLField(
        blank=True,
        validators=[URLValidator()],
        help_text="URL to related document/asset"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this milestone is currently active"
    )
    
    class Meta:
        ordering = ['-milestone_date', '-created_at']
        indexes = [
            models.Index(fields=['job_posting', 'milestone_date']),
            models.Index(fields=['milestone_type']),
        ]
        verbose_name = 'Job Milestone'
        verbose_name_plural = 'Job Milestones'
    
    def __str__(self) -> str:
        return f"{self.job_posting.title} - {self.get_milestone_type_display()}"


class JobView(TimestampedModel):
    """
    Track job posting views for analytics.
    
    Records individual page views with metadata for analysis.
    """
    
    job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='views'
    )
    ip_address = models.GenericIPAddressField(
        help_text="Visitor IP address"
    )
    user_agent = models.TextField(
        help_text="Browser user agent string"
    )
    referrer = models.URLField(
        blank=True,
        null=True,
        help_text="Referrer URL"
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        help_text="Session identifier"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job_posting', 'created_at']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'Job View'
        verbose_name_plural = 'Job Views'
    
    def __str__(self) -> str:
        return f"{self.job_posting.title} - {self.created_at}"
