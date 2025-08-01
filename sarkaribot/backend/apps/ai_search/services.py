"""
AI-powered Search Services for SarkariBot
Advanced search algorithms with machine learning capabilities.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from django.db.models import Q, F, Count, Avg
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from collections import defaultdict, Counter
import json

from .models import (
    SearchProfile, SearchSuggestion, QueryExpansion, 
    SemanticMapping, SearchIntent, PersonalizedRanking, SearchFeedback
)

logger = logging.getLogger(__name__)
User = get_user_model()


class AISearchService:
    """
    Core AI-powered search service with intelligent query processing.
    """
    
    @staticmethod
    def process_search_query(
        query: str, 
        user: User = None, 
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process search query with AI enhancements.
        
        Args:
            query: Raw search query
            user: User making the search
            filters: Additional filters
            
        Returns:
            Enhanced search parameters
        """
        try:
            # Normalize query
            normalized_query = AISearchService._normalize_query(query)
            
            # Detect search intent
            intent = AISearchService._detect_intent(normalized_query)
            
            # Expand query with synonyms and related terms
            expanded_terms = AISearchService._expand_query(normalized_query)
            
            # Apply personalization if user is provided
            personalized_boost = {}
            if user:
                personalized_boost = AISearchService._get_personalization_boost(user)
            
            # Generate semantic keywords
            semantic_keywords = AISearchService._generate_semantic_keywords(normalized_query)
            
            # Prepare enhanced search parameters
            enhanced_params = {
                'original_query': query,
                'normalized_query': normalized_query,
                'intent': intent,
                'expanded_terms': expanded_terms,
                'semantic_keywords': semantic_keywords,
                'personalized_boost': personalized_boost,
                'filters': filters or {},
                'boost_fields': intent.get('boost_fields', []) if intent else [],
                'search_type': intent.get('type', 'general') if intent else 'general'
            }
            
            logger.info(f"Enhanced search query: {query} -> {enhanced_params['search_type']}")
            return enhanced_params
            
        except Exception as e:
            logger.error(f"Failed to process search query '{query}': {e}")
            return {
                'original_query': query,
                'normalized_query': query,
                'intent': None,
                'expanded_terms': [query],
                'semantic_keywords': [],
                'personalized_boost': {},
                'filters': filters or {},
                'boost_fields': [],
                'search_type': 'general'
            }
    
    @staticmethod
    def get_search_suggestions(
        query: str, 
        user: User = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get AI-powered search suggestions.
        
        Args:
            query: Partial search query
            user: User requesting suggestions
            limit: Maximum number of suggestions
            
        Returns:
            List of search suggestions
        """
        try:
            suggestions = []
            
            # Get autocomplete suggestions
            autocomplete = AISearchService._get_autocomplete_suggestions(query, limit=5)
            suggestions.extend(autocomplete)
            
            # Get personalized suggestions for authenticated users
            if user:
                personalized = AISearchService._get_personalized_suggestions(user, query, limit=3)
                suggestions.extend(personalized)
            
            # Get trending suggestions
            trending = AISearchService._get_trending_suggestions(query, limit=2)
            suggestions.extend(trending)
            
            # Remove duplicates and rank by confidence
            unique_suggestions = {}
            for suggestion in suggestions:
                key = suggestion['suggested_query'].lower()
                if key not in unique_suggestions or suggestion['confidence_score'] > unique_suggestions[key]['confidence_score']:
                    unique_suggestions[key] = suggestion
            
            # Sort by confidence and return top results
            ranked_suggestions = sorted(
                unique_suggestions.values(),
                key=lambda x: x['confidence_score'],
                reverse=True
            )[:limit]
            
            logger.info(f"Generated {len(ranked_suggestions)} suggestions for query: {query}")
            return ranked_suggestions
            
        except Exception as e:
            logger.error(f"Failed to get search suggestions for '{query}': {e}")
            return []
    
    @staticmethod
    def update_user_profile(user: User, search_data: Dict[str, Any]):
        """
        Update user search profile based on search behavior.
        
        Args:
            user: User to update
            search_data: Search interaction data
        """
        try:
            profile, created = SearchProfile.objects.get_or_create(user=user)
            
            # Update preferences based on search data
            query = search_data.get('query', '')
            filters = search_data.get('filters', {})
            clicked_jobs = search_data.get('clicked_jobs', [])
            
            # Extract location preferences
            if 'location' in filters:
                location = filters['location']
                if location and location not in profile.location_preferences:
                    profile.location_preferences.append(location)
                    profile.location_preferences = profile.location_preferences[-10:]  # Keep last 10
            
            # Extract category preferences from clicked jobs
            for job_data in clicked_jobs:
                category = job_data.get('category')
                if category and category not in profile.category_preferences:
                    profile.category_preferences.append(category)
                    profile.category_preferences = profile.category_preferences[-10:]
            
            # Update search frequency
            profile.search_frequency = F('search_frequency') * 0.9 + 0.1  # Exponential moving average
            
            # Update personalization score
            profile.personalization_score = min(
                profile.personalization_score + 0.1,
                1.0
            )
            
            profile.save()
            
            logger.info(f"Updated search profile for user: {user.username}")
            
        except Exception as e:
            logger.error(f"Failed to update user profile for {user.username}: {e}")
    
    @staticmethod
    def record_search_feedback(
        user: User,
        query: str,
        job_id: str,
        feedback_type: str,
        relevance_rating: int = None,
        comments: str = ""
    ):
        """
        Record user feedback on search results.
        
        Args:
            user: User providing feedback
            query: Search query
            job_id: Job ID for feedback
            feedback_type: Type of feedback
            relevance_rating: 1-5 rating
            comments: Additional comments
        """
        try:
            SearchFeedback.objects.create(
                user=user,
                query=query,
                job_id=job_id,
                feedback_type=feedback_type,
                relevance_rating=relevance_rating,
                comments=comments,
                search_context={
                    'timestamp': datetime.now().isoformat(),
                    'user_agent': 'web'  # Could be passed from request
                }
            )
            
            logger.info(f"Recorded search feedback: {feedback_type} for query '{query}'")
            
        except Exception as e:
            logger.error(f"Failed to record search feedback: {e}")
    
    @staticmethod
    def _normalize_query(query: str) -> str:
        """Normalize search query."""
        # Convert to lowercase
        query = query.lower().strip()
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query)
        
        # Handle common abbreviations
        abbreviations = {
            'govt': 'government',
            'eng': 'engineer',
            'mgr': 'manager',
            'asst': 'assistant',
            'jr': 'junior',
            'sr': 'senior',
        }
        
        for abbr, full in abbreviations.items():
            query = re.sub(r'\b' + abbr + r'\b', full, query)
        
        return query
    
    @staticmethod
    def _detect_intent(query: str) -> Optional[Dict[str, Any]]:
        """Detect search intent from query."""
        try:
            # Check against stored intent patterns
            intent_mapping = SearchIntent.objects.filter(is_active=True)
            
            for intent in intent_mapping:
                pattern = intent.query_pattern
                if re.search(pattern, query, re.IGNORECASE):
                    return {
                        'type': intent.intent_type,
                        'boost_fields': intent.boost_fields,
                        'filters': intent.filter_conditions,
                        'confidence': intent.accuracy_score
                    }
            
            # Fallback to rule-based detection
            if any(word in query for word in ['notification', 'recruitment', 'vacancy']):
                return {
                    'type': 'job_search',
                    'boost_fields': ['title', 'description'],
                    'filters': {},
                    'confidence': 0.8
                }
            
            if any(word in query for word in ['result', 'score', 'marks']):
                return {
                    'type': 'result_search',
                    'boost_fields': ['title'],
                    'filters': {'type': 'result'},
                    'confidence': 0.7
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect intent for query '{query}': {e}")
            return None
    
    @staticmethod
    def _expand_query(query: str) -> List[str]:
        """Expand query with synonyms and related terms."""
        try:
            expanded_terms = [query]
            
            # Get query expansions
            words = query.split()
            for word in words:
                expansions = QueryExpansion.objects.filter(
                    original_term__iexact=word,
                    is_active=True
                ).first()
                
                if expansions:
                    expanded_terms.extend(expansions.expanded_terms)
            
            # Get semantic mappings
            for word in words:
                mappings = SemanticMapping.objects.filter(
                    concept__iexact=word
                ).first()
                
                if mappings:
                    expanded_terms.extend(mappings.related_terms[:3])  # Limit to top 3
            
            # Remove duplicates and return
            return list(set(expanded_terms))
            
        except Exception as e:
            logger.error(f"Failed to expand query '{query}': {e}")
            return [query]
    
    @staticmethod
    def _generate_semantic_keywords(query: str) -> List[str]:
        """Generate semantic keywords for enhanced matching."""
        try:
            keywords = []
            
            # Extract key terms
            words = query.split()
            
            # Get related terms from semantic mappings
            for word in words:
                mappings = SemanticMapping.objects.filter(
                    related_terms__icontains=word
                ).values_list('concept', flat=True)[:5]
                
                keywords.extend(mappings)
            
            return list(set(keywords))
            
        except Exception as e:
            logger.error(f"Failed to generate semantic keywords for '{query}': {e}")
            return []
    
    @staticmethod
    def _get_personalization_boost(user: User) -> Dict[str, float]:
        """Get personalization boost factors for user."""
        try:
            profile = SearchProfile.objects.filter(user=user).first()
            if not profile:
                return {}
            
            boost = {}
            
            # Location boost
            if profile.location_preferences:
                boost['location'] = {
                    'values': profile.location_preferences,
                    'boost': 1.5
                }
            
            # Category boost
            if profile.category_preferences:
                boost['category'] = {
                    'values': profile.category_preferences,
                    'boost': 1.3
                }
            
            # Organization boost
            if profile.organization_preferences:
                boost['organization'] = {
                    'values': profile.organization_preferences,
                    'boost': 1.2
                }
            
            return boost
            
        except Exception as e:
            logger.error(f"Failed to get personalization boost for {user.username}: {e}")
            return {}
    
    @staticmethod
    def _get_autocomplete_suggestions(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get autocomplete suggestions."""
        try:
            suggestions = SearchSuggestion.objects.filter(
                query__istartswith=query,
                suggestion_type='autocomplete',
                is_active=True
            ).order_by('-confidence_score', '-click_through_rate')[:limit]
            
            return [
                {
                    'suggested_query': s.suggested_query,
                    'type': s.suggestion_type,
                    'confidence_score': s.confidence_score,
                    'context': s.context
                }
                for s in suggestions
            ]
            
        except Exception as e:
            logger.error(f"Failed to get autocomplete suggestions: {e}")
            return []
    
    @staticmethod
    def _get_personalized_suggestions(user: User, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get personalized suggestions for user."""
        try:
            suggestions = SearchSuggestion.objects.filter(
                user=user,
                suggestion_type='personalized',
                is_active=True
            ).order_by('-confidence_score')[:limit]
            
            return [
                {
                    'suggested_query': s.suggested_query,
                    'type': s.suggestion_type,
                    'confidence_score': s.confidence_score,
                    'context': s.context
                }
                for s in suggestions
            ]
            
        except Exception as e:
            logger.error(f"Failed to get personalized suggestions: {e}")
            return []
    
    @staticmethod
    def _get_trending_suggestions(query: str, limit: int = 2) -> List[Dict[str, Any]]:
        """Get trending search suggestions."""
        try:
            suggestions = SearchSuggestion.objects.filter(
                suggestion_type='trending',
                is_active=True
            ).order_by('-times_clicked', '-confidence_score')[:limit]
            
            return [
                {
                    'suggested_query': s.suggested_query,
                    'type': s.suggestion_type,
                    'confidence_score': s.confidence_score,
                    'context': s.context
                }
                for s in suggestions
            ]
            
        except Exception as e:
            logger.error(f"Failed to get trending suggestions: {e}")
            return []


class PersonalizationService:
    """
    Service for personalized search ranking and recommendations.
    """
    
    @staticmethod
    def calculate_personalized_ranking(user: User, job_ids: List[str]) -> Dict[str, float]:
        """
        Calculate personalized ranking scores for jobs.
        
        Args:
            user: User to personalize for
            job_ids: List of job IDs to rank
            
        Returns:
            Dictionary mapping job IDs to ranking scores
        """
        try:
            # Get existing rankings
            existing_rankings = PersonalizedRanking.objects.filter(
                user=user,
                job_id__in=job_ids,
                expires_at__gt=datetime.now()
            ).values_list('job_id', 'final_score')
            
            ranking_dict = dict(existing_rankings)
            
            # Calculate rankings for missing jobs
            missing_job_ids = set(job_ids) - set(ranking_dict.keys())
            
            if missing_job_ids:
                new_rankings = PersonalizationService._calculate_new_rankings(
                    user, list(missing_job_ids)
                )
                ranking_dict.update(new_rankings)
            
            return ranking_dict
            
        except Exception as e:
            logger.error(f"Failed to calculate personalized ranking: {e}")
            return {job_id: 0.5 for job_id in job_ids}  # Default score
    
    @staticmethod
    def _calculate_new_rankings(user: User, job_ids: List[str]) -> Dict[str, float]:
        """Calculate new personalized rankings."""
        try:
            from apps.jobs.models import JobPosting
            
            profile = SearchProfile.objects.filter(user=user).first()
            if not profile:
                return {job_id: 0.5 for job_id in job_ids}
            
            rankings = {}
            jobs = JobPosting.objects.filter(id__in=job_ids)
            
            for job in jobs:
                score = PersonalizationService._calculate_job_score(profile, job)
                rankings[str(job.id)] = score
                
                # Store ranking for future use
                PersonalizedRanking.objects.update_or_create(
                    user=user,
                    job=job,
                    defaults={
                        'final_score': score,
                        'expires_at': datetime.now() + timedelta(hours=24)
                    }
                )
            
            return rankings
            
        except Exception as e:
            logger.error(f"Failed to calculate new rankings: {e}")
            return {job_id: 0.5 for job_id in job_ids}
    
    @staticmethod
    def _calculate_job_score(profile: SearchProfile, job) -> float:
        """Calculate individual job score for user."""
        try:
            score = 0.5  # Base score
            
            # Location match
            if (profile.location_preferences and 
                job.location in profile.location_preferences):
                score += 0.2
            
            # Category match
            if (profile.category_preferences and 
                job.category in profile.category_preferences):
                score += 0.15
            
            # Organization match
            if (profile.organization_preferences and 
                job.organization in profile.organization_preferences):
                score += 0.1
            
            # Experience level match
            if (profile.experience_level and 
                job.experience_required == profile.experience_level):
                score += 0.1
            
            # Salary range match
            if (profile.salary_range_min and profile.salary_range_max and
                job.salary_min and job.salary_max):
                if (job.salary_min <= profile.salary_range_max and
                    job.salary_max >= profile.salary_range_min):
                    score += 0.05
            
            # Normalize score to 0-1 range
            return min(max(score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate job score: {e}")
            return 0.5


class SearchAnalyticsService:
    """
    Service for analyzing and improving search performance.
    """
    
    @staticmethod
    def analyze_search_performance(days: int = 30) -> Dict[str, Any]:
        """
        Analyze search performance metrics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Search performance analytics
        """
        try:
            from apps.analytics.models import SearchQuery
            
            start_date = datetime.now() - timedelta(days=days)
            
            # Get search queries
            queries = SearchQuery.objects.filter(created_at__gte=start_date)
            
            # Calculate metrics
            total_searches = queries.count()
            avg_results = queries.aggregate(avg=Avg('results_count'))['avg'] or 0
            zero_result_queries = queries.filter(results_count=0).count()
            avg_response_time = queries.aggregate(avg=Avg('response_time'))['avg'] or 0
            
            # Popular search terms
            popular_terms = queries.values('query').annotate(
                count=Count('id')
            ).order_by('-count')[:20]
            
            # Zero result queries analysis
            zero_result_terms = queries.filter(
                results_count=0
            ).values('query').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            return {
                'period': {'days': days, 'start_date': start_date.date()},
                'overview': {
                    'total_searches': total_searches,
                    'avg_results_per_search': round(avg_results, 2),
                    'zero_result_rate': round(zero_result_queries / total_searches * 100, 2) if total_searches > 0 else 0,
                    'avg_response_time': round(avg_response_time, 4)
                },
                'popular_terms': list(popular_terms),
                'zero_result_terms': list(zero_result_terms)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze search performance: {e}")
            return {}
    
    @staticmethod
    def generate_search_suggestions():
        """Generate new search suggestions based on user behavior."""
        try:
            from apps.analytics.models import SearchQuery
            
            # Get popular search terms from last 30 days
            popular_queries = SearchQuery.objects.filter(
                created_at__gte=datetime.now() - timedelta(days=30)
            ).values('query').annotate(
                count=Count('id'),
                avg_results=Avg('results_count')
            ).filter(
                count__gte=5,  # Minimum 5 searches
                avg_results__gt=0  # Had results
            ).order_by('-count')[:100]
            
            # Create autocomplete suggestions
            for query_data in popular_queries:
                query = query_data['query']
                count = query_data['count']
                avg_results = query_data['avg_results']
                
                # Generate variations
                words = query.split()
                for i in range(1, len(words) + 1):
                    partial_query = ' '.join(words[:i])
                    
                    SearchSuggestion.objects.update_or_create(
                        query=partial_query,
                        suggested_query=query,
                        suggestion_type='autocomplete',
                        defaults={
                            'confidence_score': min(count / 100.0, 1.0),
                            'times_shown': 0,
                            'times_clicked': 0,
                            'is_active': True,
                            'context': {
                                'avg_results': avg_results,
                                'popularity': count
                            }
                        }
                    )
            
            logger.info(f"Generated suggestions for {len(popular_queries)} popular queries")
            
        except Exception as e:
            logger.error(f"Failed to generate search suggestions: {e}")
