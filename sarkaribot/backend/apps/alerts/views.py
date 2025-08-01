"""
Advanced Job Alert API Views
REST API endpoints for managing job alerts, bookmarks, and applications.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from .models import JobAlert, JobAlertLog, JobBookmark, JobApplication, UserNotificationPreference
from .services import JobAlertService, BookmarkService, ApplicationTrackingService
from .serializers import (
    JobAlertSerializer,
    JobAlertLogSerializer,
    JobBookmarkSerializer,
    JobApplicationSerializer,
    UserNotificationPreferenceSerializer,
    JobAlertCreateSerializer,
    JobAlertUpdateSerializer
)
import logging

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class JobAlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job alerts.
    """
    serializer_class = JobAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['frequency', 'delivery_method', 'is_active']
    
    def get_queryset(self):
        """Filter alerts by current user."""
        return JobAlert.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return JobAlertCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return JobAlertUpdateSerializer
        return JobAlertSerializer
    
    def perform_create(self, serializer):
        """Create alert with current user."""
        alert_service = JobAlertService()
        alert_data = serializer.validated_data
        alert = alert_service.create_alert(self.request.user, alert_data)
        return alert
    
    def create(self, request, *args, **kwargs):
        """Create a new job alert."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            alert = self.perform_create(serializer)
            response_serializer = JobAlertSerializer(alert)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error creating job alert: {e}")
            return Response(
                {'error': 'Failed to create job alert'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def test_alert(self, request, pk=None):
        """Test an alert to see matching jobs."""
        try:
            alert = self.get_object()
            matching_jobs = alert.get_matching_jobs()
            
            return Response({
                'matching_jobs_count': matching_jobs.count(),
                'preview_jobs': [
                    {
                        'id': job.id,
                        'title': job.title,
                        'source': job.source.name,
                        'category': job.category.name,
                        'created_at': job.created_at
                    }
                    for job in matching_jobs[:5]
                ]
            })
        except Exception as e:
            logger.error(f"Error testing alert {pk}: {e}")
            return Response(
                {'error': 'Failed to test alert'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def trigger_now(self, request, pk=None):
        """Manually trigger an alert to send now."""
        try:
            alert = self.get_object()
            
            if not alert.is_active:
                return Response(
                    {'error': 'Alert is not active'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Import here to avoid circular imports
            from .services import send_instant_alert_task
            
            # Queue the task
            task = send_instant_alert_task.delay(str(alert.id))
            
            return Response({
                'message': 'Alert triggered successfully',
                'task_id': task.id
            })
        except Exception as e:
            logger.error(f"Error triggering alert {pk}: {e}")
            return Response(
                {'error': 'Failed to trigger alert'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get logs for a specific alert."""
        try:
            alert = self.get_object()
            logs = JobAlertLog.objects.filter(alert=alert).order_by('-sent_at')
            
            page = self.paginate_queryset(logs)
            if page is not None:
                serializer = JobAlertLogSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = JobAlertLogSerializer(logs, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting alert logs for {pk}: {e}")
            return Response(
                {'error': 'Failed to get alert logs'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get alert statistics for the user."""
        try:
            user_alerts = self.get_queryset()
            
            stats = {
                'total_alerts': user_alerts.count(),
                'active_alerts': user_alerts.filter(is_active=True).count(),
                'inactive_alerts': user_alerts.filter(is_active=False).count(),
                'frequency_breakdown': dict(
                    user_alerts.values('frequency').annotate(count=Count('id')).values_list('frequency', 'count')
                ),
                'delivery_method_breakdown': dict(
                    user_alerts.values('delivery_method').annotate(count=Count('id')).values_list('delivery_method', 'count')
                ),
                'recent_logs': JobAlertLogSerializer(
                    JobAlertLog.objects.filter(
                        alert__user=request.user
                    ).order_by('-sent_at')[:10],
                    many=True
                ).data
            }
            
            return Response(stats)
        except Exception as e:
            logger.error(f"Error getting alert statistics: {e}")
            return Response(
                {'error': 'Failed to get statistics'},
                status=status.HTTP_400_BAD_REQUEST
            )


class JobBookmarkViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job bookmarks.
    """
    serializer_class = JobBookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter bookmarks by current user."""
        return JobBookmark.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create bookmark with current user."""
        bookmark_service = BookmarkService()
        job_id = serializer.validated_data['job'].id
        notes = serializer.validated_data.get('notes', '')
        
        bookmark = bookmark_service.bookmark_job(
            self.request.user,
            job_id,
            notes
        )
        return bookmark
    
    def create(self, request, *args, **kwargs):
        """Create a new bookmark."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            bookmark = self.perform_create(serializer)
            response_serializer = JobBookmarkSerializer(bookmark)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error creating bookmark: {e}")
            return Response(
                {'error': 'Failed to create bookmark'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Bulk delete bookmarks."""
        try:
            bookmark_ids = request.data.get('bookmark_ids', [])
            
            if not bookmark_ids:
                return Response(
                    {'error': 'No bookmark IDs provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            deleted_count, _ = JobBookmark.objects.filter(
                user=request.user,
                id__in=bookmark_ids
            ).delete()
            
            return Response({
                'message': f'Deleted {deleted_count} bookmarks',
                'deleted_count': deleted_count
            })
        except Exception as e:
            logger.error(f"Error bulk deleting bookmarks: {e}")
            return Response(
                {'error': 'Failed to delete bookmarks'},
                status=status.HTTP_400_BAD_REQUEST
            )


class JobApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job applications.
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    
    def get_queryset(self):
        """Filter applications by current user."""
        return JobApplication.objects.filter(user=self.request.user).order_by('-updated_at')
    
    def perform_create(self, serializer):
        """Create application with current user."""
        tracking_service = ApplicationTrackingService()
        job_id = serializer.validated_data['job'].id
        status_value = serializer.validated_data.get('status', 'interested')
        
        application = tracking_service.track_application(
            self.request.user,
            job_id,
            status_value,
            **{k: v for k, v in serializer.validated_data.items() if k not in ['job']}
        )
        return application
    
    def create(self, request, *args, **kwargs):
        """Create a new application tracking entry."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            application = self.perform_create(serializer)
            response_serializer = JobApplicationSerializer(application)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error creating application: {e}")
            return Response(
                {'error': 'Failed to create application'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get application statistics for the user."""
        try:
            user_applications = self.get_queryset()
            
            stats = {
                'total_applications': user_applications.count(),
                'status_breakdown': dict(
                    user_applications.values('status').annotate(count=Count('id')).values_list('status', 'count')
                ),
                'recent_applications': JobApplicationSerializer(
                    user_applications[:10],
                    many=True
                ).data
            }
            
            return Response(stats)
        except Exception as e:
            logger.error(f"Error getting application statistics: {e}")
            return Response(
                {'error': 'Failed to get statistics'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserNotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notification preferences.
    """
    serializer_class = UserNotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch']  # No create/delete, only update
    
    def get_object(self):
        """Get or create notification preferences for the current user."""
        preference, created = UserNotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference
    
    def list(self, request, *args, **kwargs):
        """Return the user's notification preferences."""
        preference = self.get_object()
        serializer = self.get_serializer(preference)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update notification preferences."""
        try:
            preference = self.get_object()
            serializer = self.get_serializer(preference, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error updating notification preferences: {e}")
            return Response(
                {'error': 'Failed to update preferences'},
                status=status.HTTP_400_BAD_REQUEST
            )
