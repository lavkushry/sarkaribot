"""
Tests for SEO model database indexes and performance.
"""

import django
from django.test import TestCase
from django.db import connection
from django.db.utils import ProgrammingError

from apps.seo.models import SitemapEntry, SEOMetadata, KeywordTracking, SEOAuditLog


class SEOIndexTestCase(TestCase):
    """Test that all expected database indexes exist for SEO models."""
    
    def get_table_indexes(self, table_name):
        """Get all indexes for a given table."""
        with connection.cursor() as cursor:
            # Get indexes for PostgreSQL
            cursor.execute("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = %s
                ORDER BY indexname;
            """, [table_name])
            return cursor.fetchall()
    
    def test_sitemap_entry_indexes(self):
        """Test that SitemapEntry has all required indexes."""
        indexes = self.get_table_indexes('seo_sitemapentry')
        index_names = [idx[0] for idx in indexes]
        
        # Check for basic indexes
        self.assertTrue(any('is_acti' in name for name in index_names), 
                       "Missing is_active index")
        self.assertTrue(any('change' in name for name in index_names), 
                       "Missing change_frequency index")
        self.assertTrue(any('last_mo' in name for name in index_names), 
                       "Missing last_modified index")
        
        # Check for advanced indexes
        self.assertTrue(any('generation' in name for name in index_names), 
                       "Missing sitemap generation composite index")
    
    def test_seo_metadata_indexes(self):
        """Test that SEOMetadata has all required indexes."""
        indexes = self.get_table_indexes('seo_seometadata')
        index_names = [idx[0] for idx in indexes]
        
        # Check for basic indexes
        self.assertTrue(any('content' in name and 'fdc0b8' in name for name in index_names), 
                       "Missing content_type+content_id index")
        self.assertTrue(any('url_pat' in name for name in index_names), 
                       "Missing url_path index")
        
        # Check for advanced indexes
        self.assertTrue(any('title' in name for name in index_names), 
                       "Missing title index")
        self.assertTrue(any('canonical' in name for name in index_names), 
                       "Missing canonical_url index")
    
    def test_keyword_tracking_indexes(self):
        """Test that KeywordTracking has all required indexes."""
        indexes = self.get_table_indexes('seo_keywordtracking')
        index_names = [idx[0] for idx in indexes]
        
        # Check for basic indexes
        self.assertTrue(any('keyword' in name for name in index_names), 
                       "Missing keyword index")
        self.assertTrue(any('current' in name for name in index_names), 
                       "Missing current_position index")
        
        # Check for advanced indexes
        self.assertTrue(any('target_url' in name for name in index_names), 
                       "Missing target_url index")
        self.assertTrue(any('volume' in name for name in index_names), 
                       "Missing search_volume+difficulty_score index")
    
    def test_seo_audit_log_indexes(self):
        """Test that SEOAuditLog has all required indexes."""
        indexes = self.get_table_indexes('seo_seoauditlog')
        index_names = [idx[0] for idx in indexes]
        
        # Check for basic indexes
        self.assertTrue(any('audit_t' in name for name in index_names), 
                       "Missing audit_type index")
        self.assertTrue(any('status' in name for name in index_names), 
                       "Missing status index")
        
        # Check for advanced indexes
        self.assertTrue(any('triggered' in name for name in index_names), 
                       "Missing triggered_by index")
        self.assertTrue(any('performance' in name for name in index_names), 
                       "Missing performance analysis index")
    
    def test_partial_indexes_exist(self):
        """Test that partial indexes are created correctly."""
        with connection.cursor() as cursor:
            # Check for partial indexes (PostgreSQL specific)
            cursor.execute("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE indexdef LIKE '%WHERE%'
                AND tablename LIKE 'seo_%'
                ORDER BY indexname;
            """)
            partial_indexes = cursor.fetchall()
            
            # Should have at least some partial indexes
            self.assertGreater(len(partial_indexes), 0, 
                             "No partial indexes found")
            
            # Check specific partial indexes
            partial_names = [idx[0] for idx in partial_indexes]
            self.assertTrue(any('active' in name or 'target' in name for name in partial_names),
                          "Missing expected partial indexes")


class SEOModelTestCase(TestCase):
    """Test SEO model functionality with new indexes."""
    
    def setUp(self):
        """Set up test data."""
        self.sitemap_entry = SitemapEntry.objects.create(
            url='https://example.com/test',
            priority=0.8,
            change_frequency='daily'
        )
        
        self.seo_metadata = SEOMetadata.objects.create(
            content_type='job_posting',
            content_id=1,
            url_path='/test-job',
            title='Test Job 2025',
            description='Test job description'
        )
        
        self.keyword = KeywordTracking.objects.create(
            keyword='test keyword',
            target_url='https://example.com/test',
            current_position=10,
            search_volume=1000
        )
        
        self.audit_log = SEOAuditLog.objects.create(
            audit_type='metadata_generation',
            status='success'
        )
    
    def test_model_creation_with_indexes(self):
        """Test that models can be created and queried efficiently."""
        # Test SitemapEntry queries
        active_entries = SitemapEntry.objects.filter(is_active=True).order_by('-priority')
        self.assertEqual(len(active_entries), 1)
        
        # Test SEOMetadata queries
        job_metadata = SEOMetadata.objects.filter(content_type='job_posting')
        self.assertEqual(len(job_metadata), 1)
        
        # Test KeywordTracking queries
        target_keywords = KeywordTracking.objects.filter(is_target_keyword=True)
        self.assertEqual(len(target_keywords), 1)
        
        # Test SEOAuditLog queries
        successful_audits = SEOAuditLog.objects.filter(status='success')
        self.assertEqual(len(successful_audits), 1)
    
    def test_index_query_performance(self):
        """Test that indexed fields can be queried efficiently."""
        with connection.cursor() as cursor:
            # Test title search (should use index)
            cursor.execute("""
                EXPLAIN (FORMAT JSON) 
                SELECT * FROM seo_seometadata WHERE title = %s
            """, ['Test Job 2025'])
            
            result = cursor.fetchone()[0]
            # Should mention index usage in the plan
            plan_text = str(result)
            self.assertIn('Index', plan_text, "Query should use index")