"""
URL routing for sources app API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GovernmentSourceViewSet, SourceStatisticsViewSet

app_name = 'sources'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'', GovernmentSourceViewSet, basename='governmentsource')
router.register(r'statistics', SourceStatisticsViewSet, basename='sourcestatistics')

urlpatterns = [
    path('', include(router.urls)),
]
