"""
API views for SarkariBot.

This module contains DRF viewsets and views for the job portal API,
providing comprehensive endpoints for job search, filtering, and data access.
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


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API results."""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """Return paginated response with additional metadata."""
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class JobPostingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for job postings.
    
    Provides list, detail, search, and filtering functionality
    for government job postings.
    """
    
    queryset = JobPosting.objects.filter(
        status__in=['announced', 'admit_card', 'answer_key', 'result']
    ).select_related('source', 'category').prefetch_related('milestones')
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobPostingFilter
    search_fields = ['title', 'description', 'department', 'qualification']
    ordering_fields = ['created_at', 'application_end_date', 'total_posts', 'title']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return JobPostingDetailSerializer
        return JobPostingListSerializer
    
    def get_queryset(self):
        """Apply additional filtering based on query parameters."""
        queryset = super().get_queryset()
        
        # Category filtering
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Source filtering
        source_name = self.request.query_params.get('source')
        if source_name:
            queryset = queryset.filter(source__name__icontains=source_name)
        
        # Date range filtering
        days_back = self.request.query_params.get('days_back')
        if days_back:
            try:
                days = int(days_back)
                cutoff_date = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(created_at__gte=cutoff_date)
            except ValueError:
                pass
        
        # Deadline filtering
        has_deadline = self.request.query_params.get('has_deadline')
        if has_deadline == 'true':
            queryset = queryset.filter(application_end_date__isnull=False)
        elif has_deadline == 'false':
            queryset = queryset.filter(application_end_date__isnull=True)
        
        # Expiring soon filter
        expiring_soon = self.request.query_params.get('expiring_soon')
        if expiring_soon == 'true':
            next_week = timezone.now().date() + timedelta(days=7)
            queryset = queryset.filter(
                application_end_date__isnull=False,
                application_end_date__lte=next_week,
                application_end_date__gte=timezone.now().date()
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest job postings."""
        latest_jobs = self.get_queryset()[:10]
        serializer = JobPostingListSerializer(latest_jobs, many=True)
        return Response({
            'count': len(latest_jobs),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending job postings (most viewed/popular)."""
        # For now, return recent jobs with high post counts
        trending_jobs = self.get_queryset().filter(
            total_posts__gte=10
        ).order_by('-total_posts', '-created_at')[:10]
        
        serializer = JobPostingListSerializer(trending_jobs, many=True)
        return Response({
            'count': len(trending_jobs),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get jobs expiring within next 7 days."""
        next_week = timezone.now().date() + timedelta(days=7)
        expiring_jobs = self.get_queryset().filter(
            application_end_date__isnull=False,
            application_end_date__lte=next_week,
            application_end_date__gte=timezone.now().date()
        ).order_by('application_end_date')
        
        serializer = JobPostingListSerializer(expiring_jobs, many=True)
        return Response({
            'count': len(expiring_jobs),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get jobs grouped by category."""
        categories = JobCategory.objects.all().order_by('position')
        result = {}
        
        for category in categories:
            jobs = self.get_queryset().filter(category=category)[:5]
            result[category.slug] = {
                'name': category.name,
                'count': jobs.count(),
                'jobs': JobPostingListSerializer(jobs, many=True).data
            }
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Get similar jobs to the current one."""
        job = self.get_object()
        
        similar_jobs = self.get_queryset().filter(
            category=job.category
        ).exclude(id=job.id).order_by('-created_at')[:5]
        
        serializer = JobPostingListSerializer(similar_jobs, many=True)
        return Response({
            'count': len(similar_jobs),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced search endpoint with detailed parameters."""
        search_serializer = JobSearchSerializer(data=request.data)
        
        if not search_serializer.is_valid():
            return Response(
                search_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Apply search filters
        queryset = self.get_queryset()
        search_data = search_serializer.validated_data
        
        # Text search
        if search_data.get('q'):
            query = search_data['q']
            queryset = queryset.filter(
                models.Q(title__icontains=query) |
                models.Q(description__icontains=query) |
                models.Q(department__icontains=query) |
                models.Q(keywords__icontains=query)
            )
        
        # Apply other filters
        for field, value in search_data.items():
            if value and field != 'q':
                if field == 'category':
                    queryset = queryset.filter(category__slug=value)
                elif field == 'source':
                    queryset = queryset.filter(source__name__icontains=value)
                elif field == 'posted_after':
                    queryset = queryset.filter(created_at__date__gte=value)
                elif field == 'posted_before':
                    queryset = queryset.filter(created_at__date__lte=value)
                elif field == 'deadline_after':
                    queryset = queryset.filter(application_end_date__gte=value)
                elif field == 'deadline_before':
                    queryset = queryset.filter(application_end_date__lte=value)
                # Add more filter logic as needed
        
        # Apply ordering
        ordering = search_data.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        # Paginate results
        page_size = search_data.get('page_size', 20)
        page = search_data.get('page', 1)
        
        paginator = StandardResultsSetPagination()
        paginator.page_size = page_size
        
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = JobPostingListSerializer(paginated_queryset, many=True)
        
        return paginator.get_paginated_response(serializer.data)


class JobCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for job categories.
    
    Provides category information with job counts and statistics.
    """
    
    queryset = JobCategory.objects.all().order_by('position')
    serializer_class = JobCategorySerializer
    lookup_field = 'slug'
    
    @action(detail=True, methods=['get'])
    def jobs(self, request, slug=None):
        """Get jobs for a specific category."""
        category = self.get_object()
        
        jobs_queryset = JobPosting.objects.filter(
            category=category,
            status__in=['announced', 'admit_card', 'answer_key', 'result']
        ).select_related('source').order_by('-created_at')
        
        # Apply pagination
        paginator = StandardResultsSetPagination()
        paginated_jobs = paginator.paginate_queryset(jobs_queryset, request)
        
        serializer = JobPostingListSerializer(paginated_jobs, many=True)
        return paginator.get_paginated_response(serializer.data)


class StatsAPIView(APIView):
    """
    API endpoint for general statistics and dashboard data.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get comprehensive statistics."""
        # Check cache first
        cache_key = 'api_stats'
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return Response(cached_stats)
        
        # Calculate fresh statistics
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Job statistics
        total_jobs = JobPosting.objects.count()
        active_jobs = JobPosting.objects.filter(
            status__in=['announced', 'admit_card', 'answer_key', 'result']
        ).count()
        
        new_jobs_today = JobPosting.objects.filter(
            created_at__date=today
        ).count()
        
        new_jobs_this_week = JobPosting.objects.filter(
            created_at__date__gte=week_ago
        ).count()
        
        # Source statistics
        sources_active = GovernmentSource.objects.filter(
            active=True,
            status='active'
        ).count()
        
        # Category statistics
        categories_count = JobCategory.objects.count()
        
        # Jobs by status
        jobs_by_status = {}
        for status_code, status_name in JobPosting.STATUS_CHOICES:
            count = JobPosting.objects.filter(status=status_code).count()
            jobs_by_status[status_code] = {
                'name': status_name,
                'count': count
            }
        
        # Jobs by category
        jobs_by_category = {}
        for category in JobCategory.objects.all():
            count = JobPosting.objects.filter(
                category=category,
                status__in=['announced', 'admit_card', 'answer_key', 'result']
            ).count()
            jobs_by_category[category.slug] = {
                'name': category.name,
                'count': count
            }
        
        # Recent scrape logs
        recent_scrapes = ScrapeLog.objects.select_related('source').order_by(
            '-started_at'
        )[:5]
        
        stats_data = {
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'new_jobs_today': new_jobs_today,
            'new_jobs_this_week': new_jobs_this_week,
            'sources_active': sources_active,
            'categories_count': categories_count,
            'jobs_by_status': jobs_by_status,
            'jobs_by_category': jobs_by_category,
            'recent_scrapes': ScrapeLogSerializer(recent_scrapes, many=True).data
        }
        
        # Cache for 30 minutes
        cache.set(cache_key, stats_data, 30 * 60)
        
        serializer = StatsSerializer(stats_data)
        return Response(serializer.data)


class ContactAPIView(APIView):
    """
    API endpoint for contact form submissions.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Handle contact form submission."""
        serializer = ContactFormSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process contact form (save to database, send email, etc.)
        contact_data = serializer.validated_data
        
        # Log the contact submission
        logger.info(f"Contact form submission: {contact_data['email']} - {contact_data['subject']}")
        
        # Here you would typically:
        # 1. Save to ContactSubmission model
        # 2. Send email notification
        # 3. Send auto-reply to user
        
        return Response({
            'success': True,
            'message': 'Thank you for your message. We will get back to you soon!'
        })


class NewsletterAPIView(APIView):
    """
    API endpoint for newsletter subscriptions.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Handle newsletter subscription."""
        serializer = NewsletterSubscriptionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subscription_data = serializer.validated_data
        
        # Process subscription (check for existing, save to database)
        logger.info(f"Newsletter subscription: {subscription_data['email']}")
        
        # Here you would typically:
        # 1. Check if email already exists
        # 2. Save to NewsletterSubscription model
        # 3. Send confirmation email
        
        return Response({
            'success': True,
            'message': 'Successfully subscribed to newsletter!'
        })


class JobAlertAPIView(APIView):
    """
    API endpoint for job alert subscriptions.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Handle job alert subscription."""
        serializer = JobAlertSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alert_data = serializer.validated_data
        
        # Process job alert subscription
        logger.info(f"Job alert subscription: {alert_data['email']} - {alert_data['keywords']}")
        
        # Here you would typically:
        # 1. Save to JobAlert model
        # 2. Set up background task to monitor for matching jobs
        # 3. Send confirmation email
        
        return Response({
            'success': True,
            'message': 'Job alert created successfully! You will receive notifications for matching jobs.'
        })


class HealthCheckAPIView(APIView):
    """
    Health check endpoint for monitoring.
    
    Returns system status and basic metrics.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request) -> Response:
        """Get system health status."""
        try:
            # Basic database check
            job_count = JobPosting.objects.count()
            source_count = GovernmentSource.objects.count()
            
            # Check recent activity
            recent_jobs = JobPosting.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count()
            
            health_data = {
                'status': 'healthy',
                'timestamp': timezone.now().isoformat(),
                'metrics': {
                    'total_jobs': job_count,
                    'total_sources': source_count,
                    'jobs_last_24h': recent_jobs,
                },
                'version': '1.0.0'
            }
            
            return Response(health_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return Response(
                {
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class TrendingJobsAPIView(ListAPIView):
    """
    API view for trending job postings.
    
    Returns jobs with high engagement and recent activity.
    """
    
    serializer_class = JobPostingListSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get trending jobs based on posts and recency."""
        week_ago = timezone.now() - timedelta(days=7)
        
        return JobPosting.objects.filter(
            status__in=['announced', 'admit_card'],
            created_at__gte=week_ago,
            total_posts__gte=20
        ).select_related(
            'source', 'category'
        ).order_by('-total_posts', '-created_at')[:50]


class RecentJobsAPIView(ListAPIView):
    """
    API view for recently posted jobs.
    
    Returns the most recent job postings.
    """
    
    serializer_class = JobPostingListSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get recently posted jobs."""
        return JobPosting.objects.filter(
            status__in=['announced', 'admit_card', 'answer_key', 'result']
        ).select_related(
            'source', 'category'
        ).order_by('-created_at')[:100]


class FeaturedJobsAPIView(ListAPIView):
    """
    API view for featured job postings.
    
    Returns jobs marked as featured or high-value positions.
    """
    
    serializer_class = JobPostingListSerializer
    permission_classes = [AllowAny]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        """Get featured jobs."""
        return JobPosting.objects.filter(
            status__in=['announced', 'admit_card'],
            total_posts__gte=50  # High number of posts indicates important jobs
        ).select_related(
            'source', 'category'
        ).order_by('-total_posts', '-created_at')[:25]


class SitemapAPIView(APIView):
    """
    API view for generating sitemap data.
    
    Returns URLs for SEO optimization.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request) -> Response:
        """Generate sitemap data."""
        try:
            # Get active jobs
            jobs = JobPosting.objects.filter(
                status__in=['announced', 'admit_card', 'answer_key', 'result']
            ).select_related('category').values(
                'slug', 'updated_at', 'category__slug'
            )
            
            # Get categories
            categories = JobCategory.objects.filter(
                active=True
            ).values('slug', 'updated_at')
            
            sitemap_data = {
                'jobs': [
                    {
                        'url': f'/jobs/{job["slug"]}',
                        'lastmod': job['updated_at'].isoformat(),
                        'changefreq': 'weekly',
                        'priority': '0.8'
                    }
                    for job in jobs
                ],
                'categories': [
                    {
                        'url': f'/category/{cat["slug"]}',
                        'lastmod': cat['updated_at'].isoformat(),
                        'changefreq': 'daily',
                        'priority': '0.9'
                    }
                    for cat in categories
                ],
                'static_pages': [
                    {
                        'url': '/',
                        'changefreq': 'daily',
                        'priority': '1.0'
                    },
                    {
                        'url': '/about',
                        'changefreq': 'monthly',
                        'priority': '0.5'
                    },
                    {
                        'url': '/contact',
                        'changefreq': 'monthly',
                        'priority': '0.5'
                    }
                ]
            }
            
            return Response(sitemap_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Sitemap generation failed: {e}")
            return Response(
                {'error': 'Failed to generate sitemap'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class JobFeedAPIView(APIView):
    """
    API view for RSS/Atom feed data.
    
    Returns job data formatted for feed consumption.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request) -> Response:
        """Generate feed data."""
        try:
            # Get recent jobs for feed
            jobs = JobPosting.objects.filter(
                status__in=['announced', 'admit_card']
            ).select_related(
                'source', 'category'
            ).order_by('-created_at')[:50]
            
            feed_data = {
                'title': 'SarkariBot - Latest Government Jobs',
                'description': 'Latest government job notifications from SarkariBot',
                'link': request.build_absolute_uri('/'),
                'updated': timezone.now().isoformat(),
                'items': [
                    {
                        'title': job.title,
                        'description': job.description[:200] + '...' if len(job.description) > 200 else job.description,
                        'link': request.build_absolute_uri(f'/jobs/{job.slug}'),
                        'guid': f'job-{job.id}',
                        'published': job.created_at.isoformat(),
                        'category': job.category.name if job.category else 'General',
                        'source': job.source.name,
                        'total_posts': job.total_posts,
                        'last_date': job.application_end_date.isoformat() if job.application_end_date else None
                    }
                    for job in jobs
                ]
            }
            
            return Response(feed_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Feed generation failed: {e}")
            return Response(
                {'error': 'Failed to generate feed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
