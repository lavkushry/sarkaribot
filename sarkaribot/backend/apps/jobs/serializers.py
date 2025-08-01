"""
API serializers for SarkariBot.

This module contains DRF serializers for converting model instances
to JSON and handling API data validation.
"""

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from apps.jobs.models import JobPosting, JobCategory, JobMilestone
from apps.sources.models import GovernmentSource
from apps.scraping.models import ScrapeLog
from datetime import datetime
from typing import Dict, Any


class GovernmentSourceSerializer(serializers.ModelSerializer):
    """Serializer for government sources."""
    
    stats = SerializerMethodField()
    
    class Meta:
        model = GovernmentSource
        fields = [
            'id', 'name', 'display_name', 'base_url',
            'active', 'last_scraped', 'total_jobs_found', 'stats'
        ]
        read_only_fields = ['stats']
    
    def get_stats(self, obj) -> Dict[str, Any]:
        """Get recent statistics for the source."""
        return {
            'jobs_this_month': obj.get_jobs_count_last_30_days(),
            'success_rate': obj.get_success_rate_last_30_days(),
            'avg_jobs_per_scrape': obj.get_avg_jobs_per_scrape(),
            'last_successful_scrape': obj.last_successful_scrape_time()
        }


class JobCategorySerializer(serializers.ModelSerializer):
    """Serializer for job categories."""
    
    job_count = SerializerMethodField()
    latest_jobs_count = SerializerMethodField()
    
    class Meta:
        model = JobCategory
        fields = [
            'id', 'name', 'slug', 'description',
            'position', 'job_count', 'latest_jobs_count'
        ]
    
    def get_job_count(self, obj) -> int:
        """Get total active jobs in this category."""
        return obj.job_postings.filter(
            status__in=['announced', 'admit_card', 'answer_key', 'result']
        ).count()
    
    def get_latest_jobs_count(self, obj) -> int:
        """Get jobs posted in last 7 days."""
        from datetime import timedelta
        from django.utils import timezone
        
        week_ago = timezone.now() - timedelta(days=7)
        return obj.job_postings.filter(
            status__in=['announced', 'admit_card', 'answer_key', 'result'],
            created_at__gte=week_ago
        ).count()


class JobMilestoneSerializer(serializers.ModelSerializer):
    """Serializer for job milestones."""
    
    class Meta:
        model = JobMilestone
        fields = [
            'id', 'milestone_type', 'title', 'description',
            'date', 'is_completed', 'created_at'
        ]


class JobPostingListSerializer(serializers.ModelSerializer):
    """Serializer for job posting list view (lightweight)."""
    
    source_name = serializers.CharField(source='source.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    days_remaining = SerializerMethodField()
    is_new = SerializerMethodField()
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'slug', 'status', 'source_name',
            'category_name', 'category_slug', 'department',
            'total_posts', 'qualification',
            'notification_date', 'application_end_date',
            'application_link', 'days_remaining', 'is_new',
            'created_at', 'updated_at'
        ]
    
    def get_days_remaining(self, obj) -> int:
        """Calculate days remaining for application."""
        if not obj.application_end_date:
            return None
        
        from django.utils import timezone
        today = timezone.now().date()
        
        if obj.application_end_date < today:
            return 0  # Expired
        
        return (obj.application_end_date - today).days
    
    def get_is_new(self, obj) -> bool:
        """Check if job was posted in last 3 days."""
        from datetime import timedelta
        from django.utils import timezone
        
        three_days_ago = timezone.now() - timedelta(days=3)
        return obj.created_at >= three_days_ago


class JobPostingDetailSerializer(serializers.ModelSerializer):
    """Serializer for job posting detail view (complete data)."""
    
    source = GovernmentSourceSerializer(read_only=True)
    category = JobCategorySerializer(read_only=True)
    milestones = JobMilestoneSerializer(many=True, read_only=True)
    
    # SEO and metadata
    seo_metadata = SerializerMethodField()
    breadcrumbs = SerializerMethodField()
    
    # Computed fields
    days_remaining = SerializerMethodField()
    is_new = SerializerMethodField()
    is_expiring_soon = SerializerMethodField()
    application_status = SerializerMethodField()
    
    # Related content
    similar_jobs = SerializerMethodField()
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'slug', 'description', 'source', 'category',
            'status', 'department', 'total_posts', 'qualification',
            
            # Dates
            'notification_date', 'application_end_date', 'exam_date',
            
            # Financial
            'application_fee', 'salary_min', 'salary_max',
            
            # Age limits
            'min_age', 'max_age',
            
            # Links
            'application_link', 'notification_pdf', 'source_url',
            
            # SEO
            'seo_metadata', 'breadcrumbs',
            
            # Computed fields
            'days_remaining', 'is_new', 'is_expiring_soon',
            'application_status',
            
            # Related data
            'milestones', 'similar_jobs',
            
            # Timestamps
            'created_at', 'updated_at', 'published_at'
        ]
    
    def get_seo_metadata(self, obj) -> Dict[str, Any]:
        """Get comprehensive SEO metadata for the job."""
        from apps.seo.engine import seo_engine
        from apps.seo.signals import _prepare_job_data_for_seo
        
        # Check if we have comprehensive metadata stored
        if (obj.structured_data and obj.open_graph_tags and 
            obj.seo_title and obj.seo_description):
            
            return {
                'title': obj.seo_title,
                'description': obj.seo_description,
                'keywords': obj.keywords.split(', ') if obj.keywords else [],
                'canonical_url': obj.canonical_url,
                'structured_data': obj.structured_data,
                'breadcrumb_schema': {
                    "@context": "https://schema.org",
                    "@type": "BreadcrumbList",
                    "itemListElement": obj.breadcrumbs
                } if obj.breadcrumbs else None,
                'open_graph': obj.open_graph_tags,
                'twitter_card': obj.meta_tags,
                'meta_robots': 'index, follow',
                'last_modified': obj.updated_at.isoformat() if obj.updated_at else None,
            }
        
        # Generate comprehensive metadata if not stored (fallback)
        try:
            job_data = _prepare_job_data_for_seo(obj)
            request = self.context.get('request')
            request_url = ""
            
            if request:
                request_url = request.build_absolute_uri(f'/jobs/{obj.slug}/')
            
            comprehensive_metadata = seo_engine.generate_comprehensive_metadata(
                job_data, request_url
            )
            
            return comprehensive_metadata
            
        except Exception as e:
            # Fallback to basic metadata
            return {
                'title': obj.seo_title or obj.title,
                'description': obj.seo_description or obj.description[:160],
                'keywords': obj.keywords.split(', ') if obj.keywords else [],
                'canonical_url': obj.canonical_url or f'/jobs/{obj.slug}/',
                'structured_data': obj.structured_data,
                'open_graph': obj.open_graph_tags,
                'twitter_card': obj.meta_tags,
            }
    
    def get_breadcrumbs(self, obj) -> list:
        """Get breadcrumb navigation data."""
        return obj.breadcrumbs or [
            {"name": "Home", "url": "/"},
            {"name": "Government Jobs", "url": "/jobs/"},
            {"name": obj.category.name if obj.category else "Latest Jobs", 
             "url": f"/jobs/category/{obj.category.slug}/" if obj.category else "/jobs/"},
            {"name": obj.title[:50] + "..." if len(obj.title) > 50 else obj.title,
             "url": f"/jobs/{obj.slug}"}
        ]
    
    def get_days_remaining(self, obj) -> int:
        """Calculate days remaining for application."""
        if not obj.application_end_date:
            return None
        
        from django.utils import timezone
        today = timezone.now().date()
        
        if obj.application_end_date < today:
            return 0  # Expired
        
        return (obj.application_end_date - today).days
    
    def get_is_new(self, obj) -> bool:
        """Check if job was posted in last 3 days."""
        from datetime import timedelta
        from django.utils import timezone
        
        three_days_ago = timezone.now() - timedelta(days=3)
        return obj.created_at >= three_days_ago
    
    def get_is_expiring_soon(self, obj) -> bool:
        """Check if application deadline is within 7 days."""
        days_remaining = self.get_days_remaining(obj)
        return days_remaining is not None and 0 < days_remaining <= 7
    
    def get_application_status(self, obj) -> str:
        """Get human-readable application status."""
        days_remaining = self.get_days_remaining(obj)
        
        if days_remaining is None:
            return "No deadline specified"
        elif days_remaining == 0:
            return "Applications closed"
        elif days_remaining <= 3:
            return f"Closing in {days_remaining} days - Apply now!"
        elif days_remaining <= 7:
            return f"Closing in {days_remaining} days"
        else:
            return f"{days_remaining} days remaining"
    
    def get_similar_jobs(self, obj):
        """Get similar job postings."""
        similar_queryset = JobPosting.objects.filter(
            category=obj.category,
            status__in=['announced', 'admit_card', 'answer_key', 'result']
        ).exclude(id=obj.id).order_by('-created_at')[:5]
        
        return JobPostingListSerializer(similar_queryset, many=True).data


class JobSearchSerializer(serializers.Serializer):
    """Serializer for job search parameters."""
    
    q = serializers.CharField(required=False, help_text="Search query")
    category = serializers.CharField(required=False, help_text="Category slug")
    source = serializers.CharField(required=False, help_text="Source name")
    status = serializers.ChoiceField(
        choices=JobPosting.STATUS_CHOICES,
        required=False,
        help_text="Job status"
    )
    # location = serializers.CharField(required=False, help_text="Location/State")
    qualification = serializers.CharField(required=False, help_text="Qualification level")
    
    # Date filters
    posted_after = serializers.DateField(required=False, help_text="Posted after date")
    posted_before = serializers.DateField(required=False, help_text="Posted before date")
    deadline_after = serializers.DateField(required=False, help_text="Deadline after date")
    deadline_before = serializers.DateField(required=False, help_text="Deadline before date")
    
    # Numeric filters
    min_posts = serializers.IntegerField(required=False, help_text="Minimum number of posts")
    max_posts = serializers.IntegerField(required=False, help_text="Maximum number of posts")
    min_age = serializers.IntegerField(required=False, help_text="Minimum age limit")
    max_age = serializers.IntegerField(required=False, help_text="Maximum age limit")
    
    # Sorting
    ordering = serializers.ChoiceField(
        choices=[
            'created_at', '-created_at',
            'application_end_date', '-application_end_date',
            'total_posts', '-total_posts',
            'title', '-title'
        ],
        default='-created_at',
        required=False,
        help_text="Sort order"
    )
    
    # Pagination
    page = serializers.IntegerField(default=1, min_value=1, required=False)
    page_size = serializers.IntegerField(
        default=20, 
        min_value=1, 
        max_value=100, 
        required=False,
        help_text="Number of results per page"
    )


class ScrapeLogSerializer(serializers.ModelSerializer):
    """Serializer for scrape logs."""
    
    source_name = serializers.CharField(source='source.name', read_only=True)
    duration = SerializerMethodField()
    
    class Meta:
        model = ScrapeLog
        fields = [
            'id', 'source_name', 'started_at', 'completed_at',
            'status', 'scraper_engine', 'pages_scraped',
            'requests_made', 'jobs_found', 'jobs_created',
            'jobs_updated', 'jobs_skipped', 'error_message',
            'duration'
        ]
    
    def get_duration(self, obj) -> float:
        """Calculate scraping duration in seconds."""
        if obj.duration_seconds:
            return float(obj.duration_seconds)
        return 0.0


class StatsSerializer(serializers.Serializer):
    """Serializer for general statistics."""
    
    total_jobs = serializers.IntegerField()
    active_jobs = serializers.IntegerField()
    new_jobs_today = serializers.IntegerField()
    new_jobs_this_week = serializers.IntegerField()
    sources_active = serializers.IntegerField()
    categories_count = serializers.IntegerField()
    jobs_by_status = serializers.DictField()
    jobs_by_category = serializers.DictField()
    recent_scrapes = ScrapeLogSerializer(many=True)


class ContactFormSerializer(serializers.Serializer):
    """Serializer for contact form submissions."""
    
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField()
    
    def validate_message(self, value):
        """Validate message content."""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Message must be at least 10 characters long."
            )
        return value.strip()


class NewsletterSubscriptionSerializer(serializers.Serializer):
    """Serializer for newsletter subscriptions."""
    
    email = serializers.EmailField()
    categories = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of category slugs to subscribe to"
    )
    frequency = serializers.ChoiceField(
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    
    def validate_email(self, value):
        """Validate email is not already subscribed."""
        # You would check against a newsletter subscription model
        return value.lower().strip()


class JobAlertSerializer(serializers.Serializer):
    """Serializer for job alert subscriptions."""
    
    email = serializers.EmailField()
    keywords = serializers.ListField(
        child=serializers.CharField(),
        help_text="Keywords to match in job titles/descriptions"
    )
    categories = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Category slugs to monitor"
    )
    locations = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Locations/states to monitor"
    )
    min_posts = serializers.IntegerField(required=False, min_value=1)
    max_age = serializers.IntegerField(required=False, min_value=18, max_value=65)
    frequency = serializers.ChoiceField(
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest'),
        ],
        default='daily'
    )
    
    def validate_keywords(self, value):
        """Validate keywords list."""
        if not value:
            raise serializers.ValidationError("At least one keyword is required.")
        
        # Clean and validate keywords
        cleaned_keywords = []
        for keyword in value:
            keyword = keyword.strip()
            if len(keyword) >= 3:
                cleaned_keywords.append(keyword)
        
        if not cleaned_keywords:
            raise serializers.ValidationError(
                "Keywords must be at least 3 characters long."
            )
        
        return cleaned_keywords


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for API error responses."""
    
    error = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField()


class SuccessResponseSerializer(serializers.Serializer):
    """Serializer for API success responses."""
    
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    data = serializers.DictField(required=False)
