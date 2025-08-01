"""
URL routing for jobs app API endpoints.

This module defines all URL patterns for the jobs API,
including REST endpoints and custom views.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobPostingViewSet,
    JobCategoryViewSet,
    StatsAPIView,
    ContactAPIView,
    NewsletterAPIView,
    JobAlertAPIView,
    HealthCheckAPIView,
    TrendingJobsAPIView,
    RecentJobsAPIView,
    FeaturedJobsAPIView,
    SitemapAPIView,
    JobFeedAPIView,
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'jobs', JobPostingViewSet, basename='jobposting')
router.register(r'categories', JobCategoryViewSet, basename='jobcategory')

app_name = 'jobs'

urlpatterns = [
    # IMPORTANT: Specific endpoints MUST come BEFORE generic router patterns
    
    # Custom API endpoints (non-jobs)
    path('api/v1/stats/', StatsAPIView.as_view(), name='stats'),
    path('api/v1/contact/', ContactAPIView.as_view(), name='contact'),
    path('api/v1/newsletter/', NewsletterAPIView.as_view(), name='newsletter'),
    path('api/v1/job-alerts/', JobAlertAPIView.as_view(), name='job-alerts'),
    path('api/v1/health/', HealthCheckAPIView.as_view(), name='health'),
    
    # Special job listing endpoints - THESE MUST COME BEFORE router.urls
    path('api/v1/jobs/trending/', TrendingJobsAPIView.as_view(), name='trending-jobs'),
    path('api/v1/jobs/recent/', RecentJobsAPIView.as_view(), name='recent-jobs'),
    path('api/v1/jobs/featured/', FeaturedJobsAPIView.as_view(), name='featured-jobs'),
    
    # Router URLs (includes CRUD operations) - MUST COME AFTER specific endpoints
    path('api/v1/', include(router.urls)),
    
    # SEO and feed endpoints
    path('api/v1/sitemap/', SitemapAPIView.as_view(), name='sitemap'),
    path('api/v1/feed/', JobFeedAPIView.as_view(), name='job-feed'),
    
    # Category-specific job endpoints
    path('api/v1/categories/<slug:category_slug>/jobs/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         name='category-jobs'),
    
    # Status-specific job endpoints
    path('api/v1/jobs/latest/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'status': 'announced'}, 
         name='latest-jobs'),
    
    path('api/v1/jobs/admit-card/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'status': 'admit_card'}, 
         name='admit-card-jobs'),
    
    path('api/v1/jobs/answer-key/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'status': 'answer_key'}, 
         name='answer-key-jobs'),
    
    path('api/v1/jobs/result/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'status': 'result'}, 
         name='result-jobs'),
]

# Additional URL patterns for specific use cases
extra_patterns = [
    # Search endpoints
    path('api/v1/search/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         name='job-search'),
    
    # Government source endpoints
    path('api/v1/sources/<str:source_name>/jobs/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         name='source-jobs'),
    
    # Date-based endpoints
    path('api/v1/jobs/today/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'posted_today': True}, 
         name='jobs-today'),
    
    path('api/v1/jobs/this-week/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'posted_this_week': True}, 
         name='jobs-this-week'),
    
    # Deadline-based endpoints
    path('api/v1/jobs/deadline-soon/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'deadline_soon': True}, 
         name='jobs-deadline-soon'),
    
    path('api/v1/jobs/deadline-today/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'deadline_today': True}, 
         name='jobs-deadline-today'),
    
    # Special filters
    path('api/v1/jobs/high-posts/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'high_posts': True}, 
         name='jobs-high-posts'),
    
    path('api/v1/jobs/free-application/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'free_application': True}, 
         name='jobs-free-application'),
]

urlpatterns += extra_patterns
