"""
Serializers for government sources API.

Provides serialization for government source data and statistics
according to Knowledge.md specifications.
"""

from rest_framework import serializers
from typing import Dict, Any
from django.utils import timezone
from django.db import models
from datetime import timedelta

from .models import GovernmentSource, SourceStatistics


class GovernmentSourceSerializer(serializers.ModelSerializer):
    """Basic serializer for government sources."""
    
    # Computed fields
    jobs_count = serializers.SerializerMethodField()
    last_scrape_status = serializers.SerializerMethodField()
    next_scrape_time = serializers.SerializerMethodField()
    
    class Meta:
        model = GovernmentSource
        fields = [
            'id', 'name', 'display_name', 'description',
            'base_url', 'active', 'scrape_frequency',
            'last_scraped', 'jobs_count', 'last_scrape_status',
            'next_scrape_time', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_jobs_count(self, obj) -> int:
        """Get total number of jobs from this source."""
        return obj.job_postings.count()
    
    def get_last_scrape_status(self, obj) -> str:
        """Get status of last scraping attempt."""
        # Get most recent scrape log
        recent_log = obj.scrape_logs.first()
        if recent_log:
            return recent_log.status
        return 'unknown'
    
    def get_next_scrape_time(self, obj) -> str:
        """Calculate next scheduled scrape time."""
        if not obj.last_scraped:
            return 'pending'
        
        next_scrape = obj.last_scraped + timedelta(hours=obj.scrape_frequency)
        if next_scrape <= timezone.now():
            return 'overdue'
        
        return next_scrape.isoformat()


class GovernmentSourceDetailSerializer(GovernmentSourceSerializer):
    """Detailed serializer for government source with full configuration."""
    
    # Additional detailed fields
    recent_statistics = serializers.SerializerMethodField()
    scraping_config = serializers.SerializerMethodField()
    performance_metrics = serializers.SerializerMethodField()
    
    class Meta(GovernmentSourceSerializer.Meta):
        fields = GovernmentSourceSerializer.Meta.fields + [
            'recent_statistics', 'scraping_config', 'performance_metrics'
        ]
    
    def get_recent_statistics(self, obj) -> Dict[str, Any]:
        """Get recent performance statistics."""
        # Get last 7 days of statistics
        week_ago = timezone.now() - timedelta(days=7)
        recent_stats = obj.statistics.filter(date__gte=week_ago)
        
        if not recent_stats.exists():
            return {
                'period': '7_days',
                'scrapes_attempted': 0,
                'scrapes_successful': 0,
                'jobs_found': 0,
                'success_rate': 0.0
            }
        
        total_attempted = sum(stat.scrapes_attempted for stat in recent_stats)
        total_successful = sum(stat.scrapes_successful for stat in recent_stats)
        total_jobs = sum(stat.jobs_found for stat in recent_stats)
        
        success_rate = (total_successful / total_attempted * 100) if total_attempted > 0 else 0.0
        
        return {
            'period': '7_days',
            'scrapes_attempted': total_attempted,
            'scrapes_successful': total_successful,
            'jobs_found': total_jobs,
            'success_rate': round(success_rate, 2)
        }
    
    def get_scraping_config(self, obj) -> Dict[str, Any]:
        """Get sanitized scraping configuration."""
        # Return public configuration only (no sensitive data)
        config = obj.config_json
        
        public_config = {
            'scrape_frequency_hours': obj.scrape_frequency,
            'active': obj.active,
            'supports_pagination': config.get('pagination', {}).get('enabled', False),
            'javascript_required': config.get('requires_javascript', False),
            'rate_limit_delay': config.get('rate_limit', {}).get('delay_seconds', 30)
        }
        
        return public_config
    
    def get_performance_metrics(self, obj) -> Dict[str, Any]:
        """Get overall performance metrics."""
        # Get last 30 days of statistics
        month_ago = timezone.now() - timedelta(days=30)
        month_stats = obj.statistics.filter(date__gte=month_ago)
        
        if not month_stats.exists():
            return {
                'uptime_percentage': 0.0,
                'avg_response_time': 0.0,
                'total_jobs_found': 0,
                'data_quality_score': 0.0
            }
        
        total_days = month_stats.count()
        successful_days = month_stats.filter(scrapes_successful__gt=0).count()
        uptime_percentage = (successful_days / total_days * 100) if total_days > 0 else 0.0
        
        avg_response_time = month_stats.aggregate(
            avg_time=models.Avg('average_response_time')
        )['avg_time'] or 0.0
        
        total_jobs = sum(stat.jobs_found for stat in month_stats)
        
        # Calculate data quality score based on completeness
        avg_quality = month_stats.aggregate(
            avg_quality=models.Avg('average_quality_score')
        )['avg_quality'] or 0.0
        
        return {
            'uptime_percentage': round(uptime_percentage, 2),
            'avg_response_time': round(avg_response_time, 3),
            'total_jobs_found': total_jobs,
            'data_quality_score': round(avg_quality, 2)
        }


class SourceStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for source statistics."""
    
    source_name = serializers.CharField(source='source.name', read_only=True)
    success_rate = serializers.SerializerMethodField()
    efficiency_score = serializers.SerializerMethodField()
    
    class Meta:
        model = SourceStatistics
        fields = [
            'id', 'source', 'source_name', 'date',
            'scrapes_attempted', 'scrapes_successful', 'scrapes_failed',
            'jobs_found', 'jobs_created', 'jobs_updated',
            'average_response_time', 'total_pages_scraped',
            'average_quality_score', 'success_rate', 'efficiency_score',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_success_rate(self, obj) -> float:
        """Calculate success rate percentage."""
        if obj.scrapes_attempted == 0:
            return 0.0
        return round((obj.scrapes_successful / obj.scrapes_attempted) * 100, 2)
    
    def get_efficiency_score(self, obj) -> float:
        """Calculate efficiency score based on jobs found per scrape."""
        if obj.scrapes_successful == 0:
            return 0.0
        return round(obj.jobs_found / obj.scrapes_successful, 2)


class SourceConfigurationSerializer(serializers.Serializer):
    """Serializer for source configuration validation."""
    
    base_url = serializers.URLField(required=True)
    scrape_frequency = serializers.IntegerField(min_value=1, max_value=168)  # 1 hour to 1 week
    is_active = serializers.BooleanField(default=True)
    
    # Scraping configuration
    requires_javascript = serializers.BooleanField(default=False)
    rate_limit_delay = serializers.IntegerField(min_value=5, max_value=300, default=30)
    max_pages = serializers.IntegerField(min_value=1, max_value=100, default=10)
    
    # Selectors configuration
    job_title_selector = serializers.CharField(max_length=500, required=True)
    job_description_selector = serializers.CharField(max_length=500, required=False)
    job_link_selector = serializers.CharField(max_length=500, required=True)
    pagination_selector = serializers.CharField(max_length=500, required=False)
    
    def validate_base_url(self, value):
        """Validate base URL is accessible."""
        import requests
        try:
            response = requests.head(value, timeout=10)
            if response.status_code >= 400:
                raise serializers.ValidationError(
                    f"URL returned status code {response.status_code}"
                )
        except requests.RequestException as e:
            raise serializers.ValidationError(f"URL is not accessible: {str(e)}")
        
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        # If pagination selector is provided, ensure max_pages > 1
        if data.get('pagination_selector') and data.get('max_pages', 1) <= 1:
            raise serializers.ValidationError(
                "max_pages must be greater than 1 when pagination_selector is provided"
            )
        
        return data
