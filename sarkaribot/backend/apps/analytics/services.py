"""
Analytics Service Layer for SarkariBot
Handles analytics data collection, processing, and reporting.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta, date
from django.db.models import Count, Avg, Q, F, Sum
from django.db.models.functions import TruncDate, TruncHour
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
import logging
import json
from collections import defaultdict
from user_agents import parse

from .models import (
    PageView, JobView, SearchQuery, UserSession, 
    AlertEngagement, PerformanceMetric, DailyStats, ConversionFunnel
)

logger = logging.getLogger(__name__)
User = get_user_model()


class AnalyticsService:
    """
    Core analytics service for tracking and processing user interactions.
    """
    
    @staticmethod
    def track_page_view(
        request, 
        path: str, 
        page_title: str = "", 
        metadata: Dict[str, Any] = None
    ) -> PageView:
        """
        Track a page view with comprehensive user and device information.
        
        Args:
            request: Django request object
            path: Page path
            page_title: Title of the page
            metadata: Additional metadata
            
        Returns:
            PageView instance
        """
        try:
            # Parse user agent
            user_agent_string = request.META.get('HTTP_USER_AGENT', '')
            user_agent = parse(user_agent_string)
            
            # Get IP address
            ip_address = AnalyticsService._get_client_ip(request)
            
            # Get session ID
            session_id = request.session.session_key or request.session.create()
            
            # Get geographic information (would integrate with IP geolocation service)
            geo_info = AnalyticsService._get_geo_info(ip_address)
            
            page_view = PageView.objects.create(
                path=path,
                page_title=page_title,
                referrer=request.META.get('HTTP_REFERER', ''),
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent_string,
                device_type=AnalyticsService._get_device_type(user_agent),
                browser=f"{user_agent.browser.family} {user_agent.browser.version_string}",
                os=f"{user_agent.os.family} {user_agent.os.version_string}",
                country=geo_info.get('country', ''),
                region=geo_info.get('region', ''),
                city=geo_info.get('city', ''),
                metadata=metadata or {}
            )
            
            # Update session
            AnalyticsService._update_session(request, page_view)
            
            logger.info(f"Page view tracked: {path} for session {session_id}")
            return page_view
            
        except Exception as e:
            logger.error(f"Failed to track page view for {path}: {e}")
            return None
    
    @staticmethod
    def track_job_view(
        request,
        job,
        came_from_alert: bool = False,
        search_query: str = "",
        view_duration: int = None
    ) -> JobView:
        """
        Track a job posting view with context information.
        
        Args:
            request: Django request object
            job: JobPosting instance
            came_from_alert: Whether user came from an alert
            search_query: Search query that led to this job
            view_duration: Time spent viewing the job
            
        Returns:
            JobView instance
        """
        try:
            session_id = request.session.session_key or request.session.create()
            ip_address = AnalyticsService._get_client_ip(request)
            
            job_view = JobView.objects.create(
                job=job,
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id,
                ip_address=ip_address,
                referrer=request.META.get('HTTP_REFERER', ''),
                search_query=search_query,
                came_from_alert=came_from_alert,
                view_duration=view_duration
            )
            
            # Update session metrics
            AnalyticsService._update_session_job_view(request)
            
            logger.info(f"Job view tracked: {job.title} for session {session_id}")
            return job_view
            
        except Exception as e:
            logger.error(f"Failed to track job view for {job.id}: {e}")
            return None
    
    @staticmethod
    def track_search_query(
        request,
        query: str,
        filters_applied: Dict[str, Any],
        results_count: int,
        response_time: float
    ) -> SearchQuery:
        """
        Track a search query with performance metrics.
        
        Args:
            request: Django request object
            query: Search query string
            filters_applied: Applied filters
            results_count: Number of results returned
            response_time: Search response time in seconds
            
        Returns:
            SearchQuery instance
        """
        try:
            session_id = request.session.session_key or request.session.create()
            ip_address = AnalyticsService._get_client_ip(request)
            
            search_query = SearchQuery.objects.create(
                query=query,
                filters_applied=filters_applied,
                results_count=results_count,
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id,
                ip_address=ip_address,
                response_time=response_time
            )
            
            # Update session metrics
            AnalyticsService._update_session_search(request)
            
            logger.info(f"Search query tracked: '{query}' with {results_count} results")
            return search_query
            
        except Exception as e:
            logger.error(f"Failed to track search query '{query}': {e}")
            return None
    
    @staticmethod
    def track_conversion(
        request,
        stage: str,
        job_id: Optional[str] = None,
        source_stage: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> ConversionFunnel:
        """
        Track conversion funnel stage.
        
        Args:
            request: Django request object
            stage: Funnel stage
            job_id: Related job ID
            source_stage: Previous stage
            metadata: Additional metadata
            
        Returns:
            ConversionFunnel instance
        """
        try:
            session_id = request.session.session_key or request.session.create()
            
            conversion = ConversionFunnel.objects.create(
                stage=stage,
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id,
                job_id=job_id,
                source_stage=source_stage,
                metadata=metadata or {}
            )
            
            logger.info(f"Conversion tracked: {stage} for session {session_id}")
            return conversion
            
        except Exception as e:
            logger.error(f"Failed to track conversion for stage {stage}: {e}")
            return None
    
    @staticmethod
    def track_performance_metric(
        metric_type: str,
        value: float,
        unit: str = "seconds",
        endpoint: str = "",
        source: str = "",
        metadata: Dict[str, Any] = None
    ) -> PerformanceMetric:
        """
        Track system performance metrics.
        
        Args:
            metric_type: Type of metric
            value: Metric value
            unit: Unit of measurement
            endpoint: Related API endpoint
            source: Source of the metric
            metadata: Additional metadata
            
        Returns:
            PerformanceMetric instance
        """
        try:
            metric = PerformanceMetric.objects.create(
                metric_type=metric_type,
                value=value,
                unit=unit,
                endpoint=endpoint,
                source=source,
                metadata=metadata or {}
            )
            
            logger.debug(f"Performance metric tracked: {metric_type} = {value} {unit}")
            return metric
            
        except Exception as e:
            logger.error(f"Failed to track performance metric {metric_type}: {e}")
            return None
    
    @staticmethod
    def _get_client_ip(request) -> str:
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '0.0.0.0'
    
    @staticmethod
    def _get_device_type(user_agent) -> str:
        """Determine device type from user agent."""
        if user_agent.is_mobile:
            return 'mobile'
        elif user_agent.is_tablet:
            return 'tablet'
        else:
            return 'desktop'
    
    @staticmethod
    def _get_geo_info(ip_address: str) -> Dict[str, str]:
        """
        Get geographic information from IP address.
        This would integrate with a service like MaxMind GeoIP2.
        """
        # Placeholder implementation
        return {
            'country': 'India',
            'region': 'Unknown',
            'city': 'Unknown'
        }
    
    @staticmethod
    def _update_session(request, page_view: PageView):
        """Update or create user session."""
        try:
            session_id = page_view.session_id
            user_agent = parse(page_view.user_agent)
            
            session, created = UserSession.objects.get_or_create(
                session_id=session_id,
                defaults={
                    'user': page_view.user,
                    'ip_address': page_view.ip_address,
                    'user_agent': page_view.user_agent,
                    'device_type': page_view.device_type,
                    'browser': page_view.browser,
                    'os': page_view.os,
                    'country': page_view.country,
                    'region': page_view.region,
                    'city': page_view.city,
                }
            )
            
            # Update activity metrics
            session.page_views = F('page_views') + 1
            session.last_activity = timezone.now()
            if session.page_views > 1:
                session.bounce = False
            session.save(update_fields=['page_views', 'last_activity', 'bounce'])
            
        except Exception as e:
            logger.error(f"Failed to update session: {e}")
    
    @staticmethod
    def _update_session_job_view(request):
        """Update session job view count."""
        try:
            session_id = request.session.session_key
            if session_id:
                UserSession.objects.filter(session_id=session_id).update(
                    job_views=F('job_views') + 1,
                    last_activity=timezone.now()
                )
        except Exception as e:
            logger.error(f"Failed to update session job views: {e}")
    
    @staticmethod
    def _update_session_search(request):
        """Update session search count."""
        try:
            session_id = request.session.session_key
            if session_id:
                UserSession.objects.filter(session_id=session_id).update(
                    searches=F('searches') + 1,
                    last_activity=timezone.now()
                )
        except Exception as e:
            logger.error(f"Failed to update session searches: {e}")


class ReportingService:
    """
    Service for generating analytics reports and insights.
    """
    
    @staticmethod
    def get_traffic_overview(days: int = 30) -> Dict[str, Any]:
        """
        Get traffic overview for the specified number of days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Traffic overview data
        """
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            # Cache key for this report
            cache_key = f"traffic_overview_{days}_days"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # Calculate metrics
            total_page_views = PageView.objects.filter(
                created_at__gte=start_date
            ).count()
            
            unique_visitors = PageView.objects.filter(
                created_at__gte=start_date
            ).values('session_id').distinct().count()
            
            total_sessions = UserSession.objects.filter(
                start_time__gte=start_date
            ).count()
            
            avg_session_duration = UserSession.objects.filter(
                start_time__gte=start_date,
                duration__isnull=False
            ).aggregate(avg_duration=Avg('duration'))['avg_duration'] or 0
            
            bounce_rate = UserSession.objects.filter(
                start_time__gte=start_date
            ).aggregate(
                bounce_rate=Avg(
                    models.Case(
                        models.When(bounce=True, then=1),
                        default=0,
                        output_field=models.FloatField()
                    )
                )
            )['bounce_rate'] or 0
            
            # Daily breakdown
            daily_data = PageView.objects.filter(
                created_at__gte=start_date
            ).extra(
                select={'day': 'date(created_at)'}
            ).values('day').annotate(
                page_views=Count('id'),
                unique_sessions=Count('session_id', distinct=True)
            ).order_by('day')
            
            # Top pages
            top_pages = PageView.objects.filter(
                created_at__gte=start_date
            ).values('path').annotate(
                views=Count('id'),
                unique_views=Count('session_id', distinct=True)
            ).order_by('-views')[:10]
            
            # Device breakdown
            device_stats = PageView.objects.filter(
                created_at__gte=start_date
            ).values('device_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            data = {
                'period': {
                    'start_date': start_date.date(),
                    'end_date': timezone.now().date(),
                    'days': days
                },
                'overview': {
                    'total_page_views': total_page_views,
                    'unique_visitors': unique_visitors,
                    'total_sessions': total_sessions,
                    'avg_session_duration': round(avg_session_duration, 2),
                    'bounce_rate': round(bounce_rate * 100, 2)
                },
                'daily_breakdown': list(daily_data),
                'top_pages': list(top_pages),
                'device_breakdown': list(device_stats)
            }
            
            # Cache for 1 hour
            cache.set(cache_key, data, 3600)
            
            logger.info(f"Generated traffic overview for {days} days")
            return data
            
        except Exception as e:
            logger.error(f"Failed to generate traffic overview: {e}")
            return {}
    
    @staticmethod
    def get_job_analytics(days: int = 30) -> Dict[str, Any]:
        """
        Get job-related analytics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Job analytics data
        """
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            cache_key = f"job_analytics_{days}_days"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # Job view metrics
            total_job_views = JobView.objects.filter(
                created_at__gte=start_date
            ).count()
            
            unique_job_viewers = JobView.objects.filter(
                created_at__gte=start_date
            ).values('session_id').distinct().count()
            
            avg_view_duration = JobView.objects.filter(
                created_at__gte=start_date,
                view_duration__isnull=False
            ).aggregate(avg_duration=Avg('view_duration'))['avg_duration'] or 0
            
            # Most viewed jobs
            popular_jobs = JobView.objects.filter(
                created_at__gte=start_date
            ).values(
                'job__title', 'job__id'
            ).annotate(
                views=Count('id'),
                unique_views=Count('session_id', distinct=True)
            ).order_by('-views')[:20]
            
            # Job view trends
            daily_job_views = JobView.objects.filter(
                created_at__gte=start_date
            ).extra(
                select={'day': 'date(created_at)'}
            ).values('day').annotate(
                views=Count('id')
            ).order_by('day')
            
            # Application tracking (if available)
            applications = JobView.objects.filter(
                created_at__gte=start_date,
                clicked_apply=True
            ).count()
            
            bookmarks = JobView.objects.filter(
                created_at__gte=start_date,
                bookmarked=True
            ).count()
            
            data = {
                'period': {
                    'start_date': start_date.date(),
                    'end_date': timezone.now().date(),
                    'days': days
                },
                'overview': {
                    'total_job_views': total_job_views,
                    'unique_job_viewers': unique_job_viewers,
                    'avg_view_duration': round(avg_view_duration, 2),
                    'total_applications': applications,
                    'total_bookmarks': bookmarks
                },
                'popular_jobs': list(popular_jobs),
                'daily_trends': list(daily_job_views)
            }
            
            # Cache for 1 hour
            cache.set(cache_key, data, 3600)
            
            logger.info(f"Generated job analytics for {days} days")
            return data
            
        except Exception as e:
            logger.error(f"Failed to generate job analytics: {e}")
            return {}
    
    @staticmethod
    def get_search_analytics(days: int = 30) -> Dict[str, Any]:
        """
        Get search analytics and insights.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Search analytics data
        """
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            cache_key = f"search_analytics_{days}_days"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # Search metrics
            total_searches = SearchQuery.objects.filter(
                created_at__gte=start_date
            ).count()
            
            avg_results = SearchQuery.objects.filter(
                created_at__gte=start_date
            ).aggregate(avg_results=Avg('results_count'))['avg_results'] or 0
            
            avg_response_time = SearchQuery.objects.filter(
                created_at__gte=start_date
            ).aggregate(avg_time=Avg('response_time'))['avg_time'] or 0
            
            # Popular search terms
            popular_terms = SearchQuery.objects.filter(
                created_at__gte=start_date
            ).values('query').annotate(
                count=Count('id')
            ).order_by('-count')[:20]
            
            # Zero result searches
            zero_result_searches = SearchQuery.objects.filter(
                created_at__gte=start_date,
                results_count=0
            ).values('query').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            data = {
                'period': {
                    'start_date': start_date.date(),
                    'end_date': timezone.now().date(),
                    'days': days
                },
                'overview': {
                    'total_searches': total_searches,
                    'avg_results_per_search': round(avg_results, 2),
                    'avg_response_time': round(avg_response_time, 4),
                    'zero_result_searches': zero_result_searches.count()
                },
                'popular_terms': list(popular_terms),
                'zero_result_queries': list(zero_result_searches)
            }
            
            # Cache for 1 hour
            cache.set(cache_key, data, 3600)
            
            logger.info(f"Generated search analytics for {days} days")
            return data
            
        except Exception as e:
            logger.error(f"Failed to generate search analytics: {e}")
            return {}
    
    @staticmethod
    def get_conversion_funnel(days: int = 30) -> Dict[str, Any]:
        """
        Get conversion funnel analysis.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Conversion funnel data
        """
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            cache_key = f"conversion_funnel_{days}_days"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # Get conversion data for each stage
            funnel_data = ConversionFunnel.objects.filter(
                created_at__gte=start_date
            ).values('stage').annotate(
                count=Count('session_id', distinct=True)
            ).order_by('count')
            
            # Convert to dictionary for easy lookup
            stage_counts = {item['stage']: item['count'] for item in funnel_data}
            
            # Define funnel stages in order
            stages = [
                'landing', 'browse', 'search', 'view_job', 
                'click_apply', 'register', 'bookmark', 'create_alert'
            ]
            
            funnel_stats = []
            previous_count = None
            
            for stage in stages:
                count = stage_counts.get(stage, 0)
                conversion_rate = 0
                
                if previous_count is not None and previous_count > 0:
                    conversion_rate = (count / previous_count) * 100
                
                funnel_stats.append({
                    'stage': stage,
                    'users': count,
                    'conversion_rate': round(conversion_rate, 2)
                })
                
                previous_count = count
            
            data = {
                'period': {
                    'start_date': start_date.date(),
                    'end_date': timezone.now().date(),
                    'days': days
                },
                'funnel': funnel_stats
            }
            
            # Cache for 1 hour
            cache.set(cache_key, data, 3600)
            
            logger.info(f"Generated conversion funnel for {days} days")
            return data
            
        except Exception as e:
            logger.error(f"Failed to generate conversion funnel: {e}")
            return {}


class DailyStatsService:
    """
    Service for generating and maintaining daily statistics.
    """
    
    @staticmethod
    def generate_daily_stats(target_date: date = None) -> DailyStats:
        """
        Generate daily statistics for a specific date.
        
        Args:
            target_date: Date to generate stats for (defaults to yesterday)
            
        Returns:
            DailyStats instance
        """
        if target_date is None:
            target_date = timezone.now().date() - timedelta(days=1)
        
        try:
            start_datetime = timezone.make_aware(
                datetime.combine(target_date, datetime.min.time())
            )
            end_datetime = start_datetime + timedelta(days=1)
            
            # Calculate traffic metrics
            page_views = PageView.objects.filter(
                created_at__gte=start_datetime,
                created_at__lt=end_datetime
            )
            
            unique_visitors = page_views.values('session_id').distinct().count()
            total_page_views = page_views.count()
            
            sessions = UserSession.objects.filter(
                start_time__gte=start_datetime,
                start_time__lt=end_datetime
            )
            
            total_sessions = sessions.count()
            bounce_sessions = sessions.filter(bounce=True).count()
            bounce_rate = (bounce_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            avg_session_duration = sessions.filter(
                duration__isnull=False
            ).aggregate(avg=Avg('duration'))['avg'] or 0
            
            # Job metrics
            job_views = JobView.objects.filter(
                created_at__gte=start_datetime,
                created_at__lt=end_datetime
            )
            
            jobs_viewed = job_views.count()
            jobs_applied = job_views.filter(clicked_apply=True).count()
            jobs_bookmarked = job_views.filter(bookmarked=True).count()
            jobs_shared = job_views.filter(shared=True).count()
            
            # Search metrics
            searches = SearchQuery.objects.filter(
                created_at__gte=start_datetime,
                created_at__lt=end_datetime
            )
            
            searches_performed = searches.count()
            avg_search_results = searches.aggregate(avg=Avg('results_count'))['avg'] or 0
            
            # Top search terms
            top_search_terms = list(
                searches.values('query').annotate(
                    count=Count('id')
                ).order_by('-count')[:10].values_list('query', flat=True)
            )
            
            # Performance metrics
            perf_metrics = PerformanceMetric.objects.filter(
                recorded_at__gte=start_datetime,
                recorded_at__lt=end_datetime,
                metric_type='api_response_time'
            )
            
            avg_response_time = perf_metrics.aggregate(avg=Avg('value'))['avg'] or 0
            
            # Create or update daily stats
            daily_stats, created = DailyStats.objects.update_or_create(
                date=target_date,
                defaults={
                    'unique_visitors': unique_visitors,
                    'page_views': total_page_views,
                    'sessions': total_sessions,
                    'bounce_rate': round(bounce_rate, 2),
                    'avg_session_duration': round(avg_session_duration, 2),
                    'jobs_viewed': jobs_viewed,
                    'jobs_applied': jobs_applied,
                    'jobs_bookmarked': jobs_bookmarked,
                    'jobs_shared': jobs_shared,
                    'searches_performed': searches_performed,
                    'avg_search_results': round(avg_search_results, 2),
                    'top_search_terms': top_search_terms,
                    'avg_response_time': round(avg_response_time, 4),
                    'uptime_percentage': 100.0  # Would be calculated from monitoring
                }
            )
            
            action = "Created" if created else "Updated"
            logger.info(f"{action} daily stats for {target_date}")
            return daily_stats
            
        except Exception as e:
            logger.error(f"Failed to generate daily stats for {target_date}: {e}")
            return None
