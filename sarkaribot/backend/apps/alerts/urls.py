"""
URL configuration for the alerts app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobAlertViewSet,
    JobBookmarkViewSet,
    JobApplicationViewSet,
    UserNotificationPreferenceViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'alerts', JobAlertViewSet, basename='jobalert')
router.register(r'bookmarks', JobBookmarkViewSet, basename='jobbookmark')
router.register(r'applications', JobApplicationViewSet, basename='jobapplication')
router.register(r'preferences', UserNotificationPreferenceViewSet, basename='notificationpreference')

app_name = 'alerts'

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
