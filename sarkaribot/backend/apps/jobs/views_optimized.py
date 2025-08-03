"""
Optimized API views for SarkariBot with database performance improvements.

This module provides optimized versions of the API views that eliminate N+1 queries,
use proper database aggregations, and implement efficient caching strategies.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.db.models import Count, Prefetch, Q, F, Max, Avg
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from datetime import timedelta, date
import logging

from .models import JobPosting, JobCategory, JobMilestone
from .serializers import (
    JobPostingListSerializer, JobPostingDetailSerializer,
    JobCategorySerializer, JobSearchSerializer, StatsSerializer,
    ContactFormSerializer, NewsletterSubscriptionSerializer,
    JobAlertSerializer, ScrapeLogSerializer
)
from .filters import JobPostingFilter
from apps.sources.models import GovernmentSource
from apps.scraping.models import ScrapeLog

logger = logging.getLogger(__name__)


class OptimizedStandardResultsSetPagination(PageNumberPagination):
    """Optimized pagination with metadata caching."""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """Return paginated response with cached metadata where possible."""
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class OptimizedJobPostingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Optimized API endpoint for job postings with performance improvements.
    
    Key optimizations:
    - Eliminates N+1 queries with proper select_related/prefetch_related
    - Uses database aggregations for statistics
    - Implements efficient caching for expensive operations
    - Optimizes common query patterns
    """
    
    # Optimized base queryset with all necessary relationships pre-loaded
    queryset = JobPosting.objects.filter(
        status__in=['announced', 'admit_card', 'answer_key', 'result']
    ).select_related(
        'source', 'category'
    ).prefetch_related(
        Prefetch(
            'milestones',
            queryset=JobMilestone.objects.filter(is_active=True).order_by('-milestone_date'),
            to_attr='active_milestones'
        )
    ).order_by('-published_at', '-created_at')
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobPostingFilter
    search_fields = ['title', 'description', 'department', 'qualification']
    ordering_fields = ['created_at', 'application_end_date', 'total_posts', 'title']
    ordering = ['-created_at']
    pagination_class = OptimizedStandardResultsSetPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return JobPostingDetailSerializer
        return JobPostingListSerializer
    
    def get_queryset(self):
        """Apply additional filtering with optimized queries."""
        queryset = super().get_queryset()
        
        # Category filtering with index hint
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Source filtering with index hint
        source_name = self.request.query_params.get('source')
        if source_name:
            queryset = queryset.filter(source__name__icontains=source_name)
        
        # Optimized date range filtering using indexes
        days_back = self.request.query_params.get('days_back')
        if days_back:
            try:
                days = int(days_back)
                cutoff_date = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(created_at__gte=cutoff_date)
            except ValueError:
                pass
        
        # Deadline filtering optimized for index usage
        has_deadline = self.request.query_params.get('has_deadline')
        if has_deadline == 'true':
            queryset = queryset.filter(application_end_date__isnull=False)
        elif has_deadline == 'false':
            queryset = queryset.filter(application_end_date__isnull=True)
        
        # Optimized expiring soon filter using dedicated index
        expiring_soon = self.request.query_params.get('expiring_soon')
        if expiring_soon == 'true':
            next_week = timezone.now().date() + timedelta(days=7)
            queryset = queryset.filter(
                application_end_date__isnull=False,
                application_end_date__lte=next_week,
                application_end_date__gte=timezone.now().date(),
                status__in=['announced', 'admit_card']
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest job postings with caching."""
        cache_key = 'latest_jobs_v1'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Use optimized query with limit
        latest_jobs = self.get_queryset()[:10]
        serializer = JobPostingListSerializer(latest_jobs, many=True)
        
        response_data = {
            'count': len(latest_jobs),
            'results': serializer.data
        }
        
        # Cache for 15 minutes
        cache.set(cache_key, response_data, 15 * 60)
        return Response(response_data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending job postings using optimized query."""
        cache_key = 'trending_jobs_v1'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Use the dedicated trending index
        trending_jobs = self.get_queryset().filter(
            total_posts__gte=10,
            status__in=['announced', 'admit_card']
        ).order_by('-view_count', '-total_posts', '-created_at')[:10]
        
        serializer = JobPostingListSerializer(trending_jobs, many=True)
        response_data = {
            'count': len(trending_jobs),
            'results': serializer.data
        }
        
        # Cache for 30 minutes
        cache.set(cache_key, response_data, 30 * 60)
        return Response(response_data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get jobs expiring within next 7 days using optimized index."""
        cache_key = 'expiring_soon_jobs_v1'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        next_week = timezone.now().date() + timedelta(days=7)
        
        # Use the dedicated urgent jobs index
        expiring_jobs = self.get_queryset().filter(
            application_end_date__isnull=False,
            application_end_date__lte=next_week,
            application_end_date__gte=timezone.now().date(),
            status__in=['announced', 'admit_card']
        ).order_by('application_end_date')[:20]
        
        serializer = JobPostingListSerializer(expiring_jobs, many=True)
        response_data = {
            'count': len(expiring_jobs),
            'results': serializer.data
        }
        
        # Cache for 1 hour
        cache.set(cache_key, response_data, 60 * 60)
        return Response(response_data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get jobs grouped by category using optimized bulk query."""
        cache_key = 'jobs_by_category_v1'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get categories with job counts in a single query
        categories_with_counts = JobCategory.objects.filter(
            is_active=True
        ).annotate(
            job_count=Count(
                'job_postings',
                filter=Q(job_postings__status__in=['announced', 'admit_card', 'answer_key', 'result'])
            )
        ).order_by('position')
        
        result = {}
        
        # Get jobs for each category in efficient batches
        category_ids = [cat.id for cat in categories_with_counts if cat.job_count > 0]
        if category_ids:
            jobs_by_category = {}
            all_jobs = self.get_queryset().filter(
                category_id__in=category_ids
            ).order_by('category_id', '-created_at')
            
            # Group jobs by category
            for job in all_jobs:
                if job.category_id not in jobs_by_category:
                    jobs_by_category[job.category_id] = []
                if len(jobs_by_category[job.category_id]) < 5:
                    jobs_by_category[job.category_id].append(job)
            
            # Build response
            for category in categories_with_counts:
                category_jobs = jobs_by_category.get(category.id, [])
                result[category.slug] = {
                    'name': category.name,
                    'count': category.job_count,
                    'jobs': JobPostingListSerializer(category_jobs, many=True).data
                }
        
        # Cache for 20 minutes
        cache.set(cache_key, result, 20 * 60)
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Get similar jobs using optimized query."""
        job = self.get_object()
        
        cache_key = f'similar_jobs_{job.id}_v1'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Use category + source for better similarity
        similar_jobs = self.get_queryset().filter(
            Q(category=job.category) | Q(source=job.source)
        ).exclude(id=job.id).order_by('-created_at')[:5]
        
        serializer = JobPostingListSerializer(similar_jobs, many=True)
        response_data = {
            'count': len(similar_jobs),
            'results': serializer.data
        }
        
        # Cache for 1 hour
        cache.set(cache_key, response_data, 60 * 60)
        return Response(response_data)


class OptimizedJobCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Optimized API endpoint for job categories with efficient count calculations.
    """
    
    # Pre-load job counts using annotations
    queryset = JobCategory.objects.filter(
        is_active=True
    ).annotate(
        active_job_count=Count(
            'job_postings',
            filter=Q(job_postings__status__in=['announced', 'admit_card', 'answer_key', 'result'])
        ),
        recent_job_count=Count(
            'job_postings',
            filter=Q(
                job_postings__status__in=['announced', 'admit_card', 'answer_key', 'result'],
                job_postings__created_at__gte=timezone.now() - timedelta(days=7)
            )
        )
    ).order_by('position')
    
    serializer_class = JobCategorySerializer
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def jobs(self, request, slug=None):
        """Get jobs for a specific category with optimized query."""
        category = self.get_object()
        
        jobs_queryset = JobPosting.objects.filter(
            category=category,
            status__in=['announced', 'admit_card', 'answer_key', 'result']
        ).select_related('source', 'category').order_by('-created_at')
        
        # Apply pagination
        paginator = OptimizedStandardResultsSetPagination()
        paginated_jobs = paginator.paginate_queryset(jobs_queryset, request)
        
        serializer = JobPostingListSerializer(paginated_jobs, many=True)
        return paginator.get_paginated_response(serializer.data)


class OptimizedStatsAPIView(APIView):
    """
    Optimized API endpoint for statistics using database aggregations and caching.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get comprehensive statistics using optimized queries."""
        # Check cache first
        cache_key = 'api_stats_optimized_v1'
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Calculate statistics using efficient database aggregations
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Single query for job statistics
        job_stats = JobPosting.objects.aggregate(
            total_jobs=Count('id'),
            active_jobs=Count('id', filter=Q(status__in=['announced', 'admit_card', 'answer_key', 'result'])),
            new_jobs_today=Count('id', filter=Q(created_at__date=today)),
            new_jobs_this_week=Count('id', filter=Q(created_at__date__gte=week_ago)),
        )
        
        # Single query for source statistics  
        source_stats = GovernmentSource.objects.aggregate(
            sources_active=Count('id', filter=Q(active=True, status='active'))
        )
        
        # Get category count
        categories_count = JobCategory.objects.filter(is_active=True).count()
        
        # Jobs by status using single query
        jobs_by_status = {}
        status_counts = JobPosting.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        for item in status_counts:
            status_code = item['status']
            status_name = dict(JobPosting.STATUS_CHOICES).get(status_code, status_code)
            jobs_by_status[status_code] = {
                'name': status_name,
                'count': item['count']
            }
        
        # Jobs by category using single query with joins
        jobs_by_category = {}
        category_counts = JobCategory.objects.filter(
            is_active=True
        ).annotate(
            count=Count(
                'job_postings',
                filter=Q(job_postings__status__in=['announced', 'admit_card', 'answer_key', 'result'])
            )
        ).values('slug', 'name', 'count')
        
        for item in category_counts:
            jobs_by_category[item['slug']] = {
                'name': item['name'],
                'count': item['count']
            }
        
        # Recent scrape logs with optimized query
        recent_scrapes = ScrapeLog.objects.select_related('source').order_by(
            '-started_at'
        )[:5]
        
        stats_data = {
            **job_stats,
            **source_stats,
            'categories_count': categories_count,
            'jobs_by_status': jobs_by_status,
            'jobs_by_category': jobs_by_category,
            'recent_scrapes': ScrapeLogSerializer(recent_scrapes, many=True).data
        }
        
        # Cache for 30 minutes
        cache.set(cache_key, stats_data, 30 * 60)
        
        serializer = StatsSerializer(stats_data)
        return Response(serializer.data)