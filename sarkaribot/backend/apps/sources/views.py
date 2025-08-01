"""
API views for government sources management.

Provides endpoints for managing government source configurations,
statistics, and monitoring according to Knowledge.md specifications.
"""

import logging
from typing import Dict, Any
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta

from .models import GovernmentSource, SourceStatistics
from .serializers import (
    GovernmentSourceSerializer, GovernmentSourceDetailSerializer,
    SourceStatisticsSerializer, SourceConfigurationSerializer
)

logger = logging.getLogger(__name__)


class GovernmentSourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for government sources.
    
    Provides full CRUD operations for government source management
    including statistics and scraping configuration.
    """
    
    queryset = GovernmentSource.objects.all()
    serializer_class = GovernmentSourceSerializer
    permission_classes = [AllowAny]  # TODO: Change to IsAuthenticated for production
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active', 'scrape_frequency', 'status']
    search_fields = ['name', 'display_name', 'description']
    ordering_fields = ['name', 'display_name', 'created_at', 'last_scraped']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Return detailed serializer for detail view."""
        if self.action == 'retrieve':
            return GovernmentSourceDetailSerializer
        return GovernmentSourceSerializer
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get detailed statistics for a specific source."""
        source = self.get_object()
        
        # Get recent statistics (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        stats = SourceStatistics.objects.filter(
            source=source,
            date__gte=thirty_days_ago
        ).order_by('-date')
        
        serializer = SourceStatisticsSerializer(stats, many=True)
        
        return Response({
            'source': source.name,
            'period': '30_days',
            'statistics': serializer.data,
            'summary': self._calculate_summary_stats(stats)
        })
    
    @action(detail=False, methods=['get'])
    def performance_summary(self, request):
        """Get performance summary for all sources."""
        try:
            sources = self.get_queryset()
            summary_data = []
            
            for source in sources:
                # Get recent stats
                recent_stats = SourceStatistics.objects.filter(
                    source=source,
                    date__gte=timezone.now() - timedelta(days=7)
                )
                
                summary = {
                    'source_id': source.id,
                    'name': source.name,
                    'display_name': source.display_name,
                    'active': source.active,
                    'last_scraped': source.last_scraped,
                    'scrape_frequency': source.scrape_frequency,
                    'recent_performance': self._calculate_summary_stats(recent_stats)
                }
                summary_data.append(summary)
            
            return Response({
                'total_sources': len(summary_data),
                'active_sources': len([s for s in summary_data if s['active']]),
                'sources': summary_data
            })
            
        except Exception as e:
            logger.error(f"Error generating performance summary: {e}")
            return Response(
                {'error': 'Failed to generate performance summary'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def validate_config(self, request):
        """Validate scraping configuration without saving."""
        try:
            serializer = SourceConfigurationSerializer(data=request.data)
            if serializer.is_valid():
                return Response({
                    'valid': True,
                    'message': 'Configuration is valid',
                    'validated_data': serializer.validated_data
                })
            else:
                return Response({
                    'valid': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return Response(
                {'error': 'Failed to validate configuration'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _calculate_summary_stats(self, stats_queryset) -> Dict[str, Any]:
        """Calculate summary statistics from queryset."""
        if not stats_queryset.exists():
            return {
                'total_scrapes': 0,
                'success_rate': 0.0,
                'avg_jobs_found': 0.0,
                'avg_response_time': 0.0
            }
        
        aggregates = stats_queryset.aggregate(
            total_attempted=Sum('scrapes_attempted'),
            total_successful=Sum('scrapes_successful'),
            avg_jobs=Avg('jobs_found'),
            avg_response_time=Avg('average_response_time')
        )
        
        total_attempted = aggregates['total_attempted'] or 0
        total_successful = aggregates['total_successful'] or 0
        success_rate = (total_successful / total_attempted * 100) if total_attempted > 0 else 0.0
        
        return {
            'total_scrapes': total_attempted,
            'success_rate': round(success_rate, 2),
            'avg_jobs_found': round(aggregates['avg_jobs'] or 0.0, 2),
            'avg_response_time': round(aggregates['avg_response_time'] or 0.0, 3)
        }


class SourceStatisticsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for source statistics.
    
    Provides full CRUD access to historical scraping statistics and performance metrics.
    """
    
    queryset = SourceStatistics.objects.all()
    serializer_class = SourceStatisticsSerializer
    permission_classes = [AllowAny]  # TODO: Change to IsAuthenticated for production
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['source', 'date']
    ordering_fields = ['date', 'scrapes_attempted', 'jobs_found']
    ordering = ['-date']
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by date range if provided
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        return queryset.select_related('source')
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get trending statistics over time."""
        try:
            # Get last 30 days by default
            days = int(request.query_params.get('days', 30))
            start_date = timezone.now() - timedelta(days=days)
            
            stats = self.get_queryset().filter(date__gte=start_date)
            
            # Group by date
            trends_data = {}
            for stat in stats:
                date_str = stat.date.isoformat()
                if date_str not in trends_data:
                    trends_data[date_str] = {
                        'date': date_str,
                        'total_scrapes': 0,
                        'total_jobs_found': 0,
                        'sources_active': 0
                    }
                
                trends_data[date_str]['total_scrapes'] += stat.scrapes_attempted
                trends_data[date_str]['total_jobs_found'] += stat.jobs_found
                trends_data[date_str]['sources_active'] += 1
            
            # Convert to list and sort by date
            trends_list = list(trends_data.values())
            trends_list.sort(key=lambda x: x['date'])
            
            return Response({
                'period_days': days,
                'trends': trends_list
            })
            
        except Exception as e:
            logger.error(f"Error generating trends data: {e}")
            return Response(
                {'error': 'Failed to generate trends data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
