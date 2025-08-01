"""
AI Search Views for SarkariBot
API endpoints for AI-powered search functionality.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import Q
from typing import Dict, Any
import logging

from .models import (
    SearchProfile, SearchSuggestion, QueryExpansion,
    SemanticMapping, SearchIntent, SearchFeedback
)
from .services import AISearchService, PersonalizationService, SearchAnalyticsService
from .serializers import (
    SearchProfileSerializer, SearchSuggestionSerializer,
    QueryExpansionSerializer, SemanticMappingSerializer,
    SearchIntentSerializer, SearchFeedbackSerializer
)

logger = logging.getLogger(__name__)


class AISearchViewSet(viewsets.ViewSet):
    """
    AI-powered search API endpoints.
    """
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def process_query(self, request):
        """
        Process search query with AI enhancements.
        
        Body:
        {
            "query": "software engineer jobs",
            "filters": {"location": "Delhi", "category": "IT"}
        }
        """
        try:
            query = request.data.get('query', '').strip()
            filters = request.data.get('filters', {})
            
            if not query:
                return Response(
                    {'error': 'Query parameter is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process query with AI
            user = request.user if request.user.is_authenticated else None
            enhanced_params = AISearchService.process_search_query(
                query=query,
                user=user,
                filters=filters
            )
            
            return Response(enhanced_params, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to process search query: {e}")
            return Response(
                {'error': 'Failed to process search query'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def suggestions(self, request):
        """
        Get search suggestions for autocomplete.
        
        Query Parameters:
        - q: Partial query string
        - limit: Maximum suggestions (default: 10)
        """
        try:
            query = request.query_params.get('q', '').strip()
            limit = int(request.query_params.get('limit', 10))
            
            if not query:
                return Response(
                    {'suggestions': []}, 
                    status=status.HTTP_200_OK
                )
            
            user = request.user if request.user.is_authenticated else None
            suggestions = AISearchService.get_search_suggestions(
                query=query,
                user=user,
                limit=min(limit, 20)  # Max 20 suggestions
            )
            
            return Response(
                {'suggestions': suggestions}, 
                status=status.HTTP_200_OK
            )
            
        except ValueError:
            return Response(
                {'error': 'Invalid limit parameter'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Failed to get search suggestions: {e}")
            return Response(
                {'error': 'Failed to get search suggestions'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def track_interaction(self, request):
        """
        Track search interaction for learning.
        
        Body:
        {
            "query": "software engineer",
            "interaction_type": "click|view|apply|bookmark",
            "job_id": "uuid",
            "position": 1,
            "metadata": {}
        }
        """
        try:
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            query = request.data.get('query', '')
            interaction_type = request.data.get('interaction_type', '')
            job_id = request.data.get('job_id', '')
            position = request.data.get('position', 0)
            metadata = request.data.get('metadata', {})
            
            # Update user profile based on interaction
            search_data = {
                'query': query,
                'clicked_jobs': [{'id': job_id, 'position': position}] if job_id else [],
                'interaction_type': interaction_type,
                'metadata': metadata
            }
            
            AISearchService.update_user_profile(request.user, search_data)
            
            return Response(
                {'message': 'Interaction tracked successfully'}, 
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Failed to track search interaction: {e}")
            return Response(
                {'error': 'Failed to track interaction'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def feedback(self, request):
        """
        Submit feedback on search results.
        
        Body:
        {
            "query": "software engineer",
            "job_id": "uuid",
            "feedback_type": "relevant|irrelevant|spam|outdated",
            "relevance_rating": 4,
            "comments": "Very relevant result"
        }
        """
        try:
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            query = request.data.get('query', '')
            job_id = request.data.get('job_id', '')
            feedback_type = request.data.get('feedback_type', '')
            relevance_rating = request.data.get('relevance_rating')
            comments = request.data.get('comments', '')
            
            if not all([query, job_id, feedback_type]):
                return Response(
                    {'error': 'query, job_id, and feedback_type are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            AISearchService.record_search_feedback(
                user=request.user,
                query=query,
                job_id=job_id,
                feedback_type=feedback_type,
                relevance_rating=relevance_rating,
                comments=comments
            )
            
            return Response(
                {'message': 'Feedback recorded successfully'}, 
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
            return Response(
                {'error': 'Failed to record feedback'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def personalized_ranking(self, request):
        """
        Get personalized ranking scores for jobs.
        
        Query Parameters:
        - job_ids: Comma-separated list of job IDs
        """
        try:
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            job_ids_param = request.query_params.get('job_ids', '')
            if not job_ids_param:
                return Response(
                    {'error': 'job_ids parameter is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            job_ids = [jid.strip() for jid in job_ids_param.split(',') if jid.strip()]
            
            if len(job_ids) > 100:  # Limit to prevent abuse
                return Response(
                    {'error': 'Maximum 100 job IDs allowed'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            rankings = PersonalizationService.calculate_personalized_ranking(
                user=request.user,
                job_ids=job_ids
            )
            
            return Response(
                {'rankings': rankings}, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Failed to get personalized ranking: {e}")
            return Response(
                {'error': 'Failed to get personalized ranking'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchProfileViewSet(viewsets.ModelViewSet):
    """
    User search profile management.
    """
    serializer_class = SearchProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return search profile for current user."""
        return SearchProfile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create search profile for current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get current user's search profile."""
        try:
            profile, created = SearchProfile.objects.get_or_create(
                user=request.user
            )
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get search profile: {e}")
            return Response(
                {'error': 'Failed to get search profile'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def update_preferences(self, request):
        """
        Update search preferences.
        
        Body:
        {
            "location_preferences": ["Delhi", "Mumbai"],
            "category_preferences": ["IT", "Banking"],
            "salary_range_min": 50000,
            "salary_range_max": 100000,
            "enable_ai_suggestions": true
        }
        """
        try:
            profile, created = SearchProfile.objects.get_or_create(
                user=request.user
            )
            
            # Update preferences
            location_prefs = request.data.get('location_preferences')
            if location_prefs is not None:
                profile.location_preferences = location_prefs
            
            category_prefs = request.data.get('category_preferences')
            if category_prefs is not None:
                profile.category_preferences = category_prefs
            
            organization_prefs = request.data.get('organization_preferences')
            if organization_prefs is not None:
                profile.organization_preferences = organization_prefs
            
            salary_min = request.data.get('salary_range_min')
            if salary_min is not None:
                profile.salary_range_min = salary_min
            
            salary_max = request.data.get('salary_range_max')
            if salary_max is not None:
                profile.salary_range_max = salary_max
            
            experience_level = request.data.get('experience_level')
            if experience_level is not None:
                profile.experience_level = experience_level
            
            education_prefs = request.data.get('education_preferences')
            if education_prefs is not None:
                profile.education_preferences = education_prefs
            
            enable_ai = request.data.get('enable_ai_suggestions')
            if enable_ai is not None:
                profile.enable_ai_suggestions = enable_ai
            
            enable_personalization = request.data.get('enable_personalization')
            if enable_personalization is not None:
                profile.enable_personalization = enable_personalization
            
            profile.save()
            
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to update search preferences: {e}")
            return Response(
                {'error': 'Failed to update preferences'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchAnalyticsViewSet(viewsets.ViewSet):
    """
    Search analytics and insights for admins.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 30))  # Cache for 30 minutes
    def performance(self, request):
        """
        Get search performance analytics.
        
        Query Parameters:
        - days: Number of days to analyze (default: 30)
        """
        try:
            days = int(request.query_params.get('days', 30))
            if days > 365:
                days = 365  # Limit to 1 year
            
            analytics = SearchAnalyticsService.analyze_search_performance(days)
            return Response(analytics, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response(
                {'error': 'Invalid days parameter'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Failed to get search analytics: {e}")
            return Response(
                {'error': 'Failed to get search analytics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_suggestions(self, request):
        """Generate new search suggestions based on user behavior."""
        try:
            SearchAnalyticsService.generate_search_suggestions()
            return Response(
                {'message': 'Search suggestions generated successfully'}, 
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return Response(
                {'error': 'Failed to generate suggestions'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def feedback_summary(self, request):
        """Get summary of user feedback on search results."""
        try:
            days = int(request.query_params.get('days', 30))
            
            # Get feedback summary
            feedback_summary = SearchFeedback.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=days)
            ).values('feedback_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Get average relevance rating
            avg_rating = SearchFeedback.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=days),
                relevance_rating__isnull=False
            ).aggregate(avg=Avg('relevance_rating'))['avg']
            
            return Response({
                'period': {'days': days},
                'feedback_breakdown': list(feedback_summary),
                'average_relevance_rating': round(avg_rating, 2) if avg_rating else None,
                'total_feedback': sum(item['count'] for item in feedback_summary)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get feedback summary: {e}")
            return Response(
                {'error': 'Failed to get feedback summary'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchManagementViewSet(viewsets.ViewSet):
    """
    Search configuration management for admins.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @action(detail=False, methods=['get', 'post'])
    def suggestions(self, request):
        """Manage search suggestions."""
        if request.method == 'GET':
            suggestions = SearchSuggestion.objects.filter(
                is_active=True
            ).order_by('-confidence_score')[:100]
            
            serializer = SearchSuggestionSerializer(suggestions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            serializer = SearchSuggestionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'post'])
    def query_expansions(self, request):
        """Manage query expansion rules."""
        if request.method == 'GET':
            expansions = QueryExpansion.objects.filter(
                is_active=True
            ).order_by('-effectiveness_score')
            
            serializer = QueryExpansionSerializer(expansions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            serializer = QueryExpansionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'post'])
    def semantic_mappings(self, request):
        """Manage semantic mappings."""
        if request.method == 'GET':
            mappings = SemanticMapping.objects.all().order_by('-confidence_score')
            serializer = SemanticMappingSerializer(mappings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            serializer = SemanticMappingSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'post'])
    def search_intents(self, request):
        """Manage search intent patterns."""
        if request.method == 'GET':
            intents = SearchIntent.objects.filter(is_active=True).order_by('-accuracy_score')
            serializer = SearchIntentSerializer(intents, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            serializer = SearchIntentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
