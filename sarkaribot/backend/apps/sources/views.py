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
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import GovernmentSource, SourceStatistics
from .serializers import (
    GovernmentSourceSerializer, GovernmentSourceDetailSerializer,
    SourceStatisticsSerializer
)

logger = logging.getLogger(__name__)


class GovernmentSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for government sources.

    Provides read-only access to government source information
    including statistics and scraping configuration.
    """

    queryset = GovernmentSource.objects.filter(is_active=True)
    serializer_class = GovernmentSourceSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'scrape_frequency']
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
            total_attempted=Count('scrapes_attempted'),
            total_successful=Count('scrapes_successful'),
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


class SourceStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for source statistics.

    Provides read-only access to daily source statistics
    with filtering and search capabilities.
    """

    queryset = SourceStatistics.objects.all()
    serializer_class = SourceStatisticsSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source', 'date']
    search_fields = ['source__name']
    ordering_fields = ['date', 'scrapes_successful', 'jobs_found']
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics for all sources."""

        # Get last 30 days of statistics
        thirty_days_ago = timezone.now() - timedelta(days=30)

        summary = SourceStatistics.objects.filter(
            date__gte=thirty_days_ago
        ).aggregate(
            total_scrapes_attempted=Count('scrapes_attempted'),
            total_scrapes_successful=Count('scrapes_successful'),
            total_jobs_found=Count('jobs_found'),
            avg_response_time=Avg('average_response_time')
        )

        return Response({
            'period': '30_days',
            'summary': summary
        })

    @action(detail=False, methods=['get'])
    def performance(self, request):
        """Get performance metrics for all sources."""
        from django.db.models import Count, Avg, Q
        from datetime import timedelta
        from django.utils import timezone
        
        # Get statistics for last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        sources_stats = []
        for source in self.get_queryset():
            stats = {
                'source_id': source.id,
                'source_name': source.name,
                'display_name': source.display_name,
                'is_active': source.is_active,
                'last_scraped': source.last_scraped,
                'total_jobs_found': source.total_jobs_found,
                'scrape_frequency': source.scrape_frequency,
                'status': source.status,
            }
            
            # Add recent job counts if jobs app is available
            try:
                from apps.jobs.models import JobPosting
                recent_jobs = JobPosting.objects.filter(
                    source=source,
                    created_at__gte=thirty_days_ago
                ).count()
                stats['recent_jobs_count'] = recent_jobs
            except ImportError:
                stats['recent_jobs_count'] = 0
            
            sources_stats.append(stats)
        
        return Response({
            'success': True,
            'data': sources_stats,
            'period': '30_days',
            'generated_at': timezone.now().isoformat()
        })
