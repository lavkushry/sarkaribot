"""
Scraping app API views for SarkariBot.

Implements comprehensive scraping management functionality including
scraping control, monitoring, and analytics.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg, Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import ScrapeLog, ScrapedData, SourceStatistics, ScrapingError
from .serializers import (
    ScrapeLogSerializer,
    ScrapedDataSerializer,
    SourceStatisticsSerializer,
    ScrapingErrorSerializer
)
from .engine import scrape_source, scrape_all_active_sources
from .tasks import scrape_government_source, scheduled_scraping
from apps.sources.models import GovernmentSource

logger = logging.getLogger(__name__)


class ScrapeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing scrape logs.
    
    Provides read-only access to scraping logs with filtering
    and search capabilities.
    """
    
    queryset = ScrapeLog.objects.all()
    serializer_class = ScrapeLogSerializer
    permission_classes = [AllowAny]  # Adjust as needed
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source', 'scraper_engine']
    search_fields = ['source__name', 'error_message']
    ordering_fields = ['started_at', 'completed_at', 'duration_seconds']
    ordering = ['-started_at']
    
    def get_queryset(self):
        """Filter queryset based on request parameters."""
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(started_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(started_at__lte=end_date)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get detailed statistics for a specific scrape log.
        
        Returns metrics about the scraping operation including
        success rates, performance data, and error information.
        """
        scrape_log = self.get_object()
        
        # Get related scraped data
        scraped_data = ScrapedData.objects.filter(scrape_log=scrape_log)
        
        # Calculate statistics
        stats = {
            'scrape_log_id': str(scrape_log.id),
            'source': scrape_log.source.name,
            'status': scrape_log.status,
            'duration_seconds': float(scrape_log.duration_seconds) if scrape_log.duration_seconds else 0,
            'pages_scraped': scrape_log.pages_scraped,
            'requests_made': scrape_log.requests_made,
            'average_response_time': float(scrape_log.average_response_time) if scrape_log.average_response_time else 0,
            'jobs_found': scrape_log.jobs_found,
            'jobs_created': scrape_log.jobs_created,
            'jobs_updated': scrape_log.jobs_updated,
            'jobs_skipped': scrape_log.jobs_skipped,
            'error_count': scrape_log.error_count,
            'success_rate': scrape_log.success_rate,
            'scraped_data': {
                'total_items': scraped_data.count(),
                'high_quality_items': scraped_data.filter(data_quality_score__gte=70).count(),
                'processed_items': scraped_data.filter(processing_status='processed').count(),
                'failed_items': scraped_data.filter(processing_status='failed').count(),
                'pending_items': scraped_data.filter(processing_status='pending').count(),
            }
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def errors(self, request, pk=None):
        """Get all errors for a specific scrape log."""
        scrape_log = self.get_object()
        errors = ScrapingError.objects.filter(scrape_log=scrape_log)
        serializer = ScrapingErrorSerializer(errors, many=True)
        return Response(serializer.data)


class ScrapedDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing scraped data.
    
    Provides read-only access to scraped job data with filtering
    and quality analysis capabilities.
    """
    
    queryset = ScrapedData.objects.all()
    serializer_class = ScrapedDataSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source', 'processing_status', 'scrape_log']
    search_fields = ['raw_data__title', 'raw_data__description']
    ordering_fields = ['created_at', 'data_quality_score', 'processed_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset based on request parameters."""
        queryset = super().get_queryset()
        
        # Filter by quality score
        min_quality = self.request.query_params.get('min_quality')
        if min_quality:
            queryset = queryset.filter(data_quality_score__gte=min_quality)
        
        # Filter by high quality items
        high_quality = self.request.query_params.get('high_quality')
        if high_quality and high_quality.lower() == 'true':
            queryset = queryset.filter(data_quality_score__gte=70)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def quality_analysis(self, request):
        """
        Analyze data quality across all scraped items.
        
        Returns quality distribution and recommendations.
        """
        queryset = self.get_queryset()
        
        total_items = queryset.count()
        if total_items == 0:
            return Response({'message': 'No scraped data found'})
        
        # Quality distribution
        quality_ranges = [
            ('excellent', Q(data_quality_score__gte=90)),
            ('good', Q(data_quality_score__gte=70, data_quality_score__lt=90)),
            ('fair', Q(data_quality_score__gte=50, data_quality_score__lt=70)),
            ('poor', Q(data_quality_score__lt=50)),
        ]
        
        quality_distribution = {}
        for label, q_filter in quality_ranges:
            count = queryset.filter(q_filter).count()
            quality_distribution[label] = {
                'count': count,
                'percentage': round((count / total_items) * 100, 2)
            }
        
        # Source-wise quality
        source_quality = []
        for source in GovernmentSource.objects.filter(active=True):
            source_items = queryset.filter(source=source)
            if source_items.exists():
                avg_quality = source_items.aggregate(
                    avg_quality=Avg('data_quality_score')
                )['avg_quality'] or 0
                
                source_quality.append({
                    'source_name': source.name,
                    'total_items': source_items.count(),
                    'average_quality': round(avg_quality, 2),
                    'high_quality_items': source_items.filter(data_quality_score__gte=70).count()
                })
        
        # Processing status distribution
        processing_stats = queryset.values('processing_status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        analysis = {
            'total_items': total_items,
            'quality_distribution': quality_distribution,
            'source_quality': sorted(source_quality, key=lambda x: x['average_quality'], reverse=True),
            'processing_status': list(processing_stats),
            'recommendations': generate_quality_recommendations(quality_distribution, source_quality)
        }
        
        return Response(analysis)


class SourceStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for source scraping statistics.
    
    Provides insights into source performance and reliability.
    """
    
    queryset = SourceStatistics.objects.all()
    serializer_class = SourceStatisticsSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['source', 'date']
    ordering_fields = ['date', 'success_rate', 'jobs_found']
    ordering = ['-date']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get summary statistics across all sources.
        
        Returns aggregated performance metrics.
        """
        # Date range for analysis
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        queryset = self.get_queryset().filter(date__gte=start_date, date__lte=end_date)
        
        if not queryset.exists():
            return Response({'message': 'No statistics data found for the specified period'})
        
        # Overall statistics
        total_stats = queryset.aggregate(
            total_scrapes=Count('id'),
            avg_success_rate=Avg('success_rate'),
            total_jobs_found=models.Sum('jobs_found'),
            total_jobs_created=models.Sum('jobs_created'),
            avg_response_time=Avg('average_response_time')
        )
        
        # Source performance ranking
        source_performance = []
        for source in GovernmentSource.objects.filter(active=True):
            source_stats = queryset.filter(source=source)
            if source_stats.exists():
                source_metrics = source_stats.aggregate(
                    avg_success_rate=Avg('success_rate'),
                    total_jobs=models.Sum('jobs_found'),
                    avg_jobs_per_scrape=Avg('jobs_found'),
                    scrape_count=Count('id')
                )
                
                source_performance.append({
                    'source_name': source.name,
                    'success_rate': round(source_metrics['avg_success_rate'] or 0, 2),
                    'total_jobs': source_metrics['total_jobs'] or 0,
                    'average_jobs_per_scrape': round(source_metrics['avg_jobs_per_scrape'] or 0, 2),
                    'scrape_frequency': source.scrape_frequency,
                    'total_scrapes': source_metrics['scrape_count']
                })
        
        # Daily trends (last 7 days)
        daily_trends = []
        for i in range(7):
            date = end_date - timedelta(days=i)
            day_stats = queryset.filter(date=date).aggregate(
                scrapes=Count('id'),
                jobs_found=models.Sum('jobs_found'),
                avg_success_rate=Avg('success_rate')
            )
            
            daily_trends.append({
                'date': date.isoformat(),
                'scrapes': day_stats['scrapes'] or 0,
                'jobs_found': day_stats['jobs_found'] or 0,
                'success_rate': round(day_stats['avg_success_rate'] or 0, 2)
            })
        
        summary = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': 30
            },
            'overall_statistics': {
                'total_scrapes': total_stats['total_scrapes'],
                'average_success_rate': round(total_stats['avg_success_rate'] or 0, 2),
                'total_jobs_found': total_stats['total_jobs_found'] or 0,
                'total_jobs_created': total_stats['total_jobs_created'] or 0,
                'average_response_time': round(total_stats['avg_response_time'] or 0, 3)
            },
            'source_performance': sorted(source_performance, key=lambda x: x['success_rate'], reverse=True),
            'daily_trends': daily_trends
        }
        
        return Response(summary)


class ScrapingControlAPIView(APIView):
    """
    API view for controlling scraping operations.
    
    Provides endpoints for starting, stopping, and monitoring
    scraping tasks.
    """
    
    permission_classes = [AllowAny]  # Adjust as needed
    
    def post(self, request):
        """
        Start scraping operation for specific sources or all sources.
        
        Request body:
        {
            "action": "start_scraping",
            "source_ids": [1, 2, 3],  # Optional: specific sources
            "scrape_all": true,       # Optional: scrape all active sources
            "async": true             # Optional: run asynchronously
        }
        """
        action = request.data.get('action')
        
        if action == 'start_scraping':
            source_ids = request.data.get('source_ids', [])
            scrape_all = request.data.get('scrape_all', False)
            async_execution = request.data.get('async', True)
            
            if scrape_all:
                # Scrape all active sources
                if async_execution:
                    task = scheduled_scraping.delay()
                    return Response({
                        'success': True,
                        'message': 'Scheduled scraping for all active sources',
                        'task_id': task.id,
                        'async': True
                    })
                else:
                    result = scrape_all_active_sources()
                    return Response({
                        'success': True,
                        'message': 'Completed scraping all active sources',
                        'result': result,
                        'async': False
                    })
            
            elif source_ids:
                # Scrape specific sources
                results = []
                for source_id in source_ids:
                    try:
                        if async_execution:
                            task = scrape_government_source.delay(source_id)
                            results.append({
                                'source_id': source_id,
                                'task_id': task.id,
                                'status': 'scheduled'
                            })
                        else:
                            result = scrape_source(source_id)
                            results.append({
                                'source_id': source_id,
                                'result': result,
                                'status': 'completed'
                            })
                    except Exception as e:
                        results.append({
                            'source_id': source_id,
                            'error': str(e),
                            'status': 'failed'
                        })
                
                return Response({
                    'success': True,
                    'message': f'Scraping initiated for {len(source_ids)} sources',
                    'results': results,
                    'async': async_execution
                })
            
            else:
                return Response({
                    'success': False,
                    'error': 'Either source_ids or scrape_all must be specified'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({
                'success': False,
                'error': 'Invalid action. Supported actions: start_scraping'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """
        Get current scraping status and recent activity.
        
        Returns information about running tasks, recent scrapes,
        and system health.
        """
        # Recent scrape logs (last 24 hours)
        recent_logs = ScrapeLog.objects.filter(
            started_at__gte=timezone.now() - timedelta(hours=24)
        ).order_by('-started_at')[:10]
        
        # Running scrapes
        running_logs = ScrapeLog.objects.filter(status='running')
        
        # Active sources
        active_sources = GovernmentSource.objects.filter(active=True)
        
        # Sources that need scraping
        sources_needing_scrape = []
        for source in active_sources:
            if source.last_scraped is None:
                sources_needing_scrape.append({
                    'source_id': source.id,
                    'source_name': source.name,
                    'reason': 'Never scraped'
                })
            else:
                time_since_scrape = timezone.now() - source.last_scraped
                scrape_interval = timedelta(hours=source.scrape_frequency)
                
                if time_since_scrape >= scrape_interval:
                    sources_needing_scrape.append({
                        'source_id': source.id,
                        'source_name': source.name,
                        'reason': f'Last scraped {time_since_scrape} ago'
                    })
        
        status_info = {
            'system_status': 'operational',
            'active_sources_count': active_sources.count(),
            'running_scrapes_count': running_logs.count(),
            'sources_needing_scrape': len(sources_needing_scrape),
            'recent_activity': {
                'total_scrapes_24h': recent_logs.count(),
                'successful_scrapes_24h': recent_logs.filter(status='completed').count(),
                'failed_scrapes_24h': recent_logs.filter(status='failed').count(),
            },
            'running_scrapes': [
                {
                    'scrape_log_id': str(log.id),
                    'source_name': log.source.name,
                    'started_at': log.started_at.isoformat(),
                    'duration_so_far': (timezone.now() - log.started_at).total_seconds()
                }
                for log in running_logs
            ],
            'sources_needing_scrape': sources_needing_scrape[:5],  # Top 5
            'recent_scrapes': [
                {
                    'scrape_log_id': str(log.id),
                    'source_name': log.source.name,
                    'status': log.status,
                    'started_at': log.started_at.isoformat(),
                    'jobs_found': log.jobs_found,
                    'duration_seconds': float(log.duration_seconds) if log.duration_seconds else 0
                }
                for log in recent_logs
            ]
        }
        
        return Response(status_info)


def generate_quality_recommendations(quality_dist: Dict, source_quality: list) -> list:
    """
    Generate recommendations based on data quality analysis.
    
    Args:
        quality_dist: Quality distribution statistics
        source_quality: Source-wise quality metrics
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # Overall quality recommendations
    poor_percentage = quality_dist.get('poor', {}).get('percentage', 0)
    if poor_percentage > 20:
        recommendations.append(
            f"High percentage ({poor_percentage}%) of poor quality data detected. "
            "Consider reviewing scraping selectors and data extraction logic."
        )
    
    excellent_percentage = quality_dist.get('excellent', {}).get('percentage', 0)
    if excellent_percentage < 30:
        recommendations.append(
            f"Only {excellent_percentage}% of data is excellent quality. "
            "Enhance data extraction to capture more complete information."
        )
    
    # Source-specific recommendations
    for source in source_quality[:3]:  # Top 3 sources
        if source['average_quality'] < 60:
            recommendations.append(
                f"Source '{source['source_name']}' has low average quality ({source['average_quality']}%). "
                "Review and optimize selectors for this source."
            )
    
    if not recommendations:
        recommendations.append("Data quality looks good overall. Continue monitoring for improvements.")
    
    return recommendations


# Add necessary imports for models
from django.db import models
