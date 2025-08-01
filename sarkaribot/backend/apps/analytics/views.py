"""
Analytics Views for SarkariBot
Provides API endpoints for analytics and reporting.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Count, Q
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

from .models import (
    PageView, JobView, SearchQuery, UserSession,
    AlertEngagement, PerformanceMetric, DailyStats
)
from .services import AnalyticsService, ReportingService, DailyStatsService
from .serializers import (
    PageViewSerializer, JobViewSerializer, SearchQuerySerializer,
    UserSessionSerializer, DailyStatsSerializer, PerformanceMetricSerializer
)

logger = logging.getLogger(__name__)


class AnalyticsViewSet(viewsets.ViewSet):
    """
    Analytics API endpoints for admin dashboard.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def traffic_overview(self, request):
        """
        Get traffic overview analytics.
        
        Query Parameters:
        - days: Number of days to analyze (default: 30)
        """
        try:
            days = int(request.query_params.get('days', 30))
            if days > 365:
                days = 365  # Limit to 1 year
            
            data = ReportingService.get_traffic_overview(days)
            return Response(data, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response(
                {'error': 'Invalid days parameter'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Failed to get traffic overview: {e}")
            return Response(
                {'error': 'Failed to retrieve traffic data'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 15))
    def job_analytics(self, request):
        """
        Get job-related analytics.
        
        Query Parameters:
        - days: Number of days to analyze (default: 30)
        """
        try:
            days = int(request.query_params.get('days', 30))
            if days > 365:
                days = 365
            
            data = ReportingService.get_job_analytics(days)
            return Response(data, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response(
                {'error': 'Invalid days parameter'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Failed to get job analytics: {e}")
            return Response(
                {'error': 'Failed to retrieve job analytics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 15))
    def search_analytics(self, request):
        """
        Get search analytics and insights.
        
        Query Parameters:
        - days: Number of days to analyze (default: 30)
        """
        try:
            days = int(request.query_params.get('days', 30))
            if days > 365:
                days = 365
            
            data = ReportingService.get_search_analytics(days)
            return Response(data, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response(
                {'error': 'Invalid days parameter'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Failed to get search analytics: {e}")
            return Response(
                {'error': 'Failed to retrieve search analytics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 15))
    def conversion_funnel(self, request):
        """
        Get conversion funnel analysis.
        
        Query Parameters:
        - days: Number of days to analyze (default: 30)
        """
        try:
            days = int(request.query_params.get('days', 30))
            if days > 365:
                days = 365
            
            data = ReportingService.get_conversion_funnel(days)
            return Response(data, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response(
                {'error': 'Invalid days parameter'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Failed to get conversion funnel: {e}")
            return Response(
                {'error': 'Failed to retrieve conversion funnel'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 30))  # Cache for 30 minutes
    def realtime_stats(self, request):
        """
        Get real-time statistics for the last 24 hours.
        """
        try:
            now = datetime.now()
            yesterday = now - timedelta(hours=24)
            
            # Get recent activity
            recent_page_views = PageView.objects.filter(
                created_at__gte=yesterday
            ).count()
            
            active_sessions = UserSession.objects.filter(
                last_activity__gte=now - timedelta(minutes=30)
            ).count()
            
            recent_job_views = JobView.objects.filter(
                created_at__gte=yesterday
            ).count()
            
            recent_searches = SearchQuery.objects.filter(
                created_at__gte=yesterday
            ).count()
            
            # Hourly breakdown for the last 24 hours
            hourly_data = []
            for i in range(24):
                hour_start = now - timedelta(hours=i+1)
                hour_end = now - timedelta(hours=i)
                
                hour_page_views = PageView.objects.filter(
                    created_at__gte=hour_start,
                    created_at__lt=hour_end
                ).count()
                
                hourly_data.append({
                    'hour': hour_start.strftime('%H:00'),
                    'page_views': hour_page_views
                })
            
            hourly_data.reverse()  # Chronological order
            
            data = {
                'period': '24 hours',
                'realtime': {
                    'active_sessions': active_sessions,
                    'page_views_24h': recent_page_views,
                    'job_views_24h': recent_job_views,
                    'searches_24h': recent_searches,
                },
                'hourly_breakdown': hourly_data
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get realtime stats: {e}")
            return Response(
                {'error': 'Failed to retrieve realtime stats'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 60))  # Cache for 1 hour
    def performance_metrics(self, request):
        """
        Get system performance metrics.
        
        Query Parameters:
        - days: Number of days to analyze (default: 7)
        - metric_type: Type of metric to filter by
        """
        try:
            days = int(request.query_params.get('days', 7))
            metric_type = request.query_params.get('metric_type', '')
            
            if days > 90:
                days = 90  # Limit to 90 days for performance data
            
            start_date = datetime.now() - timedelta(days=days)
            
            queryset = PerformanceMetric.objects.filter(
                recorded_at__gte=start_date
            )
            
            if metric_type:
                queryset = queryset.filter(metric_type=metric_type)
            
            # Get metrics summary
            metrics_summary = queryset.values('metric_type').annotate(
                count=Count('id'),
                avg_value=models.Avg('value'),
                min_value=models.Min('value'),
                max_value=models.Max('value')
            ).order_by('metric_type')
            
            # Get available metric types
            metric_types = PerformanceMetric.objects.values_list(
                'metric_type', flat=True
            ).distinct()
            
            data = {
                'period': {
                    'days': days,
                    'start_date': start_date.date(),
                    'end_date': datetime.now().date()
                },
                'metric_types': list(metric_types),
                'summary': list(metrics_summary),
                'details': PerformanceMetricSerializer(
                    queryset[:1000], many=True
                ).data  # Limit to last 1000 records
            }
            
            return Response(data, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response(
                {'error': 'Invalid parameters'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return Response(
                {'error': 'Failed to retrieve performance metrics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def track_event(self, request):
        """
        Track a custom analytics event.
        
        Body:
        {
            "event_type": "page_view|job_view|search|conversion",
            "data": {...}
        }
        """
        try:
            event_type = request.data.get('event_type')
            event_data = request.data.get('data', {})
            
            if event_type == 'page_view':
                path = event_data.get('path', '')
                page_title = event_data.get('page_title', '')
                metadata = event_data.get('metadata', {})
                
                AnalyticsService.track_page_view(
                    request, path, page_title, metadata
                )
                
            elif event_type == 'conversion':
                stage = event_data.get('stage', '')
                job_id = event_data.get('job_id')
                source_stage = event_data.get('source_stage')
                metadata = event_data.get('metadata', {})
                
                AnalyticsService.track_conversion(
                    request, stage, job_id, source_stage, metadata
                )
                
            else:
                return Response(
                    {'error': 'Invalid event type'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(
                {'message': 'Event tracked successfully'}, 
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Failed to track event: {e}")
            return Response(
                {'error': 'Failed to track event'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DailyStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Daily statistics API endpoints.
    """
    queryset = DailyStats.objects.all()
    serializer_class = DailyStatsSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Filter daily stats by date range."""
        queryset = super().get_queryset()
        
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass
        
        return queryset.order_by('-date')
    
    @action(detail=False, methods=['post'])
    def generate_stats(self, request):
        """
        Generate daily stats for a specific date.
        
        Body:
        {
            "date": "2023-12-01"  # Optional, defaults to yesterday
        }
        """
        try:
            date_str = request.data.get('date')
            target_date = None
            
            if date_str:
                try:
                    target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            daily_stats = DailyStatsService.generate_daily_stats(target_date)
            
            if daily_stats:
                serializer = self.get_serializer(daily_stats)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Failed to generate daily stats'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Failed to generate daily stats: {e}")
            return Response(
                {'error': 'Failed to generate daily stats'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User session analytics API.
    """
    queryset = UserSession.objects.all()
    serializer_class = UserSessionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        """Filter sessions by date range and user."""
        queryset = super().get_queryset()
        
        # Date filtering
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(start_time__gte=start_date)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                end_date = end_date + timedelta(days=1)  # Include full day
                queryset = queryset.filter(start_time__lt=end_date)
            except ValueError:
                pass
        
        # User filtering
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Device filtering
        device_type = self.request.query_params.get('device_type')
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        
        return queryset.order_by('-start_time')
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 30))
    def device_breakdown(self, request):
        """Get session breakdown by device type."""
        try:
            days = int(request.query_params.get('days', 30))
            start_date = datetime.now() - timedelta(days=days)
            
            device_stats = UserSession.objects.filter(
                start_time__gte=start_date
            ).values('device_type').annotate(
                sessions=Count('id'),
                avg_duration=models.Avg('duration'),
                bounce_rate=models.Avg(
                    models.Case(
                        models.When(bounce=True, then=1),
                        default=0,
                        output_field=models.FloatField()
                    )
                )
            ).order_by('-sessions')
            
            return Response(list(device_stats), status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get device breakdown: {e}")
            return Response(
                {'error': 'Failed to retrieve device breakdown'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
