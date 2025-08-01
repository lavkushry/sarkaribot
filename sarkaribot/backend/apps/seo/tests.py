"""
Tests for SEO automation engine.

This module contains comprehensive tests for the NLP-powered SEO
automation system including fallback mechanisms.
"""

import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.conf import settings
from django.utils import timezone
from datetime import datetime

from .engine import NLPSEOEngine, SPACY_AVAILABLE
from .tasks import generate_seo_metadata


class TestNLPSEOEngine(TestCase):
    """Test cases for the NLP SEO automation engine."""
    
    def setUp(self):
        """Set up test data."""
        self.engine = NLPSEOEngine()
        
        # Sample job data for testing
        self.complete_job_data = {
            'id': 1,
            'title': 'Railway Recruitment Board Junior Engineer 2024',
            'description': 'Apply for Railway JE posts in various departments. Total 5000+ vacancies available. Engineering graduates can apply with attractive salary package.',
            'department': 'Ministry of Railways',
            'qualification': 'Engineering Graduate (B.E/B.Tech)',
            'notification_date': timezone.now(),
            'application_end_date': timezone.now(),
            'location': 'All India',
            'source_url': 'https://rrbcdg.gov.in',
            'category': {'name': 'Engineering Jobs', 'slug': 'engineering'},
            'source': {'base_url': 'https://rrbcdg.gov.in'}
        }
        
        self.minimal_job_data = {
            'title': 'Staff Selection Commission Clerk'
        }
    
    def test_engine_initialization(self):
        """Test that the engine initializes correctly."""
        self.assertIsInstance(self.engine, NLPSEOEngine)
        self.assertEqual(self.engine.seo_title_max_length, 60)
        self.assertEqual(self.engine.seo_description_max_length, 160)
        self.assertEqual(self.engine.seo_keywords_max_count, 7)
    
    def test_generate_seo_metadata_complete_data(self):
        """Test SEO metadata generation with complete job data."""
        metadata = self.engine.generate_seo_metadata(self.complete_job_data)
        
        # Basic structure validation
        self.assertIsInstance(metadata, dict)
        self.assertIn('seo_title', metadata)
        self.assertIn('seo_description', metadata)
        self.assertIn('keywords', metadata)
        self.assertIn('structured_data', metadata)
        self.assertIn('slug', metadata)
        self.assertIn('canonical_url', metadata)
        self.assertIn('quality_score', metadata)
        
        # Content validation
        self.assertTrue(len(metadata['seo_title']) > 0)
        self.assertTrue(len(metadata['seo_title']) <= 60)
        
        self.assertTrue(len(metadata['seo_description']) > 0)
        self.assertTrue(len(metadata['seo_description']) <= 160)
        
        self.assertIsInstance(metadata['keywords'], list)
        self.assertTrue(len(metadata['keywords']) > 0)
        self.assertTrue(len(metadata['keywords']) <= 7)
        
        # Quality score validation
        self.assertIsInstance(metadata['quality_score'], (int, float))
        self.assertTrue(0 <= metadata['quality_score'] <= 100)
        
        # Structured data validation
        structured_data = metadata['structured_data']
        self.assertEqual(structured_data['@type'], 'JobPosting')
        self.assertEqual(structured_data['title'], self.complete_job_data['title'])
    
    def test_generate_seo_metadata_minimal_data(self):
        """Test SEO metadata generation with minimal job data."""
        metadata = self.engine.generate_seo_metadata(self.minimal_job_data)
        
        # Should still generate valid metadata
        self.assertIsInstance(metadata, dict)
        self.assertTrue(len(metadata['seo_title']) > 0)
        self.assertTrue(len(metadata['seo_description']) > 0)
        self.assertIsInstance(metadata['keywords'], list)
        self.assertTrue(metadata['quality_score'] > 0)
    
    def test_generate_seo_metadata_invalid_data(self):
        """Test SEO metadata generation with invalid data."""
        # Test with empty data
        metadata = self.engine.generate_seo_metadata({})
        self.assertEqual(metadata['generation_method'], 'fallback')
        
        # Test with None title
        metadata = self.engine.generate_seo_metadata({'title': None})
        self.assertEqual(metadata['generation_method'], 'fallback')
    
    def test_keyword_extraction(self):
        """Test keyword extraction functionality."""
        keywords = self.engine._extract_keywords(self.complete_job_data)
        
        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) > 0)
        self.assertTrue(len(keywords) <= 7)
        
        # Check for expected keywords
        keywords_text = ' '.join(keywords).lower()
        self.assertIn('railway', keywords_text)
        self.assertIn('engineer', keywords_text)
    
    def test_keyword_extraction_fallback(self):
        """Test fallback keyword extraction method."""
        keywords = self.engine._extract_keywords_fallback(self.complete_job_data)
        
        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) > 0)
        self.assertTrue(len(keywords) <= 7)
        
        # Check for government-specific keywords
        keywords_text = ' '.join(keywords).lower()
        expected_govt_keywords = ['railway', 'recruitment', 'engineer', 'government']
        found_govt_keywords = [kw for kw in expected_govt_keywords if kw in keywords_text]
        self.assertTrue(len(found_govt_keywords) > 0)
    
    def test_seo_title_generation(self):
        """Test SEO title generation."""
        title = self.engine._generate_seo_title(self.complete_job_data)
        
        self.assertIsInstance(title, str)
        self.assertTrue(len(title) > 0)
        self.assertTrue(len(title) <= 60)
        
        # Should include the current year
        current_year = str(datetime.now().year)
        self.assertIn(current_year, title)
        
        # Should include the original title
        self.assertIn('Railway', title)
    
    def test_seo_description_generation(self):
        """Test SEO description generation."""
        description = self.engine._generate_seo_description(self.complete_job_data)
        
        self.assertIsInstance(description, str)
        self.assertTrue(len(description) > 0)
        self.assertTrue(len(description) <= 160)
        
        # Should include action words
        self.assertIn('Apply', description)
        
        # Should include qualification if provided
        if self.complete_job_data.get('qualification'):
            self.assertIn('Eligibility', description)
    
    def test_structured_data_generation(self):
        """Test structured data generation."""
        structured_data = self.engine._generate_job_schema(self.complete_job_data)
        
        self.assertIsInstance(structured_data, dict)
        self.assertEqual(structured_data['@context'], 'https://schema.org/')
        self.assertEqual(structured_data['@type'], 'JobPosting')
        self.assertEqual(structured_data['title'], self.complete_job_data['title'])
        
        # Check required schema.org fields
        self.assertIn('hiringOrganization', structured_data)
        self.assertIn('jobLocation', structured_data)
        self.assertEqual(structured_data['employmentType'], 'FULL_TIME')
    
    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        keywords = ['railway', 'engineer', 'job', 'recruitment']
        score = self.engine._calculate_quality_score(self.complete_job_data, keywords)
        
        self.assertIsInstance(score, (int, float))
        self.assertTrue(0 <= score <= 100)
        
        # Complete data should have high score
        self.assertTrue(score > 50)
    
    def test_slug_generation(self):
        """Test URL slug generation."""
        slug = self.engine._generate_slug(self.complete_job_data['title'])
        
        self.assertIsInstance(slug, str)
        self.assertTrue(len(slug) > 0)
        
        # Should be URL-friendly
        self.assertNotIn(' ', slug)
        self.assertNotIn('_', slug)
        self.assertTrue(slug.islower() or '-' in slug)
    
    def test_fallback_metadata_generation(self):
        """Test fallback metadata generation."""
        metadata = self.engine._generate_fallback_metadata(self.complete_job_data)
        
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata['generation_method'], 'fallback')
        self.assertEqual(metadata['quality_score'], 50.0)
        
        # Should still have all required fields
        required_fields = ['seo_title', 'seo_description', 'keywords', 'structured_data', 'slug']
        for field in required_fields:
            self.assertIn(field, metadata)
    
    @patch('apps.seo.engine.SPACY_AVAILABLE', False)
    def test_engine_without_spacy(self):
        """Test engine functionality when spaCy is not available."""
        engine = NLPSEOEngine()
        self.assertIsNone(engine.nlp)
        
        metadata = engine.generate_seo_metadata(self.complete_job_data)
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata['generation_method'], 'fallback')
    
    def test_filter_keywords(self):
        """Test keyword filtering and ranking."""
        test_keywords = ['railway', 'job', 'engineer', 'recruitment', 'government', 'test']
        filtered = self.engine._filter_keywords(test_keywords, self.complete_job_data)
        
        self.assertIsInstance(filtered, list)
        self.assertTrue(len(filtered) <= 7)
        
        # Government-related keywords should be prioritized
        if 'railway' in filtered and 'test' in filtered:
            railway_index = filtered.index('railway')
            test_index = filtered.index('test')
            self.assertTrue(railway_index < test_index)
    
    def test_error_handling(self):
        """Test error handling in metadata generation."""
        # Test with None input
        with self.assertRaises(TypeError):
            self.engine.generate_seo_metadata(None)
        
        # Test with missing title
        metadata = self.engine.generate_seo_metadata({'description': 'Test'})
        self.assertEqual(metadata['generation_method'], 'fallback')


class TestSEOTasks(TestCase):
    """Test cases for SEO Celery tasks."""
    
    @patch('apps.seo.tasks.JobPosting')
    @patch('apps.seo.tasks.seo_engine')
    def test_generate_seo_metadata_task(self, mock_engine, mock_job_model):
        """Test the SEO metadata generation task."""
        # Mock job posting
        mock_job = MagicMock()
        mock_job.id = 1
        mock_job.title = 'Test Job'
        mock_job.description = 'Test Description'
        mock_job.seo_title = None
        mock_job.seo_description = None
        mock_job.keywords = None
        
        mock_job_model.objects.get.return_value = mock_job
        
        # Mock SEO engine
        mock_metadata = {
            'seo_title': 'Test Job 2024',
            'seo_description': 'Apply for Test Job',
            'keywords': ['test', 'job'],
            'structured_data': {'@type': 'JobPosting'}
        }
        mock_engine.generate_seo_metadata.return_value = mock_metadata
        
        # Test the task
        result = generate_seo_metadata(1)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'updated')
        
        # Verify the job was updated
        mock_job.save.assert_called_once()
    
    def test_seo_engine_integration(self):
        """Test integration between engine and tasks."""
        # This would be an integration test with actual database
        # For now, just verify the engine can be imported and initialized
        from .engine import seo_engine
        self.assertIsInstance(seo_engine, NLPSEOEngine)


class TestSEOEnginePerformance(TestCase):
    """Performance tests for SEO engine."""
    
    def test_bulk_metadata_generation(self):
        """Test performance with multiple job postings."""
        engine = NLPSEOEngine()
        
        # Generate test data
        test_jobs = []
        for i in range(10):
            job_data = {
                'title': f'Government Job {i} 2024',
                'description': f'This is test job number {i} for performance testing.',
                'department': f'Department {i}'
            }
            test_jobs.append(job_data)
        
        # Time the generation
        import time
        start_time = time.time()
        
        results = []
        for job_data in test_jobs:
            metadata = engine.generate_seo_metadata(job_data)
            results.append(metadata)
        
        end_time = time.time()
        
        # Verify all jobs were processed
        self.assertEqual(len(results), 10)
        
        # Performance should be reasonable (less than 5 seconds for 10 jobs)
        processing_time = end_time - start_time
        self.assertTrue(processing_time < 5.0, f"Processing took {processing_time:.2f} seconds")
        
        # All results should be valid
        for metadata in results:
            self.assertIsInstance(metadata, dict)
            self.assertTrue(len(metadata['seo_title']) > 0)
            self.assertTrue(len(metadata['keywords']) > 0)


if __name__ == '__main__':
    unittest.main()