"""
Django filters for job posting API.

This module provides comprehensive filtering capabilities for job postings
using django-filter integration with DRF.
"""

import django_filters
from django.db import models
from django.utils import timezone
from datetime import timedelta, date
from .models import JobPosting, JobCategory
from apps.sources.models import GovernmentSource


class JobPostingFilter(django_filters.FilterSet):
    """
    Comprehensive filter set for job postings.
    
    Provides filtering by various job attributes with support for
    ranges, choices, and custom logic.
    """
    
    # Text search filters
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        help_text="Filter by job title (case-insensitive)"
    )
    
    department = django_filters.CharFilter(
        field_name='department',
        lookup_expr='icontains',
        help_text="Filter by department/organization"
    )
    
    qualification = django_filters.CharFilter(
        field_name='qualification',
        lookup_expr='icontains',
        help_text="Filter by qualification requirements"
    )
    
    location = django_filters.CharFilter(
        field_name='location',
        lookup_expr='icontains',
        help_text="Filter by job location"
    )
    
    state = django_filters.CharFilter(
        field_name='state',
        lookup_expr='icontains',
        help_text="Filter by state"
    )
    
    # Category filters
    category = django_filters.ModelChoiceFilter(
        field_name='category',
        queryset=JobCategory.objects.all(),
        to_field_name='slug',
        help_text="Filter by category slug"
    )
    
    category_name = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains',
        help_text="Filter by category name"
    )
    
    # Source filters
    source = django_filters.ModelChoiceFilter(
        field_name='source',
        queryset=GovernmentSource.objects.all(),
        to_field_name='name',
        help_text="Filter by source name"
    )
    
    source_type = django_filters.CharFilter(
        field_name='source__status',
        help_text="Filter by source status"
    )
    
    # Status filter
    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=JobPosting.STATUS_CHOICES,
        help_text="Filter by job status"
    )
    
    # Numeric range filters
    total_posts = django_filters.RangeFilter(
        field_name='total_posts',
        help_text="Filter by number of posts (min,max)"
    )
    
    total_posts_min = django_filters.NumberFilter(
        field_name='total_posts',
        lookup_expr='gte',
        help_text="Minimum number of posts"
    )
    
    total_posts_max = django_filters.NumberFilter(
        field_name='total_posts',
        lookup_expr='lte',
        help_text="Maximum number of posts"
    )
    
    # Age filters
    min_age = django_filters.NumberFilter(
        field_name='min_age',
        lookup_expr='lte',
        help_text="Filter jobs where minimum age is at most this value"
    )
    
    max_age = django_filters.NumberFilter(
        field_name='max_age',
        lookup_expr='gte',
        help_text="Filter jobs where maximum age is at least this value"
    )
    
    age_range = django_filters.RangeFilter(
        field_name='max_age',
        help_text="Filter by age range (considering max age)"
    )
    
    # Salary filters
    salary_min = django_filters.NumberFilter(
        field_name='salary_min',
        lookup_expr='gte',
        help_text="Minimum salary threshold"
    )
    
    salary_max = django_filters.NumberFilter(
        field_name='salary_max',
        lookup_expr='lte',
        help_text="Maximum salary threshold"
    )
    
    has_salary = django_filters.BooleanFilter(
        method='filter_has_salary',
        help_text="Filter jobs with salary information"
    )
    
    # Application fee filters
    application_fee = django_filters.RangeFilter(
        field_name='application_fee',
        help_text="Filter by application fee range"
    )
    
    free_application = django_filters.BooleanFilter(
        method='filter_free_application',
        help_text="Filter jobs with free application"
    )
    
    # Date filters
    notification_date = django_filters.DateFromToRangeFilter(
        field_name='notification_date',
        help_text="Filter by notification date range"
    )
    
    application_end_date = django_filters.DateFromToRangeFilter(
        field_name='application_end_date',
        help_text="Filter by application end date range"
    )
    
    exam_date = django_filters.DateFromToRangeFilter(
        field_name='exam_date',
        help_text="Filter by exam date range"
    )
    
    # Creation date filters
    created_at = django_filters.DateFromToRangeFilter(
        field_name='created_at',
        help_text="Filter by creation date range"
    )
    
    created_after = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__gte',
        help_text="Filter jobs created after this date"
    )
    
    created_before = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__lte',
        help_text="Filter jobs created before this date"
    )
    
    # Convenience date filters
    posted_today = django_filters.BooleanFilter(
        method='filter_posted_today',
        help_text="Filter jobs posted today"
    )
    
    posted_this_week = django_filters.BooleanFilter(
        method='filter_posted_this_week',
        help_text="Filter jobs posted this week"
    )
    
    posted_this_month = django_filters.BooleanFilter(
        method='filter_posted_this_month',
        help_text="Filter jobs posted this month"
    )
    
    # Deadline-related filters
    has_deadline = django_filters.BooleanFilter(
        method='filter_has_deadline',
        help_text="Filter jobs with application deadline"
    )
    
    deadline_soon = django_filters.BooleanFilter(
        method='filter_deadline_soon',
        help_text="Filter jobs with deadline within 7 days"
    )
    
    deadline_today = django_filters.BooleanFilter(
        method='filter_deadline_today',
        help_text="Filter jobs with deadline today"
    )
    
    deadline_expired = django_filters.BooleanFilter(
        method='filter_deadline_expired',
        help_text="Filter jobs with expired deadlines"
    )
    
    # Link availability filters
    has_application_link = django_filters.BooleanFilter(
        method='filter_has_application_link',
        help_text="Filter jobs with application link"
    )
    
    has_notification_pdf = django_filters.BooleanFilter(
        method='filter_has_notification_pdf',
        help_text="Filter jobs with notification PDF"
    )
    
    # Special filters
    high_posts = django_filters.BooleanFilter(
        method='filter_high_posts',
        help_text="Filter jobs with high number of posts (>50)"
    )
    
    popular = django_filters.BooleanFilter(
        method='filter_popular',
        help_text="Filter popular jobs (high posts + recent)"
    )
    
    # Search across multiple fields
    search = django_filters.CharFilter(
        method='filter_search',
        help_text="Search across title, description, department, and keywords"
    )
    
    class Meta:
        model = JobPosting
        fields = {
            'status': ['exact', 'in'],
            'total_posts': ['exact', 'gte', 'lte'],
            'min_age': ['exact', 'gte', 'lte'],
            'max_age': ['exact', 'gte', 'lte'],
            'application_fee': ['exact', 'gte', 'lte', 'isnull'],
            'salary_min': ['exact', 'gte', 'lte', 'isnull'],
            'salary_max': ['exact', 'gte', 'lte', 'isnull'],
        }
    
    def filter_has_salary(self, queryset, name, value):
        """Filter jobs that have salary information."""
        if value:
            return queryset.filter(
                models.Q(salary_min__isnull=False) | 
                models.Q(salary_max__isnull=False)
            )
        else:
            return queryset.filter(
                salary_min__isnull=True,
                salary_max__isnull=True
            )
    
    def filter_free_application(self, queryset, name, value):
        """Filter jobs with free application."""
        if value:
            return queryset.filter(
                models.Q(application_fee__isnull=True) |
                models.Q(application_fee=0)
            )
        else:
            return queryset.filter(
                application_fee__isnull=False,
                application_fee__gt=0
            )
    
    def filter_posted_today(self, queryset, name, value):
        """Filter jobs posted today."""
        if value:
            today = timezone.now().date()
            return queryset.filter(created_at__date=today)
        return queryset
    
    def filter_posted_this_week(self, queryset, name, value):
        """Filter jobs posted this week."""
        if value:
            week_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(created_at__gte=week_ago)
        return queryset
    
    def filter_posted_this_month(self, queryset, name, value):
        """Filter jobs posted this month."""
        if value:
            month_ago = timezone.now() - timedelta(days=30)
            return queryset.filter(created_at__gte=month_ago)
        return queryset
    
    def filter_has_deadline(self, queryset, name, value):
        """Filter jobs with application deadline."""
        if value:
            return queryset.filter(application_end_date__isnull=False)
        else:
            return queryset.filter(application_end_date__isnull=True)
    
    def filter_deadline_soon(self, queryset, name, value):
        """Filter jobs with deadline within 7 days."""
        if value:
            today = timezone.now().date()
            next_week = today + timedelta(days=7)
            return queryset.filter(
                application_end_date__isnull=False,
                application_end_date__gte=today,
                application_end_date__lte=next_week
            )
        return queryset
    
    def filter_deadline_today(self, queryset, name, value):
        """Filter jobs with deadline today."""
        if value:
            today = timezone.now().date()
            return queryset.filter(application_end_date=today)
        return queryset
    
    def filter_deadline_expired(self, queryset, name, value):
        """Filter jobs with expired deadlines."""
        if value:
            today = timezone.now().date()
            return queryset.filter(
                application_end_date__isnull=False,
                application_end_date__lt=today
            )
        else:
            today = timezone.now().date()
            return queryset.filter(
                models.Q(application_end_date__isnull=True) |
                models.Q(application_end_date__gte=today)
            )
    
    def filter_has_application_link(self, queryset, name, value):
        """Filter jobs with application link."""
        if value:
            return queryset.exclude(
                models.Q(application_link__isnull=True) |
                models.Q(application_link='')
            )
        else:
            return queryset.filter(
                models.Q(application_link__isnull=True) |
                models.Q(application_link='')
            )
    
    def filter_has_notification_pdf(self, queryset, name, value):
        """Filter jobs with notification PDF."""
        if value:
            return queryset.exclude(
                models.Q(notification_pdf__isnull=True) |
                models.Q(notification_pdf='')
            )
        else:
            return queryset.filter(
                models.Q(notification_pdf__isnull=True) |
                models.Q(notification_pdf='')
            )
    
    def filter_high_posts(self, queryset, name, value):
        """Filter jobs with high number of posts."""
        if value:
            return queryset.filter(total_posts__gte=50)
        else:
            return queryset.filter(
                models.Q(total_posts__lt=50) |
                models.Q(total_posts__isnull=True)
            )
    
    def filter_popular(self, queryset, name, value):
        """Filter popular jobs (high posts + recent)."""
        if value:
            week_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(
                total_posts__gte=20,
                created_at__gte=week_ago
            )
        return queryset
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields."""
        if not value:
            return queryset
        
        search_terms = value.split()
        query = models.Q()
        
        for term in search_terms:
            term_query = (
                models.Q(title__icontains=term) |
                models.Q(description__icontains=term) |
                models.Q(department__icontains=term) |
                models.Q(qualification__icontains=term) |
                models.Q(keywords__icontains=term) |
                models.Q(location__icontains=term)
            )
            query &= term_query
        
        return queryset.filter(query)


class JobCategoryFilter(django_filters.FilterSet):
    """Filter set for job categories."""
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text="Filter by category name"
    )
    
    has_jobs = django_filters.BooleanFilter(
        method='filter_has_jobs',
        help_text="Filter categories with active jobs"
    )
    
    class Meta:
        model = JobCategory
        fields = ['name', 'slug']
    
    def filter_has_jobs(self, queryset, name, value):
        """Filter categories that have active jobs."""
        if value:
            return queryset.filter(
                jobs__status__in=['announced', 'admit_card', 'answer_key', 'result']
            ).distinct()
        return queryset


class GovernmentSourceFilter(django_filters.FilterSet):
    """Filter set for government sources."""
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text="Filter by source name"
    )
    
    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=GovernmentSource.SCRAPE_STATUS_CHOICES,
        help_text="Filter by scraping status"
    )
    
    active = django_filters.BooleanFilter(
        field_name='active',
        help_text="Filter by active status"
    )
    
    has_recent_jobs = django_filters.BooleanFilter(
        method='filter_has_recent_jobs',
        help_text="Filter sources with jobs in last 30 days"
    )
    
    class Meta:
        model = GovernmentSource
        fields = ['name', 'active', 'status']
    
    def filter_has_recent_jobs(self, queryset, name, value):
        """Filter sources that have posted jobs recently."""
        if value:
            month_ago = timezone.now() - timedelta(days=30)
            return queryset.filter(
                jobs__created_at__gte=month_ago
            ).distinct()
        return queryset
