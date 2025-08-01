"""
URL routing for scraping app API endpoints.

This module defines all URL patterns for the scraping API,
including scraping control, monitoring, and analytics endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ScrapeLogViewSet,
    ScrapedDataViewSet,
    SourceStatisticsViewSet,
    ScrapingControlAPIView,
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'logs', ScrapeLogViewSet, basename='scrapelog')
router.register(r'data', ScrapedDataViewSet, basename='scrapeddata')
router.register(r'statistics', SourceStatisticsViewSet, basename='sourcestatistics')

app_name = 'scraping'

urlpatterns = [
    # Router URLs (includes CRUD operations)
    path('', include(router.urls)),
    
    # Scraping control endpoints
    path('control/', ScrapingControlAPIView.as_view(), name='scraping-control'),
]
