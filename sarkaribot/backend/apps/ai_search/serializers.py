"""
AI Search Serializers for SarkariBot
DRF serializers for AI search models and data structures.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    SearchProfile, SearchSuggestion, QueryExpansion,
    SemanticMapping, SearchIntent, PersonalizedRanking,
    SearchFeedback, AISearchMetrics
)

User = get_user_model()


class SearchProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for SearchProfile model.
    """
    user_display = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SearchProfile
        fields = [
            'id', 'user', 'user_display', 'location_preferences',
            'category_preferences', 'organization_preferences',
            'salary_range_min', 'salary_range_max', 'experience_level',
            'education_preferences', 'search_frequency', 'avg_search_terms',
            'preferred_search_time', 'personalization_score',
            'enable_ai_suggestions', 'enable_personalization',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'search_frequency', 'avg_search_terms',
            'personalization_score', 'created_at', 'updated_at'
        ]


class SearchSuggestionSerializer(serializers.ModelSerializer):
    """
    Serializer for SearchSuggestion model.
    """
    user_display = serializers.CharField(source='user.username', read_only=True)
    click_through_rate_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = SearchSuggestion
        fields = [
            'id', 'query', 'suggested_query', 'suggestion_type',
            'context', 'confidence_score', 'times_shown', 'times_clicked',
            'click_through_rate', 'click_through_rate_percentage',
            'user', 'user_display', 'location', 'category',
            'is_active', 'created_at', 'expires_at'
        ]
        read_only_fields = [
            'id', 'times_shown', 'times_clicked', 'click_through_rate',
            'created_at'
        ]
    
    def get_click_through_rate_percentage(self, obj):
        """Get click-through rate as percentage."""
        return round(obj.click_through_rate * 100, 2)


class QueryExpansionSerializer(serializers.ModelSerializer):
    """
    Serializer for QueryExpansion model.
    """
    created_by_display = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = QueryExpansion
        fields = [
            'id', 'original_term', 'expanded_terms', 'expansion_type',
            'effectiveness_score', 'usage_count', 'domain', 'language',
            'is_active', 'created_by', 'created_by_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'effectiveness_score', 'usage_count',
            'created_by', 'created_at', 'updated_at'
        ]


class SemanticMappingSerializer(serializers.ModelSerializer):
    """
    Serializer for SemanticMapping model.
    """
    
    class Meta:
        model = SemanticMapping
        fields = [
            'id', 'concept', 'related_terms', 'category',
            'embedding_vector', 'confidence_score', 'usage_frequency',
            'source', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'usage_frequency', 'created_at', 'updated_at'
        ]


class SearchIntentSerializer(serializers.ModelSerializer):
    """
    Serializer for SearchIntent model.
    """
    
    class Meta:
        model = SearchIntent
        fields = [
            'id', 'query_pattern', 'intent_type', 'parameters',
            'boost_fields', 'filter_conditions', 'accuracy_score',
            'usage_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'accuracy_score', 'usage_count',
            'created_at', 'updated_at'
        ]


class PersonalizedRankingSerializer(serializers.ModelSerializer):
    """
    Serializer for PersonalizedRanking model.
    """
    user_display = serializers.CharField(source='user.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = PersonalizedRanking
        fields = [
            'id', 'user', 'user_display', 'job', 'job_title',
            'relevance_score', 'location_match', 'category_match',
            'qualification_match', 'experience_match', 'salary_match',
            'view_history_score', 'application_likelihood',
            'final_score', 'calculated_at', 'expires_at'
        ]
        read_only_fields = ['id', 'calculated_at']


class SearchFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for SearchFeedback model.
    """
    user_display = serializers.CharField(source='user.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = SearchFeedback
        fields = [
            'id', 'user', 'user_display', 'query', 'job', 'job_title',
            'feedback_type', 'relevance_rating', 'comments',
            'search_context', 'result_position', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class AISearchMetricsSerializer(serializers.ModelSerializer):
    """
    Serializer for AISearchMetrics model.
    """
    suggestion_ctr_percentage = serializers.SerializerMethodField()
    feedback_sentiment = serializers.SerializerMethodField()
    
    class Meta:
        model = AISearchMetrics
        fields = [
            'id', 'date', 'avg_relevance_score', 'personalization_effectiveness',
            'query_understanding_accuracy', 'ai_suggestions_shown',
            'ai_suggestions_clicked', 'suggestion_ctr_percentage',
            'personalized_searches', 'intent_detection_success',
            'avg_search_response_time', 'search_success_rate',
            'zero_result_rate', 'positive_feedback_count',
            'negative_feedback_count', 'feedback_response_rate',
            'feedback_sentiment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_suggestion_ctr_percentage(self, obj):
        """Calculate suggestion click-through rate percentage."""
        if obj.ai_suggestions_shown > 0:
            return round((obj.ai_suggestions_clicked / obj.ai_suggestions_shown) * 100, 2)
        return 0.0
    
    def get_feedback_sentiment(self, obj):
        """Calculate feedback sentiment score."""
        total_feedback = obj.positive_feedback_count + obj.negative_feedback_count
        if total_feedback > 0:
            return round((obj.positive_feedback_count / total_feedback) * 100, 2)
        return 0.0


class SearchQueryProcessingSerializer(serializers.Serializer):
    """
    Serializer for search query processing requests.
    """
    query = serializers.CharField(max_length=255)
    filters = serializers.DictField(required=False, default=dict)
    
    def validate_query(self, value):
        """Validate search query."""
        if not value.strip():
            raise serializers.ValidationError("Query cannot be empty")
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Query must be at least 2 characters")
        
        return value.strip()


class SearchSuggestionRequestSerializer(serializers.Serializer):
    """
    Serializer for search suggestion requests.
    """
    q = serializers.CharField(max_length=255)
    limit = serializers.IntegerField(min_value=1, max_value=20, default=10)
    
    def validate_q(self, value):
        """Validate query parameter."""
        if not value.strip():
            raise serializers.ValidationError("Query parameter cannot be empty")
        return value.strip()


class SearchInteractionTrackingSerializer(serializers.Serializer):
    """
    Serializer for search interaction tracking.
    """
    query = serializers.CharField(max_length=255)
    interaction_type = serializers.ChoiceField(
        choices=['click', 'view', 'apply', 'bookmark', 'share']
    )
    job_id = serializers.UUIDField(required=False)
    position = serializers.IntegerField(min_value=0, default=0)
    metadata = serializers.DictField(required=False, default=dict)
    
    def validate(self, data):
        """Validate interaction data."""
        interaction_type = data.get('interaction_type')
        job_id = data.get('job_id')
        
        # Job ID required for certain interaction types
        if interaction_type in ['click', 'view', 'apply', 'bookmark'] and not job_id:
            raise serializers.ValidationError(
                f"job_id is required for {interaction_type} interactions"
            )
        
        return data


class SearchFeedbackSubmissionSerializer(serializers.Serializer):
    """
    Serializer for search feedback submission.
    """
    query = serializers.CharField(max_length=255)
    job_id = serializers.UUIDField()
    feedback_type = serializers.ChoiceField(
        choices=[
            'relevant', 'irrelevant', 'spam', 'outdated',
            'wrong_category', 'location_mismatch'
        ]
    )
    relevance_rating = serializers.IntegerField(
        min_value=1, max_value=5, required=False
    )
    comments = serializers.CharField(max_length=1000, required=False, default="")


class PersonalizedRankingRequestSerializer(serializers.Serializer):
    """
    Serializer for personalized ranking requests.
    """
    job_ids = serializers.CharField()
    
    def validate_job_ids(self, value):
        """Validate job IDs list."""
        job_ids = [jid.strip() for jid in value.split(',') if jid.strip()]
        
        if not job_ids:
            raise serializers.ValidationError("At least one job ID is required")
        
        if len(job_ids) > 100:
            raise serializers.ValidationError("Maximum 100 job IDs allowed")
        
        # Validate UUID format
        import uuid
        for job_id in job_ids:
            try:
                uuid.UUID(job_id)
            except ValueError:
                raise serializers.ValidationError(f"Invalid job ID format: {job_id}")
        
        return job_ids


class SearchPreferencesUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating search preferences.
    """
    location_preferences = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        max_length=10
    )
    category_preferences = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        max_length=10
    )
    organization_preferences = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False,
        max_length=10
    )
    salary_range_min = serializers.IntegerField(min_value=0, required=False)
    salary_range_max = serializers.IntegerField(min_value=0, required=False)
    experience_level = serializers.ChoiceField(
        choices=['entry', 'mid', 'senior', 'executive'],
        required=False
    )
    education_preferences = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        max_length=10
    )
    enable_ai_suggestions = serializers.BooleanField(required=False)
    enable_personalization = serializers.BooleanField(required=False)
    
    def validate(self, data):
        """Validate salary range."""
        salary_min = data.get('salary_range_min')
        salary_max = data.get('salary_range_max')
        
        if salary_min is not None and salary_max is not None:
            if salary_min > salary_max:
                raise serializers.ValidationError(
                    "salary_range_min must be less than or equal to salary_range_max"
                )
        
        return data


class SearchAnalyticsResponseSerializer(serializers.Serializer):
    """
    Serializer for search analytics response.
    """
    period = serializers.DictField()
    overview = serializers.DictField()
    popular_terms = serializers.ListField()
    zero_result_terms = serializers.ListField()


class SearchPerformanceMetricsSerializer(serializers.Serializer):
    """
    Serializer for search performance metrics.
    """
    total_searches = serializers.IntegerField()
    avg_results_per_search = serializers.FloatField()
    zero_result_rate = serializers.FloatField()
    avg_response_time = serializers.FloatField()


class FeedbackSummarySerializer(serializers.Serializer):
    """
    Serializer for feedback summary data.
    """
    period = serializers.DictField()
    feedback_breakdown = serializers.ListField()
    average_relevance_rating = serializers.FloatField(allow_null=True)
    total_feedback = serializers.IntegerField()


class SearchSuggestionResponseSerializer(serializers.Serializer):
    """
    Serializer for search suggestion response.
    """
    suggestions = serializers.ListField()


class PersonalizedRankingResponseSerializer(serializers.Serializer):
    """
    Serializer for personalized ranking response.
    """
    rankings = serializers.DictField()


class EnhancedSearchParametersSerializer(serializers.Serializer):
    """
    Serializer for enhanced search parameters response.
    """
    original_query = serializers.CharField()
    normalized_query = serializers.CharField()
    intent = serializers.DictField(allow_null=True)
    expanded_terms = serializers.ListField()
    semantic_keywords = serializers.ListField()
    personalized_boost = serializers.DictField()
    filters = serializers.DictField()
    boost_fields = serializers.ListField()
    search_type = serializers.CharField()


class SearchSuggestionDetailSerializer(serializers.Serializer):
    """
    Serializer for individual search suggestion details.
    """
    suggested_query = serializers.CharField()
    type = serializers.CharField()
    confidence_score = serializers.FloatField()
    context = serializers.DictField()


class FeedbackBreakdownSerializer(serializers.Serializer):
    """
    Serializer for feedback breakdown data.
    """
    feedback_type = serializers.CharField()
    count = serializers.IntegerField()


class PopularSearchTermSerializer(serializers.Serializer):
    """
    Serializer for popular search terms.
    """
    query = serializers.CharField()
    count = serializers.IntegerField()


class ZeroResultTermSerializer(serializers.Serializer):
    """
    Serializer for zero result search terms.
    """
    query = serializers.CharField()
    count = serializers.IntegerField()
