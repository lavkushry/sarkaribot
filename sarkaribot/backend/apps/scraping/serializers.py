"""
Serializers for scraping app API endpoints.

Defines serializers for scraping models and data transformation.
"""

from rest_framework import serializers
from .models import ScrapeLog, ScrapedData, SourceStatistics, ScrapingError, ProxyConfiguration
from apps.sources.models import GovernmentSource


class ScrapeLogSerializer(serializers.ModelSerializer):
    """Serializer for ScrapeLog model."""
    
    source_name = serializers.CharField(source='source.name', read_only=True)
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = ScrapeLog
        fields = [
            'id', 'source', 'source_name', 'task_id', 'started_at', 'completed_at',
            'duration_seconds', 'status', 'scraper_engine', 'config_snapshot',
            'pages_scraped', 'requests_made', 'average_response_time',
            'jobs_found', 'jobs_created', 'jobs_updated', 'jobs_skipped',
            'error_message', 'error_count', 'warnings_count', 'success_rate'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at', 'success_rate']


class ScrapedDataSerializer(serializers.ModelSerializer):
    """Serializer for ScrapedData model."""
    
    source_name = serializers.CharField(source='source.name', read_only=True)
    job_title = serializers.SerializerMethodField()
    is_high_quality = serializers.ReadOnlyField()
    
    class Meta:
        model = ScrapedData
        fields = [
            'id', 'source', 'source_name', 'scrape_log', 'job_posting',
            'raw_data', 'source_url', 'content_hash', 'processing_status',
            'processing_error', 'processed_at', 'data_quality_score',
            'field_count', 'job_title', 'is_high_quality', 'created_at'
        ]
        read_only_fields = ['id', 'content_hash', 'is_high_quality', 'created_at']
    
    def get_job_title(self, obj):
        """Extract job title from raw data."""
        if obj.raw_data and 'title' in obj.raw_data:
            return obj.raw_data['title']
        return 'No Title'


class SourceStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for SourceStatistics model."""
    
    source_name = serializers.CharField(source='source.name', read_only=True)
    success_rate = serializers.ReadOnlyField()
    jobs_per_scrape = serializers.ReadOnlyField()
    creation_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = SourceStatistics
        fields = [
            'id', 'source', 'source_name', 'date', 'scrapes_attempted',
            'scrapes_successful', 'scrapes_failed', 'jobs_found',
            'jobs_created', 'jobs_updated', 'average_response_time',
            'total_pages_scraped', 'average_quality_score',
            'success_rate', 'jobs_per_scrape', 'creation_rate'
        ]
        read_only_fields = ['id', 'success_rate', 'jobs_per_scrape', 'creation_rate']


class ScrapingErrorSerializer(serializers.ModelSerializer):
    """Serializer for ScrapingError model."""
    
    class Meta:
        model = ScrapingError
        fields = [
            'id', 'scrape_log', 'error_type', 'error_message', 'stack_trace',
            'url', 'selector', 'occurred_at', 'retry_count', 'resolved',
            'resolution_notes'
        ]
        read_only_fields = ['id', 'occurred_at']


class ProxyConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for ProxyConfiguration model."""
    
    proxy_url = serializers.ReadOnlyField()
    
    class Meta:
        model = ProxyConfiguration
        fields = [
            'id', 'host', 'port', 'proxy_type', 'username', 'password',
            'status', 'last_tested', 'success_rate', 'average_response_time',
            'requests_made', 'successful_requests', 'failed_requests',
            'proxy_url'
        ]
        read_only_fields = [
            'id', 'last_tested', 'success_rate', 'average_response_time',
            'requests_made', 'successful_requests', 'failed_requests', 'proxy_url'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }


class ScrapeJobSerializer(serializers.Serializer):
    """Serializer for scrape job requests."""
    
    source_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of source IDs to scrape"
    )
    scrape_all = serializers.BooleanField(
        default=False,
        help_text="Scrape all active sources"
    )
    async_execution = serializers.BooleanField(
        default=True,
        help_text="Execute scraping asynchronously"
    )
    priority = serializers.ChoiceField(
        choices=['low', 'normal', 'high'],
        default='normal',
        help_text="Task priority"
    )
    
    def validate(self, data):
        """Validate that either source_ids or scrape_all is provided."""
        if not data.get('source_ids') and not data.get('scrape_all'):
            raise serializers.ValidationError(
                "Either 'source_ids' or 'scrape_all' must be provided."
            )
        return data


class ScrapingStatsSerializer(serializers.Serializer):
    """Serializer for scraping statistics responses."""
    
    total_scrapes = serializers.IntegerField()
    successful_scrapes = serializers.IntegerField()
    failed_scrapes = serializers.IntegerField()
    total_jobs_found = serializers.IntegerField()
    total_jobs_created = serializers.IntegerField()
    average_success_rate = serializers.FloatField()
    period_start = serializers.DateField()
    period_end = serializers.DateField()


class SourcePerformanceSerializer(serializers.Serializer):
    """Serializer for source performance data."""
    
    source_id = serializers.IntegerField()
    source_name = serializers.CharField()
    success_rate = serializers.FloatField()
    total_jobs = serializers.IntegerField()
    average_jobs_per_scrape = serializers.FloatField()
    scrape_frequency = serializers.IntegerField()
    total_scrapes = serializers.IntegerField()
    last_scraped = serializers.DateTimeField(allow_null=True)


class QualityAnalysisSerializer(serializers.Serializer):
    """Serializer for data quality analysis."""
    
    total_items = serializers.IntegerField()
    excellent_count = serializers.IntegerField()
    good_count = serializers.IntegerField()
    fair_count = serializers.IntegerField()
    poor_count = serializers.IntegerField()
    average_quality = serializers.FloatField()
    recommendations = serializers.ListField(
        child=serializers.CharField()
    )
