"""
Optimized API serializers for SarkariBot with performance improvements.

This module provides optimized versions of the serializers that eliminate N+1 queries
and use efficient data access patterns.
"""

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, Any

from apps.jobs.models import JobPosting, JobCategory, JobMilestone
from apps.sources.models import GovernmentSource
from apps.scraping.models import ScrapeLog


class OptimizedGovernmentSourceSerializer(serializers.ModelSerializer):
    """Optimized serializer for government sources with pre-computed stats."""
    
    stats = SerializerMethodField()
    
    class Meta:
        model = GovernmentSource
        fields = [
            'id', 'name', 'display_name', 'base_url',
            'active', 'last_scraped', 'total_jobs_found', 'stats'
        ]
        read_only_fields = ['stats']
    
    def get_stats(self, obj) -> Dict[str, Any]:
        """Get cached or pre-computed statistics for the source."""
        # Check if stats are already annotated on the object
        if hasattr(obj, '_prefetched_stats'):
            return obj._prefetched_stats
        
        # Fallback to individual queries (should be avoided in bulk operations)
        return {
            'jobs_this_month': obj.get_jobs_count_last_30_days(),
            'success_rate': obj.get_success_rate_last_30_days(),
            'avg_jobs_per_scrape': obj.get_avg_jobs_per_scrape(),
            'last_successful_scrape': obj.last_successful_scrape_time()
        }


class OptimizedJobCategorySerializer(serializers.ModelSerializer):
    """Optimized serializer for job categories using pre-computed counts."""
    
    job_count = SerializerMethodField()
    latest_jobs_count = SerializerMethodField()
    
    class Meta:
        model = JobCategory
        fields = [
            'id', 'name', 'slug', 'description',
            'position', 'job_count', 'latest_jobs_count'
        ]
    
    def get_job_count(self, obj) -> int:
        """Get job count from annotation if available, otherwise calculate."""
        # Use pre-computed count if available (from queryset annotation)
        if hasattr(obj, 'active_job_count'):
            return obj.active_job_count
        
        # Fallback to cached count or calculation
        return getattr(obj, '_job_count_cache', 0)
    
    def get_latest_jobs_count(self, obj) -> int:
        """Get recent jobs count from annotation if available."""
        # Use pre-computed count if available (from queryset annotation)
        if hasattr(obj, 'recent_job_count'):
            return obj.recent_job_count
        
        # Fallback to cached count or calculation
        return getattr(obj, '_recent_job_count_cache', 0)


class OptimizedJobMilestoneSerializer(serializers.ModelSerializer):
    """Optimized serializer for job milestones."""
    
    class Meta:
        model = JobMilestone
        fields = [
            'id', 'milestone_type', 'title', 'description',
            'milestone_date', 'is_active', 'created_at'
        ]


class OptimizedJobPostingListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for job posting list view with minimal database hits.
    """
    
    source_name = serializers.CharField(source='source.name', read_only=True)
    source_display_name = serializers.CharField(source='source.display_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    days_remaining = SerializerMethodField()
    is_new = SerializerMethodField()
    is_urgent = SerializerMethodField()
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'slug', 'status', 'source_name', 'source_display_name',
            'category_name', 'category_slug', 'department',
            'total_posts', 'qualification', 'short_description',
            'notification_date', 'application_end_date',
            'application_link', 'days_remaining', 'is_new', 'is_urgent',
            'created_at', 'updated_at', 'published_at'
        ]
    
    def get_days_remaining(self, obj) -> int:
        """Calculate days remaining using cached computation if available."""
        if not obj.application_end_date:
            return None
        
        # Use cached computation if available
        if hasattr(obj, '_days_remaining_cache'):
            return obj._days_remaining_cache
        
        today = timezone.now().date()
        if obj.application_end_date < today:
            return 0  # Expired
        
        return (obj.application_end_date - today).days
    
    def get_is_new(self, obj) -> bool:
        """Check if job was posted in last 3 days using cached computation."""
        if hasattr(obj, '_is_new_cache'):
            return obj._is_new_cache
        
        three_days_ago = timezone.now() - timedelta(days=3)
        return obj.created_at >= three_days_ago
    
    def get_is_urgent(self, obj) -> bool:
        """Check if job is urgent (deadline within 7 days)."""
        days_remaining = self.get_days_remaining(obj)
        return days_remaining is not None and 0 < days_remaining <= 7


class OptimizedJobPostingDetailSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for job posting detail view with efficient related data loading.
    """
    
    source = OptimizedGovernmentSourceSerializer(read_only=True)
    category = OptimizedJobCategorySerializer(read_only=True)
    milestones = SerializerMethodField()  # Use prefetched data
    
    # SEO and metadata
    seo_metadata = SerializerMethodField()
    breadcrumbs = SerializerMethodField()
    
    # Computed fields
    days_remaining = SerializerMethodField()
    is_new = SerializerMethodField()
    is_expiring_soon = SerializerMethodField()
    application_status = SerializerMethodField()
    
    # Related content - optimized to avoid additional queries
    similar_jobs = SerializerMethodField()
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'source', 'category', 'status', 'department', 'total_posts', 
            'qualification',
            
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
            'created_at', 'updated_at', 'published_at', 'view_count'
        ]
    
    def get_milestones(self, obj):
        """Get milestones from prefetched data to avoid additional queries."""
        # Use prefetched milestones if available
        if hasattr(obj, 'active_milestones'):
            milestones = obj.active_milestones
        else:
            # Fallback to related manager (will cause additional query)
            milestones = obj.milestones.filter(is_active=True).order_by('-milestone_date')[:5]
        
        return OptimizedJobMilestoneSerializer(milestones, many=True).data
    
    def get_seo_metadata(self, obj) -> Dict[str, Any]:
        """Get SEO metadata for the job."""
        return {
            'title': obj.seo_title,
            'description': obj.seo_description,
            'keywords': obj.keywords.split(', ') if obj.keywords else [],
            'canonical_url': obj.canonical_url,
            'structured_data': obj.structured_data,
            'meta_tags': obj.meta_tags,
            'open_graph_tags': obj.open_graph_tags,
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
        
        today = timezone.now().date()
        if obj.application_end_date < today:
            return 0  # Expired
        
        return (obj.application_end_date - today).days
    
    def get_is_new(self, obj) -> bool:
        """Check if job was posted in last 3 days."""
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
        """Get similar job postings using cached data if available."""
        # Check if similar jobs are already provided via context
        context_similar = self.context.get('similar_jobs', {})
        if obj.id in context_similar:
            return OptimizedJobPostingListSerializer(
                context_similar[obj.id], 
                many=True
            ).data
        
        # Fallback to database query (should be avoided)
        similar_queryset = JobPosting.objects.filter(
            category=obj.category,
            status__in=['announced', 'admit_card', 'answer_key', 'result']
        ).exclude(id=obj.id).select_related(
            'source', 'category'
        ).order_by('-created_at')[:3]
        
        return OptimizedJobPostingListSerializer(similar_queryset, many=True).data


class OptimizedScrapeLogSerializer(serializers.ModelSerializer):
    """Optimized serializer for scrape logs."""
    
    source_name = serializers.CharField(source='source.name', read_only=True)
    source_display_name = serializers.CharField(source='source.display_name', read_only=True)
    duration = SerializerMethodField()
    success_rate = SerializerMethodField()
    
    class Meta:
        model = ScrapeLog
        fields = [
            'id', 'source_name', 'source_display_name', 'started_at', 'completed_at',
            'status', 'scraper_engine', 'pages_scraped',
            'requests_made', 'jobs_found', 'jobs_created',
            'jobs_updated', 'jobs_skipped', 'error_message',
            'duration', 'success_rate'
        ]
    
    def get_duration(self, obj) -> float:
        """Calculate scraping duration in seconds."""
        if obj.duration_seconds:
            return float(obj.duration_seconds)
        return 0.0
    
    def get_success_rate(self, obj) -> float:
        """Calculate success rate for the scrape."""
        total_processed = obj.jobs_created + obj.jobs_updated + obj.jobs_skipped
        if total_processed == 0:
            return 0.0
        return (obj.jobs_created + obj.jobs_updated) / total_processed * 100


# Bulk serializers for efficient data loading
class BulkJobCategorySerializer(serializers.ModelSerializer):
    """Bulk serializer for job categories with pre-computed stats."""
    
    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'slug', 'active_job_count', 'recent_job_count']
    
    def to_representation(self, instance):
        """Use pre-computed values from annotations."""
        return {
            'id': instance.id,
            'name': instance.name,
            'slug': instance.slug,
            'job_count': getattr(instance, 'active_job_count', 0),
            'recent_job_count': getattr(instance, 'recent_job_count', 0),
        }


class BulkJobPostingSerializer(serializers.ModelSerializer):
    """Bulk serializer for job postings with minimal field selection."""
    
    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'slug', 'status', 'total_posts',
            'application_end_date', 'created_at', 'source_id', 'category_id'
        ]


# Cache-aware serializers
class CachedStatsSerializer(serializers.Serializer):
    """Serializer for cached statistics with efficient data access."""
    
    total_jobs = serializers.IntegerField()
    active_jobs = serializers.IntegerField()
    new_jobs_today = serializers.IntegerField()
    new_jobs_this_week = serializers.IntegerField()
    sources_active = serializers.IntegerField()
    categories_count = serializers.IntegerField()
    jobs_by_status = serializers.DictField()
    jobs_by_category = serializers.DictField()
    recent_scrapes = OptimizedScrapeLogSerializer(many=True)