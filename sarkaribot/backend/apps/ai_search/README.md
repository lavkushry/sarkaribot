# AI-Powered Advanced Search for SarkariBot

This app provides intelligent search capabilities with machine learning enhancements for better job discovery and user experience.

## Features

### AI-Powered Search Processing
- **Query Enhancement**: Automatic query normalization and expansion
- **Intent Detection**: Understand user search intent (job search, results, notifications)
- **Semantic Search**: Related term matching and concept understanding
- **Query Suggestions**: Smart autocomplete and search suggestions
- **Spell Correction**: Automatic correction of common misspellings

### Personalization
- **User Profiles**: Learn from user search behavior and preferences
- **Personalized Rankings**: Customize search results based on user history
- **Preference Learning**: Automatic extraction of location, category, and other preferences
- **Behavioral Analytics**: Track and learn from user interactions

### Advanced Features
- **Semantic Mappings**: Understand relationships between job terms
- **Query Expansion**: Expand searches with synonyms and related terms
- **Feedback Learning**: Improve results based on user feedback
- **Real-time Analytics**: Monitor search performance and effectiveness

## Models

### Core Models
- `SearchProfile`: User search preferences and behavior patterns
- `SearchSuggestion`: AI-generated search suggestions
- `QueryExpansion`: Query expansion rules and synonyms
- `SemanticMapping`: Semantic relationships between terms
- `SearchIntent`: Intent detection patterns
- `PersonalizedRanking`: User-specific job ranking factors
- `SearchFeedback`: User feedback for continuous improvement
- `AISearchMetrics`: Performance metrics and analytics

## Services

### AISearchService
Core AI search functionality:
- `process_search_query()`: Enhance queries with AI
- `get_search_suggestions()`: Generate smart suggestions
- `update_user_profile()`: Learn from user behavior
- `record_search_feedback()`: Collect user feedback

### PersonalizationService
Personalized search experience:
- `calculate_personalized_ranking()`: Rank jobs for users
- `_calculate_job_score()`: Score individual jobs

### SearchAnalyticsService
Analytics and insights:
- `analyze_search_performance()`: Performance metrics
- `generate_search_suggestions()`: Auto-generate suggestions

## API Endpoints

### AI Search (`/api/ai-search/ai/`)
- `POST process_query/`: Process and enhance search queries
- `GET suggestions/`: Get search suggestions
- `POST track_interaction/`: Track user interactions
- `POST feedback/`: Submit search feedback
- `GET personalized_ranking/`: Get personalized job rankings

### Search Profile (`/api/ai-search/profile/`)
- `GET my_profile/`: Get user's search profile
- `POST update_preferences/`: Update search preferences

### Analytics (`/api/ai-search/analytics/`)
- `GET performance/`: Search performance analytics
- `POST generate_suggestions/`: Generate new suggestions
- `GET feedback_summary/`: User feedback summary

### Management (`/api/ai-search/management/`)
- `GET/POST suggestions/`: Manage search suggestions
- `GET/POST query_expansions/`: Manage query expansions
- `GET/POST semantic_mappings/`: Manage semantic mappings
- `GET/POST search_intents/`: Manage intent patterns

## Usage Examples

### Process Search Query
```python
from apps.ai_search.services import AISearchService

# Enhance a search query
enhanced = AISearchService.process_search_query(
    query="software engineer jobs delhi",
    user=request.user,
    filters={"experience": "mid"}
)

# Use enhanced parameters for search
# enhanced['normalized_query'] - cleaned query
# enhanced['expanded_terms'] - related terms
# enhanced['intent'] - detected intent
# enhanced['personalized_boost'] - user preferences
```

### Get Search Suggestions
```python
# Get autocomplete suggestions
suggestions = AISearchService.get_search_suggestions(
    query="softw",
    user=request.user,
    limit=10
)

# Returns list of suggested queries with confidence scores
for suggestion in suggestions:
    print(f"{suggestion['suggested_query']} ({suggestion['confidence_score']})")
```

### Track User Interactions
```python
# Update user profile based on search behavior
AISearchService.update_user_profile(request.user, {
    'query': 'python developer',
    'filters': {'location': 'Mumbai'},
    'clicked_jobs': [{'id': 'job-id', 'category': 'IT'}]
})

# Record user feedback
AISearchService.record_search_feedback(
    user=request.user,
    query='python developer',
    job_id='job-id',
    feedback_type='relevant',
    relevance_rating=5
)
```

### Personalized Rankings
```python
from apps.ai_search.services import PersonalizationService

# Get personalized rankings for jobs
rankings = PersonalizationService.calculate_personalized_ranking(
    user=request.user,
    job_ids=['job1', 'job2', 'job3']
)

# Apply rankings to search results
# Higher scores = more relevant for the user
```

## Configuration

Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... other apps
    'apps.ai_search',
]
```

Add to main `urls.py`:
```python
urlpatterns = [
    # ... other patterns
    path('search/', include('apps.ai_search.urls')),
]
```

## Integration with Main Search

The AI search service is designed to enhance existing search functionality:

1. **Query Processing**: Use `AISearchService.process_search_query()` before executing searches
2. **Result Ranking**: Apply personalized rankings to search results
3. **Suggestions**: Integrate autocomplete suggestions in search UI
4. **Analytics**: Track search interactions for continuous improvement

## Machine Learning Integration

The system is designed to integrate with ML services:

- **Vector Embeddings**: Store semantic embeddings for concepts
- **Recommendation Engine**: Can integrate with external ML models
- **Natural Language Processing**: Expandable for advanced NLP features
- **Feedback Loop**: Continuous learning from user interactions

## Privacy and Performance

- **Privacy**: User preferences stored securely, can be anonymized
- **Caching**: Search suggestions and rankings are cached for performance
- **Background Processing**: Heavy ML operations can run asynchronously
- **Scalability**: Designed for high-volume search scenarios
