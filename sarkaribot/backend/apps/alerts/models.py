# Advanced Job Alert System for SarkariBot

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.utils import timezone
import uuid

User = get_user_model()

class JobAlert(models.Model):
    """
    Advanced job alert system for users to receive notifications
    about new jobs matching their criteria.
    """
    FREQUENCY_CHOICES = [
        ('instant', 'Instant'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    DELIVERY_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('webhook', 'Webhook'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_alerts')
    name = models.CharField(max_length=255, help_text="Name for this alert")
    
    # Alert criteria
    keywords = models.TextField(blank=True, help_text="Comma-separated keywords")
    categories = models.ManyToManyField('jobs.Category', blank=True)
    sources = models.ManyToManyField('sources.Source', blank=True)
    locations = models.TextField(blank=True, help_text="Comma-separated locations")
    qualifications = models.TextField(blank=True, help_text="Comma-separated qualifications")
    
    # Salary and age filters
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    min_age = models.IntegerField(null=True, blank=True)
    max_age = models.IntegerField(null=True, blank=True)
    
    # Delivery preferences
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='email')
    delivery_email = models.EmailField(validators=[validate_email], blank=True)
    delivery_phone = models.CharField(max_length=15, blank=True)
    webhook_url = models.URLField(blank=True)
    
    # Alert settings
    is_active = models.BooleanField(default=True)
    last_sent = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['frequency', 'is_active']),
            models.Index(fields=['last_sent']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def get_matching_jobs(self, since=None):
        """
        Get jobs that match this alert's criteria.
        """
        from apps.jobs.models import JobPosting
        from django.db.models import Q
        
        queryset = JobPosting.objects.filter(status='announced')
        
        if since:
            queryset = queryset.filter(created_at__gte=since)
        
        # Keywords filter
        if self.keywords:
            keywords = [k.strip() for k in self.keywords.split(',')]
            keyword_q = Q()
            for keyword in keywords:
                keyword_q |= Q(title__icontains=keyword) | Q(description__icontains=keyword)
            queryset = queryset.filter(keyword_q)
        
        # Category filter
        if self.categories.exists():
            queryset = queryset.filter(category__in=self.categories.all())
        
        # Source filter
        if self.sources.exists():
            queryset = queryset.filter(source__in=self.sources.all())
        
        # Salary filter
        if self.min_salary:
            queryset = queryset.filter(salary_min__gte=self.min_salary)
        if self.max_salary:
            queryset = queryset.filter(salary_max__lte=self.max_salary)
        
        # Age filter
        if self.min_age:
            queryset = queryset.filter(min_age__lte=self.min_age)
        if self.max_age:
            queryset = queryset.filter(max_age__gte=self.max_age)
        
        return queryset.distinct()


class JobAlertLog(models.Model):
    """
    Log of job alert deliveries for tracking and analytics.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]
    
    alert = models.ForeignKey(JobAlert, on_delete=models.CASCADE, related_name='logs')
    jobs_count = models.IntegerField(default=0)
    delivery_method = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['alert', 'status']),
            models.Index(fields=['sent_at']),
        ]
    
    def __str__(self):
        return f"{self.alert.name} - {self.status} - {self.sent_at}"


class UserNotificationPreference(models.Model):
    """
    User preferences for different types of notifications.
    """
    NOTIFICATION_TYPES = [
        ('job_alerts', 'Job Alerts'),
        ('system_updates', 'System Updates'),
        ('newsletter', 'Newsletter'),
        ('promotional', 'Promotional'),
        ('security', 'Security Alerts'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_job_alerts = models.BooleanField(default=True)
    email_system_updates = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=False)
    email_promotional = models.BooleanField(default=False)
    email_security = models.BooleanField(default=True)
    
    # SMS preferences
    sms_job_alerts = models.BooleanField(default=False)
    sms_system_updates = models.BooleanField(default=False)
    sms_security = models.BooleanField(default=True)
    
    # Push notification preferences
    push_job_alerts = models.BooleanField(default=True)
    push_system_updates = models.BooleanField(default=True)
    push_security = models.BooleanField(default=True)
    
    # Global settings
    quiet_hours_start = models.TimeField(default='22:00')
    quiet_hours_end = models.TimeField(default='08:00')
    timezone = models.CharField(max_length=50, default='Asia/Kolkata')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"


class JobBookmark(models.Model):
    """
    User bookmarks for saving interesting jobs.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    job = models.ForeignKey('jobs.JobPosting', on_delete=models.CASCADE, related_name='bookmarks')
    notes = models.TextField(blank=True, help_text="Personal notes about this job")
    reminder_date = models.DateTimeField(null=True, blank=True, help_text="Set a reminder for this job")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'job']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['reminder_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.job.title}"


class JobApplication(models.Model):
    """
    Track user job applications.
    """
    STATUS_CHOICES = [
        ('interested', 'Interested'),
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Scheduled'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey('jobs.JobPosting', on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='interested')
    application_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Application tracking
    application_id = models.CharField(max_length=100, blank=True, help_text="External application ID")
    documents_submitted = models.JSONField(default=list, help_text="List of submitted documents")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'job']
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['job', 'status']),
            models.Index(fields=['application_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.job.title} - {self.status}"
