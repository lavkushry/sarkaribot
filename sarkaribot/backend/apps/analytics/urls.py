"""
Analytics URL Configuration for SarkariBot
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyticsViewSet, DailyStatsViewSet, UserSessionViewSet

# Create router for viewsets
router = DefaultRouter()
router.register(r'overview', AnalyticsViewSet, basename='analytics')
router.register(r'daily-stats', DailyStatsViewSet, basename='daily-stats')
router.register(r'sessions', UserSessionViewSet, basename='user-sessions')

app_name = 'analytics'

urlpatterns = [
    path('api/', include(router.urls)),
]
