"""
SEO-optimized URL patterns for SarkariBot.

This module defines URL patterns following the Knowledge.md specification:
- /{category}/{job-slug}/ - Individual job detail pages
- /{category}/ - Category listing pages

These URLs are optimized for search engines and provide clean, 
readable URLs for better SEO performance.
"""

from django.urls import path, re_path
from .seo_views import (
    JobDetailSEOView,
    CategoryListSEOView,
    job_detail_redirect_view,
    category_list_view
)

app_name = 'jobs_seo'

urlpatterns = [
    # Category listing pages: /{category}/
    # Examples: /latest-jobs/, /admit-card/, /answer-key/, /result/
    path('<slug:category_slug>/', 
         category_list_view, 
         name='category-list'),
    
    # Job detail pages: /{category}/{job-slug}/
    # Examples: /latest-jobs/ssc-cgl-2025-notification/
    path('<slug:category_slug>/<slug:job_slug>/', 
         job_detail_redirect_view, 
         name='job-detail'),
]

# Additional URL patterns for redirects and compatibility
extra_patterns = [
    # Alternative patterns using class-based views (if needed)
    # path('<slug:category_slug>/list/', 
    #      CategoryListSEOView.as_view(), 
    #      name='category-list-cbv'),
    
    # path('<slug:category_slug>/<slug:job_slug>/detail/', 
    #      JobDetailSEOView.as_view(), 
    #      name='job-detail-cbv'),
]

# We'll add these if needed for backward compatibility
# urlpatterns += extra_patterns