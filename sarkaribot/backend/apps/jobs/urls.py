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
    # NewsletterAPIView,  # Comment out if not implemented yet
    # JobAlertAPIView,    # Comment out if not implemented yet
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
    path('stats/', StatsAPIView.as_view(), name='stats'),
    path('contact/', ContactAPIView.as_view(), name='contact'),
    # path('newsletter/', NewsletterSubscriptionAPIView.as_view(), name='newsletter'),  # Comment out if not implemented
    # path('job-alerts/', JobAlertAPIView.as_view(), name='job-alerts'),  # Comment out if not implemented
    path('health/', HealthCheckAPIView.as_view(), name='health'),
    
    # Special job listing endpoints - THESE MUST COME BEFORE router.urls
    path('jobs/trending/', TrendingJobsAPIView.as_view(), name='trending-jobs'),
    path('jobs/recent/', RecentJobsAPIView.as_view(), name='recent-jobs'),
    path('jobs/featured/', FeaturedJobsAPIView.as_view(), name='featured-jobs'),
    
    # Router URLs (includes CRUD operations) - MUST COME AFTER specific endpoints
    path('', include(router.urls)),
    
    # SEO and feed endpoints
    path('sitemap/', SitemapAPIView.as_view(), name='sitemap'),
    path('feed/', JobFeedAPIView.as_view(), name='job-feed'),
    
    # Category-specific job endpoints
    path('categories/<slug:category_slug>/jobs/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         name='category-jobs'),
    
    # Status-specific job endpoints
    path('jobs/latest/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'status': 'announced'}, 
         name='latest-jobs'),
    
    path('jobs/admit-card/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'status': 'admit_card'}, 
         name='admit-card-jobs'),
    
    path('jobs/answer-key/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'status': 'answer_key'}, 
         name='answer-key-jobs'),
    
    path('jobs/result/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'status': 'result'}, 
         name='result-jobs'),
]

# Additional URL patterns for specific use cases
extra_patterns = [
    # Search endpoints
    path('search/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         name='job-search'),
    
    # Government source endpoints
    path('sources/<str:source_name>/jobs/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         name='source-jobs'),
    
    # Date-based endpoints
    path('jobs/today/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'posted_today': True}, 
         name='jobs-today'),
    
    path('jobs/this-week/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'posted_this_week': True}, 
         name='jobs-this-week'),
    
    # Deadline-based endpoints
    path('jobs/deadline-soon/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'deadline_soon': True}, 
         name='jobs-deadline-soon'),
    
    path('jobs/deadline-today/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'deadline_today': True}, 
         name='jobs-deadline-today'),
    
    # Special filters
    path('jobs/high-posts/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'high_posts': True}, 
         name='jobs-high-posts'),
    
    path('jobs/free-application/', 
         JobPostingViewSet.as_view({'get': 'list'}), 
         {'free_application': True}, 
         name='jobs-free-application'),
]

urlpatterns += extra_patterns
