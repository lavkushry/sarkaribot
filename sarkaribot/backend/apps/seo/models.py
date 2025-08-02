"""
SEO automation models for SarkariBot.

Implements NLP-powered metadata generation, sitemap management,
and structured data handling for government job postings.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from apps.core.models import TimestampedModel
import uuid


class SitemapEntry(TimestampedModel):
    """
    Tracks sitemap entries for dynamic generation.
    """
    url = models.URLField(unique=True, help_text="Full URL of the page")
    change_frequency = models.CharField(
        max_length=20,
        choices=[
            ('always', 'Always'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
            ('never', 'Never'),
        ],
        default='weekly',
        help_text="How frequently the page is likely to change"
    )
    priority = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Priority of this URL relative to other URLs on your site"
    )
    last_modified = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the page was last modified"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether to include this URL in the sitemap"
    )

    class Meta:
        ordering = ['-priority', '-last_modified']
        indexes = [
            models.Index(fields=['is_active', '-priority']),
            models.Index(fields=['change_frequency']),
            models.Index(fields=['-last_modified']),
            models.Index(fields=['url']),
        ]

    def __str__(self) -> str:
        return f"{self.url} (Priority: {self.priority})"


class SEOMetadata(TimestampedModel):
    """
    Stores SEO metadata for various content types.
    """
    content_type = models.CharField(
        max_length=50,
        choices=[
            ('job_posting', 'Job Posting'),
            ('category_page', 'Category Page'),
            ('search_page', 'Search Page'),
            ('static_page', 'Static Page'),
        ],
        help_text="Type of content this metadata applies to"
    )
    content_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID of the related content object"
    )
    url_path = models.CharField(
        max_length=255,
        unique=True,
        help_text="URL path for this content"
    )

    # SEO Fields
    title = models.CharField(
        max_length=60,
        help_text="SEO title (50-60 characters)"
    )
    description = models.CharField(
        max_length=160,
        help_text="Meta description (150-160 characters)"
    )
    keywords = models.TextField(
        blank=True,
        help_text="Comma-separated keywords"
    )
    canonical_url = models.URLField(
        blank=True,
        help_text="Canonical URL for this content"
    )

    # Structured Data
    structured_data = models.JSONField(
        default=dict,
        help_text="JSON-LD structured data"
    )

    # OpenGraph Data
    og_title = models.CharField(max_length=95, blank=True)
    og_description = models.CharField(max_length=300, blank=True)
    og_image = models.URLField(blank=True)
    og_type = models.CharField(max_length=50, default='website')

    # Twitter Card Data
    twitter_card = models.CharField(
        max_length=20,
        choices=[
            ('summary', 'Summary'),
            ('summary_large_image', 'Summary Large Image'),
            ('app', 'App'),
            ('player', 'Player'),
        ],
        default='summary'
    )
    twitter_title = models.CharField(max_length=70, blank=True)
    twitter_description = models.CharField(max_length=200, blank=True)
    twitter_image = models.URLField(blank=True)

    # Performance Tracking
    generation_method = models.CharField(
        max_length=20,
        choices=[
            ('auto_nlp', 'Automatic NLP'),
            ('manual', 'Manual Entry'),
            ('template', 'Template Based'),
        ],
        default='auto_nlp'
    )
    quality_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Content quality score (0-100)"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['url_path']),
            models.Index(fields=['title']),
            models.Index(fields=['-updated_at']),
        ]
        unique_together = ['content_type', 'content_id']

    def __str__(self) -> str:
        return f"SEO: {self.title} ({self.content_type})"


class KeywordTracking(TimestampedModel):
    """
    Tracks keyword performance and ranking positions.
    """
    keyword = models.CharField(max_length=255, db_index=True)
    target_url = models.URLField(help_text="URL this keyword should rank for")

    # Ranking Data
    current_position = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Current Google ranking position"
    )
    previous_position = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Previous ranking position"
    )
    best_position = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Best ever ranking position"
    )

    # Performance Metrics
    search_volume = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Monthly search volume"
    )
    difficulty_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Keyword difficulty score (0-100)"
    )

    # Tracking Status
    is_target_keyword = models.BooleanField(
        default=True,
        help_text="Whether this is a target keyword for optimization"
    )
    last_checked = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the ranking was last checked"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['keyword']),
            models.Index(fields=['-search_volume']),
            models.Index(fields=['-difficulty_score']),
        ]

    def __str__(self) -> str:
        position = self.current_position or "Unranked"
        return f"{self.keyword} - Position: {position}"


class SEOAuditLog(TimestampedModel):
    """
    Logs SEO audit activities and results.
    """
    audit_type = models.CharField(
        max_length=30,
        choices=[
            ('metadata_generation', 'Metadata Generation'),
            ('keyword_analysis', 'Keyword Analysis'),
            ('sitemap_update', 'Sitemap Update'),
            ('structured_data', 'Structured Data Update'),
            ('performance_check', 'Performance Check'),
        ],
        help_text="Type of SEO audit performed"
    )

    # Audit Details
    content_type = models.CharField(max_length=50, blank=True)
    content_id = models.PositiveIntegerField(null=True, blank=True)

    # Results
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('warning', 'Warning'),
            ('error', 'Error'),
            ('skipped', 'Skipped'),
        ],
        default='success'
    )
    details = models.JSONField(
        default=dict,
        help_text="Detailed audit results"
    )

    # Performance Metrics
    processing_time = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Processing time in seconds"
    )
    items_processed = models.PositiveIntegerField(
        default=0,
        help_text="Number of items processed"
    )

    # User Context
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who triggered this audit"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['audit_type', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['content_type', 'content_id']),
        ]

    def __str__(self) -> str:
        return f"{self.audit_type} - {self.status} ({self.created_at})"
