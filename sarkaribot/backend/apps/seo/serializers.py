"""
Serializers for SEO app API endpoints.

Handles serialization and deserialization of SEO-related models
according to Knowledge.md specifications.
"""

from rest_framework import serializers
from .models import SEOMetadata, KeywordTracking, SitemapEntry, SEOAuditLog


class SEOMetadataSerializer(serializers.ModelSerializer):
    """
    Serializer for SEO metadata model.
    
    Handles comprehensive SEO metadata including title, description,
    keywords, and structured data.
    """
    
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = SEOMetadata
        fields = [
            'id',
            'content_type',
            'content_type_name',
            'object_id',
            'page_type',
            'seo_title',
            'seo_description',
            'keywords',
            'canonical_url',
            'meta_robots',
            'og_title',
            'og_description',
            'og_image',
            'og_type',
            'twitter_title',
            'twitter_description',
            'twitter_image',
            'twitter_card',
            'structured_data',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'content_type_name']
    
    def validate_seo_title(self, value):
        """Validate SEO title length."""
        if len(value) > 60:
            raise serializers.ValidationError("SEO title must be 60 characters or less.")
        if len(value) < 30:
            raise serializers.ValidationError("SEO title should be at least 30 characters.")
        return value
    
    def validate_seo_description(self, value):
        """Validate SEO description length."""
        if len(value) > 160:
            raise serializers.ValidationError("SEO description must be 160 characters or less.")
        if len(value) < 120:
            raise serializers.ValidationError("SEO description should be at least 120 characters.")
        return value


class KeywordTrackingSerializer(serializers.ModelSerializer):
    """
    Serializer for keyword tracking model.
    
    Tracks keyword usage and performance metrics.
    """
    
    job_title = serializers.CharField(source='job_posting.title', read_only=True)
    
    class Meta:
        model = KeywordTracking
        fields = [
            'id',
            'keyword',
            'job_posting',
            'job_title',
            'frequency',
            'position',
            'context',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'job_title']
    
    def validate_keyword(self, value):
        """Validate keyword format."""
        if len(value) < 2:
            raise serializers.ValidationError("Keyword must be at least 2 characters long.")
        if len(value) > 100:
            raise serializers.ValidationError("Keyword must be 100 characters or less.")
        return value.lower().strip()


class SitemapEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for sitemap entry model.
    
    Manages sitemap entries for SEO optimization.
    """
    
    class Meta:
        model = SitemapEntry
        fields = [
            'id',
            'url',
            'url_type',
            'priority',
            'change_frequency',
            'last_modified',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_url(self, value):
        """Validate URL format."""
        if not value.startswith(('http://', 'https://', '/')):
            raise serializers.ValidationError("URL must be a valid absolute or relative URL.")
        return value
    
    def validate_priority(self, value):
        """Validate priority range."""
        if not (0.0 <= value <= 1.0):
            raise serializers.ValidationError("Priority must be between 0.0 and 1.0.")
        return value


class SEOAuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for SEO audit log model.
    
    Tracks SEO operations and their outcomes for auditing.
    """
    
    class Meta:
        model = SEOAuditLog
        fields = [
            'id',
            'action_type',
            'details',
            'status',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SEOGenerateRequestSerializer(serializers.Serializer):
    """
    Serializer for SEO metadata generation requests.
    """
    
    job_id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False)
    source = serializers.CharField(max_length=100, required=False)
    category = serializers.CharField(max_length=100, required=False)
    last_date = serializers.CharField(max_length=50, required=False)
    
    def validate(self, data):
        """Validate that either job_id or title+description is provided."""
        if not data.get('job_id') and not (data.get('title') and data.get('description')):
            raise serializers.ValidationError(
                "Either job_id or both title and description must be provided."
            )
        return data


class SEOAnalysisSerializer(serializers.Serializer):
    """
    Serializer for SEO analysis responses.
    """
    
    seo_score = serializers.IntegerField()
    recommendations = serializers.ListField(child=serializers.CharField())
    metadata_analysis = serializers.DictField()
    keyword_analysis = serializers.DictField()
    performance_metrics = serializers.DictField()
    timestamp = serializers.DateTimeField()


class SEOStatsSerializer(serializers.Serializer):
    """
    Serializer for SEO statistics responses.
    """
    
    total_metadata = serializers.IntegerField()
    total_keywords = serializers.IntegerField()
    total_sitemap_entries = serializers.IntegerField()
    avg_seo_score = serializers.FloatField()
    recent_activity = serializers.ListField()
    top_keywords = serializers.ListField()
    performance_trends = serializers.DictField()
