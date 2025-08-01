"""
Analytics Serializers for SarkariBot
DRF serializers for analytics models and data structures.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    PageView, JobView, SearchQuery, UserSession,
    AlertEngagement, PerformanceMetric, DailyStats, ConversionFunnel
)

User = get_user_model()


class PageViewSerializer(serializers.ModelSerializer):
    """
    Serializer for PageView model.
    """
    user_display = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PageView
        fields = [
            'id', 'path', 'page_title', 'referrer', 'user', 'user_display',
            'session_id', 'ip_address', 'device_type', 'browser', 'os',
            'country', 'region', 'city', 'created_at', 'duration', 'metadata'
        ]
        read_only_fields = ['id', 'created_at']


class JobViewSerializer(serializers.ModelSerializer):
    """
    Serializer for JobView model.
    """
    user_display = serializers.CharField(source='user.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_organization = serializers.CharField(source='job.organization', read_only=True)
    
    class Meta:
        model = JobView
        fields = [
            'id', 'job', 'job_title', 'job_organization', 'user', 'user_display',
            'session_id', 'ip_address', 'referrer', 'search_query',
            'came_from_alert', 'created_at', 'view_duration',
            'clicked_apply', 'bookmarked', 'shared'
        ]
        read_only_fields = ['id', 'created_at']


class SearchQuerySerializer(serializers.ModelSerializer):
    """
    Serializer for SearchQuery model.
    """
    user_display = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SearchQuery
        fields = [
            'id', 'query', 'filters_applied', 'results_count', 'user',
            'user_display', 'session_id', 'ip_address', 'response_time',
            'clicked_results', 'page_views', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for UserSession model.
    """
    user_display = serializers.CharField(source='user.username', read_only=True)
    session_duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'session_id', 'user', 'user_display', 'start_time',
            'last_activity', 'duration', 'session_duration_minutes',
            'ip_address', 'device_type', 'browser', 'os',
            'country', 'region', 'city', 'page_views', 'job_views',
            'searches', 'applications', 'bookmarks', 'converted', 'bounce'
        ]
        read_only_fields = ['id', 'start_time']
    
    def get_session_duration_minutes(self, obj):
        """Calculate session duration in minutes."""
        if obj.duration:
            return round(obj.duration / 60, 2)
        return None


class AlertEngagementSerializer(serializers.ModelSerializer):
    """
    Serializer for AlertEngagement model.
    """
    alert_name = serializers.CharField(source='alert.name', read_only=True)
    user_email = serializers.CharField(source='alert.user.email', read_only=True)
    
    class Meta:
        model = AlertEngagement
        fields = [
            'id', 'alert', 'alert_name', 'user_email', 'alert_log',
            'opened', 'clicked', 'jobs_clicked', 'applications_made',
            'bookmarks_made', 'sent_at', 'first_opened_at',
            'last_activity_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PerformanceMetricSerializer(serializers.ModelSerializer):
    """
    Serializer for PerformanceMetric model.
    """
    
    class Meta:
        model = PerformanceMetric
        fields = [
            'metric_type', 'value', 'unit', 'endpoint', 'source',
            'metadata', 'recorded_at'
        ]
        read_only_fields = ['recorded_at']


class DailyStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for DailyStats model.
    """
    conversion_rate = serializers.SerializerMethodField()
    pages_per_session = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyStats
        fields = [
            'date', 'unique_visitors', 'page_views', 'sessions',
            'bounce_rate', 'avg_session_duration', 'pages_per_session',
            'jobs_viewed', 'jobs_applied', 'jobs_bookmarked', 'jobs_shared',
            'searches_performed', 'avg_search_results', 'top_search_terms',
            'alerts_sent', 'alerts_opened', 'alerts_clicked',
            'new_jobs_added', 'jobs_updated', 'avg_response_time',
            'uptime_percentage', 'conversion_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_conversion_rate(self, obj):
        """Calculate conversion rate (applications / job views)."""
        if obj.jobs_viewed > 0:
            return round((obj.jobs_applied / obj.jobs_viewed) * 100, 2)
        return 0.0
    
    def get_pages_per_session(self, obj):
        """Calculate average pages per session."""
        if obj.sessions > 0:
            return round(obj.page_views / obj.sessions, 2)
        return 0.0


class ConversionFunnelSerializer(serializers.ModelSerializer):
    """
    Serializer for ConversionFunnel model.
    """
    user_display = serializers.CharField(source='user.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = ConversionFunnel
        fields = [
            'id', 'stage', 'user', 'user_display', 'session_id',
            'job', 'job_title', 'source_stage', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AnalyticsOverviewSerializer(serializers.Serializer):
    """
    Serializer for analytics overview data.
    """
    period = serializers.DictField()
    overview = serializers.DictField()
    daily_breakdown = serializers.ListField()
    top_pages = serializers.ListField()
    device_breakdown = serializers.ListField()


class JobAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for job analytics data.
    """
    period = serializers.DictField()
    overview = serializers.DictField()
    popular_jobs = serializers.ListField()
    daily_trends = serializers.ListField()


class SearchAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for search analytics data.
    """
    period = serializers.DictField()
    overview = serializers.DictField()
    popular_terms = serializers.ListField()
    zero_result_queries = serializers.ListField()


class ConversionFunnelAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for conversion funnel analytics data.
    """
    period = serializers.DictField()
    funnel = serializers.ListField()


class RealtimeStatsSerializer(serializers.Serializer):
    """
    Serializer for real-time statistics.
    """
    period = serializers.CharField()
    realtime = serializers.DictField()
    hourly_breakdown = serializers.ListField()


class PerformanceAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for performance analytics data.
    """
    period = serializers.DictField()
    metric_types = serializers.ListField()
    summary = serializers.ListField()
    details = serializers.ListField()


class EventTrackingSerializer(serializers.Serializer):
    """
    Serializer for event tracking requests.
    """
    event_type = serializers.ChoiceField(
        choices=['page_view', 'job_view', 'search', 'conversion']
    )
    data = serializers.DictField()
    
    def validate_data(self, value):
        """Validate event data based on event type."""
        event_type = self.initial_data.get('event_type')
        
        if event_type == 'page_view':
            required_fields = ['path']
            for field in required_fields:
                if field not in value:
                    raise serializers.ValidationError(
                        f"'{field}' is required for page_view events"
                    )
        
        elif event_type == 'conversion':
            required_fields = ['stage']
            for field in required_fields:
                if field not in value:
                    raise serializers.ValidationError(
                        f"'{field}' is required for conversion events"
                    )
        
        return value


class DailyStatsGenerationSerializer(serializers.Serializer):
    """
    Serializer for daily stats generation requests.
    """
    date = serializers.DateField(required=False)
    
    def validate_date(self, value):
        """Validate that date is not in the future."""
        from datetime import date
        if value and value > date.today():
            raise serializers.ValidationError(
                "Cannot generate stats for future dates"
            )
        return value


class DateRangeSerializer(serializers.Serializer):
    """
    Serializer for date range filters.
    """
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    
    def validate(self, data):
        """Validate date range."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "start_date must be before or equal to end_date"
            )
        
        return data


class DeviceBreakdownSerializer(serializers.Serializer):
    """
    Serializer for device breakdown analytics.
    """
    device_type = serializers.CharField()
    sessions = serializers.IntegerField()
    avg_duration = serializers.FloatField()
    bounce_rate = serializers.FloatField()


class PopularSearchTermSerializer(serializers.Serializer):
    """
    Serializer for popular search terms.
    """
    query = serializers.CharField()
    count = serializers.IntegerField()


class PopularJobSerializer(serializers.Serializer):
    """
    Serializer for popular jobs analytics.
    """
    job__title = serializers.CharField()
    job__id = serializers.UUIDField()
    views = serializers.IntegerField()
    unique_views = serializers.IntegerField()


class FunnelStageSerializer(serializers.Serializer):
    """
    Serializer for funnel stage data.
    """
    stage = serializers.CharField()
    users = serializers.IntegerField()
    conversion_rate = serializers.FloatField()


class HourlyDataSerializer(serializers.Serializer):
    """
    Serializer for hourly analytics data.
    """
    hour = serializers.CharField()
    page_views = serializers.IntegerField()


class MetricsSummarySerializer(serializers.Serializer):
    """
    Serializer for metrics summary data.
    """
    metric_type = serializers.CharField()
    count = serializers.IntegerField()
    avg_value = serializers.FloatField()
    min_value = serializers.FloatField()
    max_value = serializers.FloatField()
