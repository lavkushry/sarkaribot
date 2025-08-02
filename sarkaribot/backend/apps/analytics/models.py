"""
Advanced Analytics and Reporting Models for SarkariBot
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class PageView(models.Model):
    """
    Track page views for analytics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Page information
    path = models.CharField(max_length=255, db_index=True)
    page_title = models.CharField(max_length=255, blank=True)
    referrer = models.URLField(blank=True)
    
    # User information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Device/Browser information
    device_type = models.CharField(max_length=50, blank=True)  # mobile, tablet, desktop
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    
    # Geographic information
    country = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Timing information
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    duration = models.IntegerField(null=True, blank=True, help_text="Time spent on page in seconds")
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['path', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['session_id', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.path} - {self.created_at}"


class JobView(models.Model):
    """
    Track specific job posting views.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    job = models.ForeignKey('jobs.JobPosting', on_delete=models.CASCADE, related_name='view_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField()
    
    # View context
    referrer = models.URLField(blank=True)
    search_query = models.CharField(max_length=255, blank=True)
    came_from_alert = models.BooleanField(default=False)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    view_duration = models.IntegerField(null=True, blank=True, help_text="Time spent viewing job in seconds")
    
    # Actions taken
    clicked_apply = models.BooleanField(default=False)
    bookmarked = models.BooleanField(default=False)
    shared = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"View of {self.job.title} - {self.created_at}"


class SearchQuery(models.Model):
    """
    Track search queries for analytics and optimization.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Query information
    query = models.CharField(max_length=255, db_index=True)
    filters_applied = models.JSONField(default=dict, blank=True)
    results_count = models.IntegerField(default=0)
    
    # User information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField()
    
    # Performance metrics
    response_time = models.FloatField(help_text="Response time in seconds")
    
    # User interaction
    clicked_results = models.IntegerField(default=0)
    page_views = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Search: '{self.query}' - {self.results_count} results"


class UserSession(models.Model):
    """
    Track user sessions for analytics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Session details
    start_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    duration = models.IntegerField(null=True, blank=True, help_text="Session duration in seconds")
    
    # Technical details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    
    # Geographic information
    country = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Activity metrics
    page_views = models.IntegerField(default=0)
    job_views = models.IntegerField(default=0)
    searches = models.IntegerField(default=0)
    applications = models.IntegerField(default=0)
    bookmarks = models.IntegerField(default=0)
    
    # Session outcome
    converted = models.BooleanField(default=False)  # Applied to at least one job
    bounce = models.BooleanField(default=True)  # Only viewed one page
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', '-start_time']),
            models.Index(fields=['-start_time']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id} - {self.start_time}"


class AlertEngagement(models.Model):
    """
    Track engagement with job alerts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    alert = models.ForeignKey('alerts.JobAlert', on_delete=models.CASCADE, related_name='engagement_logs')
    alert_log = models.ForeignKey('alerts.JobAlertLog', on_delete=models.CASCADE, related_name='engagement_logs')
    
    # Engagement metrics
    opened = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)
    jobs_clicked = models.IntegerField(default=0)
    applications_made = models.IntegerField(default=0)
    bookmarks_made = models.IntegerField(default=0)
    
    # Timing
    sent_at = models.DateTimeField()
    first_opened_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Alert engagement for {self.alert.name} - {self.sent_at}"


class PerformanceMetric(models.Model):
    """
    Track system performance metrics.
    """
    METRIC_TYPES = [
        ('api_response_time', 'API Response Time'),
        ('page_load_time', 'Page Load Time'),
        ('search_response_time', 'Search Response Time'),
        ('database_query_time', 'Database Query Time'),
        ('scraping_success_rate', 'Scraping Success Rate'),
        ('alert_delivery_rate', 'Alert Delivery Rate'),
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES, db_index=True)
    value = models.FloatField()
    unit = models.CharField(max_length=20, default='seconds')
    
    # Context
    endpoint = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['metric_type', '-recorded_at']),
            models.Index(fields=['-recorded_at']),
        ]
    
    def __str__(self):
        return f"{self.metric_type}: {self.value} {self.unit} - {self.recorded_at}"


class DailyStats(models.Model):
    """
    Daily aggregated statistics.
    """
    date = models.DateField(unique=True, db_index=True)
    
    # Traffic metrics
    unique_visitors = models.IntegerField(default=0)
    page_views = models.IntegerField(default=0)
    sessions = models.IntegerField(default=0)
    bounce_rate = models.FloatField(default=0.0)
    avg_session_duration = models.FloatField(default=0.0)
    
    # Job metrics
    jobs_viewed = models.IntegerField(default=0)
    jobs_applied = models.IntegerField(default=0)
    jobs_bookmarked = models.IntegerField(default=0)
    jobs_shared = models.IntegerField(default=0)
    
    # Search metrics
    searches_performed = models.IntegerField(default=0)
    avg_search_results = models.FloatField(default=0.0)
    top_search_terms = models.JSONField(default=list)
    
    # Alert metrics
    alerts_sent = models.IntegerField(default=0)
    alerts_opened = models.IntegerField(default=0)
    alerts_clicked = models.IntegerField(default=0)
    
    # Content metrics
    new_jobs_added = models.IntegerField(default=0)
    jobs_updated = models.IntegerField(default=0)
    
    # Performance metrics
    avg_response_time = models.FloatField(default=0.0)
    uptime_percentage = models.FloatField(default=100.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date']),
        ]
    
    def __str__(self):
        return f"Daily stats for {self.date}"


class ConversionFunnel(models.Model):
    """
    Track conversion funnel stages.
    """
    STAGES = [
        ('landing', 'Landing Page'),
        ('browse', 'Browse Jobs'),
        ('search', 'Search Jobs'),
        ('view_job', 'View Job Details'),
        ('click_apply', 'Click Apply'),
        ('register', 'Register Account'),
        ('bookmark', 'Bookmark Job'),
        ('share', 'Share Job'),
        ('create_alert', 'Create Alert'),
    ]
    
    stage = models.CharField(max_length=50, choices=STAGES, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=255, db_index=True)
    
    # Context
    job = models.ForeignKey('jobs.JobPosting', on_delete=models.SET_NULL, null=True, blank=True)
    source_stage = models.CharField(max_length=50, blank=True)  # Previous stage
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stage', '-created_at']),
            models.Index(fields=['session_id', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.stage} - {self.created_at}"
