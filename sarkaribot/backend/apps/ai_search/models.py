"""
AI-powered Advanced Search Models for SarkariBot
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils import timezone
import uuid

User = get_user_model()


class SearchProfile(models.Model):
    """
    User search profile for personalized recommendations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='search_profile')
    
    # Preference vectors (would be calculated from user behavior)
    location_preferences = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Preferred job locations"
    )
    
    category_preferences = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Preferred job categories"
    )
    
    organization_preferences = ArrayField(
        models.CharField(max_length=200),
        default=list,
        blank=True,
        help_text="Preferred organizations"
    )
    
    salary_range_min = models.IntegerField(null=True, blank=True)
    salary_range_max = models.IntegerField(null=True, blank=True)
    
    # Experience and education preferences
    experience_level = models.CharField(
        max_length=50,
        choices=[
            ('entry', 'Entry Level'),
            ('mid', 'Mid Level'),
            ('senior', 'Senior Level'),
            ('executive', 'Executive'),
        ],
        blank=True
    )
    
    education_preferences = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Preferred education requirements"
    )
    
    # Behavioral data
    search_frequency = models.FloatField(default=0.0, help_text="Searches per day")
    avg_search_terms = models.IntegerField(default=0, help_text="Average search terms used")
    preferred_search_time = models.TimeField(null=True, blank=True)
    
    # AI features
    personalization_score = models.FloatField(default=0.0, help_text="How well we understand user preferences")
    last_updated = models.DateTimeField(auto_now=True)
    
    # Settings
    enable_ai_suggestions = models.BooleanField(default=True)
    enable_personalization = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['-last_updated']),
        ]
    
    def __str__(self):
        return f"Search Profile for {self.user.username}"


class SearchSuggestion(models.Model):
    """
    AI-generated search suggestions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Base query information
    query = models.CharField(max_length=255, db_index=True)
    suggested_query = models.CharField(max_length=255)
    suggestion_type = models.CharField(
        max_length=50,
        choices=[
            ('autocomplete', 'Autocomplete'),
            ('spelling', 'Spelling Correction'),
            ('synonym', 'Synonym Expansion'),
            ('related', 'Related Terms'),
            ('trending', 'Trending Searches'),
            ('personalized', 'Personalized Suggestion'),
        ],
        db_index=True
    )
    
    # Context and metadata
    context = JSONField(default=dict, blank=True, help_text="Additional context for the suggestion")
    confidence_score = models.FloatField(default=0.0, help_text="AI confidence in suggestion")
    
    # Usage statistics
    times_shown = models.IntegerField(default=0)
    times_clicked = models.IntegerField(default=0)
    click_through_rate = models.FloatField(default=0.0)
    
    # Targeting
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True)
    
    # Lifecycle
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-confidence_score', '-click_through_rate']
        indexes = [
            models.Index(fields=['query', 'suggestion_type']),
            models.Index(fields=['is_active', '-confidence_score']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"'{self.query}' -> '{self.suggested_query}'"


class QueryExpansion(models.Model):
    """
    Query expansion rules and mappings.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    original_term = models.CharField(max_length=100, db_index=True)
    expanded_terms = ArrayField(
        models.CharField(max_length=100),
        help_text="Terms to expand the original with"
    )
    
    expansion_type = models.CharField(
        max_length=50,
        choices=[
            ('synonym', 'Synonym'),
            ('abbreviation', 'Abbreviation'),
            ('category', 'Category Expansion'),
            ('location', 'Location Expansion'),
            ('skill', 'Skill Expansion'),
        ],
        db_index=True
    )
    
    # Quality metrics
    effectiveness_score = models.FloatField(default=0.0)
    usage_count = models.IntegerField(default=0)
    
    # Context
    domain = models.CharField(max_length=100, blank=True, help_text="Domain this expansion applies to")
    language = models.CharField(max_length=10, default='en')
    
    # Lifecycle
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effectiveness_score']
        indexes = [
            models.Index(fields=['original_term', 'expansion_type']),
            models.Index(fields=['is_active', '-effectiveness_score']),
        ]
    
    def __str__(self):
        return f"{self.original_term} -> {', '.join(self.expanded_terms[:3])}"


class SemanticMapping(models.Model):
    """
    Semantic mappings for intelligent search understanding.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    concept = models.CharField(max_length=100, unique=True, db_index=True)
    related_terms = ArrayField(
        models.CharField(max_length=100),
        help_text="Semantically related terms"
    )
    
    # Semantic categories
    category = models.CharField(
        max_length=50,
        choices=[
            ('job_title', 'Job Title'),
            ('skill', 'Skill'),
            ('qualification', 'Qualification'),
            ('location', 'Location'),
            ('organization', 'Organization'),
            ('department', 'Department'),
            ('benefit', 'Benefit'),
        ],
        db_index=True
    )
    
    # Vector embeddings (if using ML)
    embedding_vector = JSONField(null=True, blank=True, help_text="Vector representation of the concept")
    
    # Quality and usage
    confidence_score = models.FloatField(default=0.0)
    usage_frequency = models.IntegerField(default=0)
    
    # Metadata
    source = models.CharField(
        max_length=50,
        choices=[
            ('manual', 'Manual Entry'),
            ('ml_generated', 'ML Generated'),
            ('user_feedback', 'User Feedback'),
            ('data_mining', 'Data Mining'),
        ],
        default='manual'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-confidence_score', '-usage_frequency']
        indexes = [
            models.Index(fields=['concept']),
            models.Index(fields=['category', '-confidence_score']),
        ]
    
    def __str__(self):
        return f"{self.concept} ({self.category})"


class SearchIntent(models.Model):
    """
    Detected search intent for better result ranking.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    query_pattern = models.CharField(max_length=255, unique=True)
    intent_type = models.CharField(
        max_length=50,
        choices=[
            ('job_search', 'Job Search'),
            ('notification_search', 'Notification Search'),
            ('result_search', 'Result Search'),
            ('admit_card_search', 'Admit Card Search'),
            ('syllabus_search', 'Syllabus Search'),
            ('application_search', 'Application Search'),
            ('eligibility_search', 'Eligibility Search'),
            ('salary_search', 'Salary Search'),
        ],
        db_index=True
    )
    
    # Intent parameters
    parameters = JSONField(
        default=dict,
        blank=True,
        help_text="Parameters extracted from the query"
    )
    
    # Ranking adjustments
    boost_fields = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Fields to boost for this intent"
    )
    
    filter_conditions = JSONField(
        default=dict,
        blank=True,
        help_text="Additional filters to apply"
    )
    
    # Performance metrics
    accuracy_score = models.FloatField(default=0.0)
    usage_count = models.IntegerField(default=0)
    
    # Lifecycle
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-accuracy_score', '-usage_count']
        indexes = [
            models.Index(fields=['intent_type', 'is_active']),
            models.Index(fields=['-accuracy_score']),
        ]
    
    def __str__(self):
        return f"{self.query_pattern} -> {self.intent_type}"


class PersonalizedRanking(models.Model):
    """
    Store personalized ranking factors for users.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ranking_factors')
    job = models.ForeignKey('jobs.JobPosting', on_delete=models.CASCADE)
    
    # Ranking factors
    relevance_score = models.FloatField(default=0.0)
    location_match = models.FloatField(default=0.0)
    category_match = models.FloatField(default=0.0)
    qualification_match = models.FloatField(default=0.0)
    experience_match = models.FloatField(default=0.0)
    salary_match = models.FloatField(default=0.0)
    
    # Behavioral factors
    view_history_score = models.FloatField(default=0.0)
    application_likelihood = models.FloatField(default=0.0)
    
    # Combined score
    final_score = models.FloatField(default=0.0, db_index=True)
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        unique_together = ['user', 'job']
        ordering = ['-final_score']
        indexes = [
            models.Index(fields=['user', '-final_score']),
            models.Index(fields=['job', '-final_score']),
            models.Index(fields=['-calculated_at']),
        ]
    
    def __str__(self):
        return f"Ranking for {self.user.username} - {self.job.title}"


class SearchFeedback(models.Model):
    """
    User feedback on search results for ML training.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    job = models.ForeignKey('jobs.JobPosting', on_delete=models.CASCADE)
    
    # Feedback types
    feedback_type = models.CharField(
        max_length=50,
        choices=[
            ('relevant', 'Relevant Result'),
            ('irrelevant', 'Irrelevant Result'),
            ('spam', 'Spam/Duplicate'),
            ('outdated', 'Outdated'),
            ('wrong_category', 'Wrong Category'),
            ('location_mismatch', 'Location Mismatch'),
        ]
    )
    
    # Detailed feedback
    relevance_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        null=True,
        blank=True,
        help_text="1-5 relevance rating"
    )
    
    comments = models.TextField(blank=True)
    
    # Context
    search_context = JSONField(default=dict, blank=True)
    result_position = models.IntegerField(help_text="Position in search results")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['query', 'feedback_type']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Feedback: {self.feedback_type} for '{self.query}'"


class AISearchMetrics(models.Model):
    """
    Metrics for AI search performance tracking.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    date = models.DateField(unique=True, db_index=True)
    
    # Search quality metrics
    avg_relevance_score = models.FloatField(default=0.0)
    personalization_effectiveness = models.FloatField(default=0.0)
    query_understanding_accuracy = models.FloatField(default=0.0)
    
    # Usage metrics
    ai_suggestions_shown = models.IntegerField(default=0)
    ai_suggestions_clicked = models.IntegerField(default=0)
    personalized_searches = models.IntegerField(default=0)
    intent_detection_success = models.IntegerField(default=0)
    
    # Performance metrics
    avg_search_response_time = models.FloatField(default=0.0)
    search_success_rate = models.FloatField(default=0.0)
    zero_result_rate = models.FloatField(default=0.0)
    
    # Feedback metrics
    positive_feedback_count = models.IntegerField(default=0)
    negative_feedback_count = models.IntegerField(default=0)
    feedback_response_rate = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date']),
        ]
    
    def __str__(self):
        return f"AI Search Metrics for {self.date}"
