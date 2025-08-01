"""
URL configuration for SEO app.

Provides endpoints for SEO metadata management, keyword tracking,
sitemap generation, and analytics according to Knowledge.md specifications.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SEOMetadataViewSet, KeywordTrackingViewSet, SitemapEntryViewSet,
    SEOAuditLogViewSet, SEOGenerateView, SEOAnalyzeView
)

app_name = 'seo'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'metadata', SEOMetadataViewSet)
router.register(r'keywords', KeywordTrackingViewSet)
router.register(r'sitemap', SitemapEntryViewSet)
router.register(r'audit-logs', SEOAuditLogViewSet)

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Custom API endpoints
    path('generate/', SEOGenerateView.as_view(), name='generate'),
    path('analyze/', SEOAnalyzeView.as_view(), name='analyze'),
]
