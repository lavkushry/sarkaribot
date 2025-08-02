"""
AI-powered Advanced Search Models for SarkariBot (SQLite-compatible version)
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class SearchProfile(models.Model):
    """
    User search profile for personalized recommendations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='search_profile')
    
    # Preferences (stored as JSON in SQLite-compatible format)
    location_preferences = models.JSONField(default=list, blank=True)
    category_preferences = models.JSONField(default=list, blank=True)
    organization_preferences = models.JSONField(default=list, blank=True)
    education_preferences = models.JSONField(default=list, blank=True)
    
    # Search behavior analysis
    search_frequency = models.IntegerField(default=0)
    preferred_search_time = models.TimeField(null=True, blank=True)
    avg_session_duration = models.DurationField(null=True, blank=True)
    
    # Machine learning features
    preference_vector = models.TextField(blank=True, help_text="Serialized preference vector")
    learning_rate = models.FloatField(default=0.1)
    confidence_score = models.FloatField(default=0.0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['last_active']),
        ]
    
    def __str__(self):
        return f"Search Profile for {self.user.username}"


class SearchSuggestion(models.Model):
    """
    AI-generated search suggestions based on user behavior and popular searches.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Suggestion content
    suggestion_text = models.CharField(max_length=255, db_index=True)
    suggestion_type = models.CharField(
        max_length=50,
        choices=[
            ('keyword', 'Keyword Suggestion'),
            ('phrase', 'Phrase Suggestion'), 
            ('category', 'Category Suggestion'),
            ('location', 'Location Suggestion'),
            ('organization', 'Organization Suggestion'),
        ],
        default='keyword'
    )
    
    # AI relevance metrics
    relevance_score = models.FloatField(default=0.0)
    popularity_score = models.FloatField(default=0.0)
    freshness_score = models.FloatField(default=0.0)
    final_score = models.FloatField(default=0.0, db_index=True)
    
    # Usage tracking
    times_suggested = models.IntegerField(default=0)
    times_clicked = models.IntegerField(default=0)
    conversion_rate = models.FloatField(default=0.0)
    
    # Context and metadata
    context = models.JSONField(default=dict, blank=True, help_text="Additional context for the suggestion")
    
    # Lifecycle management
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-final_score', '-created_at']
        indexes = [
            models.Index(fields=['suggestion_type', 'final_score']),
            models.Index(fields=['is_active', 'expires_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.suggestion_text} ({self.suggestion_type})"


class QueryExpansion(models.Model):
    """
    Query expansion rules for improving search results.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Original and expanded query
    original_query = models.CharField(max_length=255, db_index=True)
    expanded_terms = models.JSONField(default=list, blank=True)
    
    # Expansion strategy
    expansion_type = models.CharField(
        max_length=50,
        choices=[
            ('synonym', 'Synonym Expansion'),
            ('related', 'Related Terms'),
            ('domain', 'Domain-specific Terms'),
            ('autocorrect', 'Auto-correction'),
            ('abbreviation', 'Abbreviation Expansion'),
        ],
        default='synonym'
    )
    
    # Performance metrics
    effectiveness_score = models.FloatField(default=0.0)
    usage_count = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    
    # Management
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='query_expansions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effectiveness_score', '-created_at']
        indexes = [
            models.Index(fields=['original_query']),
            models.Index(fields=['expansion_type', 'is_active']),
            models.Index(fields=['effectiveness_score']),
        ]
    
    def __str__(self):
        return f"Expansion: {self.original_query} -> {len(self.expanded_terms)} terms"


class SemanticMapping(models.Model):
    """
    Semantic mappings for understanding job-related concepts and relationships.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Core concept
    concept = models.CharField(max_length=255, db_index=True, unique=True)
    concept_type = models.CharField(
        max_length=50,
        choices=[
            ('skill', 'Skill/Competency'),
            ('qualification', 'Educational Qualification'),
            ('department', 'Government Department'),
            ('position', 'Job Position/Title'),
            ('location', 'Geographic Location'),
            ('category', 'Job Category'),
        ],
        default='skill'
    )
    
    # Semantic relationships
    related_terms = models.JSONField(default=list, blank=True)
    
    # Vector representation for AI similarity
    embedding_vector = models.JSONField(null=True, blank=True, help_text="Vector representation of the concept")
    
    # Usage and confidence metrics
    confidence_score = models.FloatField(default=0.0)
    usage_frequency = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Metadata
    source = models.CharField(max_length=100, blank=True, help_text="Source of the mapping")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['concept']
        indexes = [
            models.Index(fields=['concept_type', 'confidence_score']),
            models.Index(fields=['is_verified', 'usage_frequency']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.concept} ({self.concept_type})"


class SearchIntent(models.Model):
    """
    Classification and understanding of user search intents.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Intent classification
    intent_name = models.CharField(max_length=100, db_index=True)
    intent_category = models.CharField(
        max_length=50,
        choices=[
            ('informational', 'Informational Query'),
            ('navigational', 'Navigational Query'),
            ('transactional', 'Application Intent'),
            ('comparison', 'Comparison Shopping'),
            ('temporal', 'Time-sensitive Query'),
        ],
        default='informational'
    )
    
    # Intent parameters and configuration
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Parameters for intent processing"
    )
    
    # Search optimization
    boost_fields = models.JSONField(default=list, blank=True)
    filter_conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Default filters for this intent"
    )
    
    # Performance tracking
    accuracy_score = models.FloatField(default=0.0)
    precision_score = models.FloatField(default=0.0)
    recall_score = models.FloatField(default=0.0)
    
    # Management
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['intent_name']
        indexes = [
            models.Index(fields=['intent_category', 'is_active']),
            models.Index(fields=['accuracy_score']),
        ]
    
    def __str__(self):
        return f"{self.intent_name} ({self.intent_category})"


class SearchFeedback(models.Model):
    """
    User feedback on search results for continuous improvement.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Feedback context
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='search_feedback'
    )
    session_id = models.CharField(max_length=255, db_index=True)
    search_query = models.CharField(max_length=255)
    result_position = models.IntegerField(help_text="Position of the result in search results")
    
    # Feedback data
    feedback_type = models.CharField(
        max_length=50,
        choices=[
            ('click', 'Result Clicked'),
            ('bookmark', 'Result Bookmarked'),
            ('apply', 'Application Started'),
            ('irrelevant', 'Marked as Irrelevant'),
            ('spam', 'Marked as Spam'),
            ('outdated', 'Marked as Outdated'),
        ],
        default='click'
    )
    
    relevance_rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        null=True,
        blank=True,
        help_text="1-5 relevance rating"
    )
    
    # Additional context
    dwell_time = models.DurationField(null=True, blank=True)
    search_context = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'feedback_type']),
            models.Index(fields=['search_query', 'relevance_rating']),
            models.Index(fields=['created_at']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Feedback: {self.feedback_type} for '{self.search_query}'"
