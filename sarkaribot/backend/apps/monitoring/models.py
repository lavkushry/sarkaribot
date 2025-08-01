"""
Monitoring models for tracking system health and performance.
"""
from typing import Dict, Any, Optional
import logging
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class SystemHealth(models.Model):
    """Track system health metrics."""
    
    STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('down', 'Down'),
    ]
    
    component = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    details = models.JSONField(default=dict)
    last_check = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_check']
        indexes = [
            models.Index(fields=['component', 'status']),
        ]
    
    def __str__(self) -> str:
        return f"{self.component}: {self.status}"


class ErrorLog(models.Model):
    """Store application errors for analysis."""
    
    LEVEL_CHOICES = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    SOURCE_CHOICES = [
        ('django', 'Django'),
        ('celery', 'Celery'),
        ('scraping', 'Scraping'),
        ('frontend', 'Frontend'),
        ('api', 'API'),
    ]
    
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    message = models.TextField()
    traceback = models.TextField(null=True, blank=True)
    request_path = models.CharField(max_length=500, null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level', 'source']),
            models.Index(fields=['created_at']),
            models.Index(fields=['resolved']),
        ]
    
    def __str__(self) -> str:
        return f"{self.level}: {self.message[:100]}"
    
    @classmethod
    def log_error(
        cls,
        level: str,
        source: str,
        message: str,
        traceback: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        request=None
    ) -> 'ErrorLog':
        """Create an error log entry."""
        try:
            data = {
                'level': level,
                'source': source,
                'message': message,
                'traceback': traceback,
                'metadata': metadata or {},
            }
            
            if request:
                data.update({
                    'request_path': request.path,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'ip_address': cls._get_client_ip(request),
                })
            
            return cls.objects.create(**data)
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
            return None
    
    @staticmethod
    def _get_client_ip(request) -> str:
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PerformanceMetric(models.Model):
    """Track performance metrics."""
    
    METRIC_TYPES = [
        ('response_time', 'Response Time'),
        ('memory_usage', 'Memory Usage'),
        ('db_query_time', 'Database Query Time'),
        ('scraping_time', 'Scraping Time'),
        ('cpu_usage', 'CPU Usage'),
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.FloatField()
    unit = models.CharField(max_length=20)  # ms, seconds, MB, %
    component = models.CharField(max_length=100)
    metadata = models.JSONField(default=dict)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['metric_type', 'component']),
            models.Index(fields=['recorded_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.metric_type}: {self.value}{self.unit} ({self.component})"


class UserFeedback(models.Model):
    """Store user feedback on errors and issues."""
    
    FEEDBACK_TYPES = [
        ('bug_report', 'Bug Report'),
        ('error_feedback', 'Error Feedback'),
        ('suggestion', 'Suggestion'),
        ('complaint', 'Complaint'),
    ]
    
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    message = models.TextField()
    error_log = models.ForeignKey(
        ErrorLog, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='user_feedback'
    )
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    page_url = models.URLField(null=True, blank=True)
    contact_info = models.EmailField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['feedback_type']),
            models.Index(fields=['resolved']),
        ]
    
    def __str__(self) -> str:
        return f"{self.feedback_type}: {self.message[:100]}"