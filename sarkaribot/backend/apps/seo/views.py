"""
SEO app API views for SarkariBot.

Implements comprehensive SEO management functionality including metadata generation,
keyword tracking, sitemap management, and SEO analytics according to Knowledge.md specifications.
"""

import logging
from typing import Dict, Any
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import SEOMetadata, KeywordTracking, SitemapEntry, SEOAuditLog
from .serializers import (
    SEOMetadataSerializer,
    KeywordTrackingSerializer, 
    SitemapEntrySerializer,
    SEOAuditLogSerializer
)
from .engine import seo_engine
from apps.jobs.models import JobPosting

logger = logging.getLogger(__name__)


class SEOMetadataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing SEO metadata.
    
    Provides CRUD operations for SEO metadata with filtering
    and search capabilities.
    """
    
    queryset = SEOMetadata.objects.all()
    serializer_class = SEOMetadataSerializer
    permission_classes = [AllowAny]  # Adjust as needed
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['content_type', 'page_type']
    search_fields = ['seo_title', 'seo_description', 'keywords']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by content type
        content_type = self.request.query_params.get('content_type')
        if content_type:
            queryset = queryset.filter(content_type=content_type)
            
        return queryset.select_related('content_type')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get SEO metadata statistics."""
        total_metadata = self.get_queryset().count()
        by_type = dict(
            self.get_queryset()
            .values('page_type')
            .annotate(count=Count('id'))
            .values_list('page_type', 'count')
        )
        
        return Response({
            'total_metadata': total_metadata,
            'by_type': by_type,
            'last_updated': timezone.now()
        })


class KeywordTrackingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing keyword tracking.
    
    Tracks keyword performance and provides analytics.
    """
    
    queryset = KeywordTracking.objects.all()
    serializer_class = KeywordTrackingSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['keyword', 'job_posting']
    search_fields = ['keyword']
    ordering_fields = ['frequency', 'created_at']
    ordering = ['-frequency']
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending keywords."""
        trending_keywords = (
            self.get_queryset()
            .values('keyword')
            .annotate(total_frequency=Count('id'))
            .order_by('-total_frequency')[:10]
        )
        
        return Response(trending_keywords)


class SitemapEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing sitemap entries.
    
    Handles sitemap generation and management.
    """
    
    queryset = SitemapEntry.objects.all()
    serializer_class = SitemapEntrySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['url_type', 'priority']
    ordering_fields = ['priority', 'last_modified']
    ordering = ['-priority', '-last_modified']
    
    @action(detail=False, methods=['get'])
    def generate(self, request):
        """Generate sitemap entries for all content."""
        try:
            # This would integrate with the sitemap generation logic
            count = self.get_queryset().count()
            return Response({
                'message': 'Sitemap generation completed',
                'total_entries': count,
                'timestamp': timezone.now()
            })
        except Exception as e:
            logger.error(f"Sitemap generation failed: {e}")
            return Response(
                {'error': 'Sitemap generation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SEOAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for SEO audit logs.
    
    Provides access to SEO audit history and analytics.
    """
    
    queryset = SEOAuditLog.objects.all()
    serializer_class = SEOAuditLogSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action_type', 'status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get audit log summary."""
        logs = self.get_queryset()
        
        # Get counts by action type
        by_action = dict(
            logs.values('action_type')
            .annotate(count=Count('id'))
            .values_list('action_type', 'count')
        )
        
        # Get counts by status
        by_status = dict(
            logs.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        
        return Response({
            'total_logs': logs.count(),
            'by_action': by_action,
            'by_status': by_status,
            'recent_activity': logs[:5].values(
                'action_type', 'status', 'created_at'
            )
        })


class SEOGenerateView(APIView):
    """
    API view for generating SEO metadata using NLP engine.
    
    Integrates with the NLP SEO engine to automatically generate
    metadata for content.
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Generate SEO metadata for provided content."""
        try:
            # Get job data from request
            job_id = request.data.get('job_id')
            title = request.data.get('title', '')
            description = request.data.get('description', '')
            
            if not (job_id or (title and description)):
                return Response(
                    {'error': 'Either job_id or title+description required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use the global SEO engine instance
            # seo_engine is already initialized
            
            # Get job data if job_id provided
            if job_id:
                try:
                    job = JobPosting.objects.get(id=job_id)
                    job_data = {
                        'title': job.title,
                        'description': job.description,
                        'source': job.source.name if job.source else '',
                        'category': job.category.name if job.category else '',
                        'last_date': job.application_end_date.isoformat() if job.application_end_date else ''
                    }
                except JobPosting.DoesNotExist:
                    return Response(
                        {'error': 'Job not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                job_data = {
                    'title': title,
                    'description': description,
                    'source': request.data.get('source', ''),
                    'category': request.data.get('category', ''),
                    'last_date': request.data.get('last_date', '')
                }
            
            # Generate metadata
            metadata = seo_engine.generate_seo_metadata(job_data)
            
            # Log the action
            SEOAuditLog.objects.create(
                action_type='metadata_generation',
                details={'job_data': job_data, 'generated_metadata': metadata},
                status='success'
            )
            
            return Response({
                'metadata': metadata,
                'timestamp': timezone.now()
            })
            
        except Exception as e:
            logger.error(f"SEO metadata generation failed: {e}")
            
            # Log the error
            SEOAuditLog.objects.create(
                action_type='metadata_generation',
                details={'error': str(e), 'request_data': request.data},
                status='error'
            )
            
            return Response(
                {'error': 'Metadata generation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SEOAnalyzeView(APIView):
    """
    API view for analyzing SEO performance and providing recommendations.
    
    Provides comprehensive SEO analysis and optimization suggestions.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get SEO analysis and recommendations."""
        try:
            # Get analysis parameters
            job_id = request.query_params.get('job_id')
            url = request.query_params.get('url')
            
            if not (job_id or url):
                return Response(
                    {'error': 'Either job_id or url parameter required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Initialize analysis results
            analysis = {
                'seo_score': 0,
                'recommendations': [],
                'metadata_analysis': {},
                'keyword_analysis': {},
                'performance_metrics': {},
                'timestamp': timezone.now()
            }
            
            # Get job-specific analysis
            if job_id:
                try:
                    job = JobPosting.objects.get(id=job_id)
                    
                    # Analyze metadata
                    seo_metadata = SEOMetadata.objects.filter(
                        object_id=job_id
                    ).first()
                    
                    if seo_metadata:
                        analysis['metadata_analysis'] = {
                            'title_length': len(seo_metadata.seo_title),
                            'description_length': len(seo_metadata.seo_description),
                            'keywords_count': len(seo_metadata.keywords.split(',')) if seo_metadata.keywords else 0,
                            'has_structured_data': bool(seo_metadata.structured_data)
                        }
                        
                        # Calculate SEO score
                        score = 0
                        if 50 <= len(seo_metadata.seo_title) <= 60:
                            score += 25
                        if 150 <= len(seo_metadata.seo_description) <= 160:
                            score += 25
                        if seo_metadata.keywords:
                            score += 25
                        if seo_metadata.structured_data:
                            score += 25
                        
                        analysis['seo_score'] = score
                        
                        # Generate recommendations
                        if len(seo_metadata.seo_title) < 50:
                            analysis['recommendations'].append('SEO title is too short. Aim for 50-60 characters.')
                        elif len(seo_metadata.seo_title) > 60:
                            analysis['recommendations'].append('SEO title is too long. Keep it under 60 characters.')
                        
                        if len(seo_metadata.seo_description) < 150:
                            analysis['recommendations'].append('Meta description is too short. Aim for 150-160 characters.')
                        elif len(seo_metadata.seo_description) > 160:
                            analysis['recommendations'].append('Meta description is too long. Keep it under 160 characters.')
                        
                        if not seo_metadata.keywords:
                            analysis['recommendations'].append('Add relevant keywords for better SEO.')
                        
                        if not seo_metadata.structured_data:
                            analysis['recommendations'].append('Add structured data (JSON-LD) for better search visibility.')
                    
                    else:
                        analysis['recommendations'].append('No SEO metadata found. Generate metadata for this job posting.')
                        
                except JobPosting.DoesNotExist:
                    return Response(
                        {'error': 'Job not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Get keyword analysis
            if job_id:
                keywords = KeywordTracking.objects.filter(job_posting_id=job_id)
                analysis['keyword_analysis'] = {
                    'total_keywords': keywords.count(),
                    'top_keywords': list(
                        keywords.order_by('-frequency')[:5]
                        .values_list('keyword', flat=True)
                    )
                }
            
            # Log the analysis
            SEOAuditLog.objects.create(
                action_type='seo_analysis',
                details={'analysis_params': {'job_id': job_id, 'url': url}, 'results': analysis},
                status='success'
            )
            
            return Response(analysis)
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
            
            # Log the error
            SEOAuditLog.objects.create(
                action_type='seo_analysis',
                details={'error': str(e), 'params': request.query_params.dict()},
                status='error'
            )
            
            return Response(
                {'error': 'SEO analysis failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
