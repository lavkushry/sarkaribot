"""
AI Search URL Configuration for SarkariBot
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AISearchViewSet, SearchProfileViewSet, 
    SearchAnalyticsViewSet, SearchManagementViewSet
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'ai', AISearchViewSet, basename='ai-search')
router.register(r'profile', SearchProfileViewSet, basename='search-profile')
router.register(r'analytics', SearchAnalyticsViewSet, basename='search-analytics')
router.register(r'management', SearchManagementViewSet, basename='search-management')

app_name = 'ai_search'

urlpatterns = [
    path('api/', include(router.urls)),
]
