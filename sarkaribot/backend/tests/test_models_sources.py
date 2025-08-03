"""
Unit tests for Sources app models.
"""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from apps.sources.models import GovernmentSource
from tests.factories import GovernmentSourceFactory


@pytest.mark.django_db
class TestGovernmentSource:
    """Test cases for GovernmentSource model."""
    
    def test_create_government_source(self):
        """Test creating a government source."""
        source = GovernmentSourceFactory(
            name='SSC',
            display_name='Staff Selection Commission',
            base_url='https://ssc.nic.in'
        )
        
        assert source.name == 'SSC'
        assert source.display_name == 'Staff Selection Commission'
        assert source.base_url == 'https://ssc.nic.in'
        assert source.status == 'active'
    
    def test_string_representation(self):
        """Test string representation of government source."""
        source = GovernmentSourceFactory(
            name='UPSC',
            display_name='Union Public Service Commission'
        )
        
        assert str(source) == 'Union Public Service Commission (UPSC)'
    
    def test_unique_name_constraint(self):
        """Test that source names must be unique."""
        GovernmentSourceFactory(name='SSC')
        
        with pytest.raises(IntegrityError):
            GovernmentSourceFactory(name='SSC')
    
    def test_url_validation(self):
        """Test URL field validation."""
        # Valid URL
        source = GovernmentSourceFactory(base_url='https://example.gov.in')
        assert source.base_url == 'https://example.gov.in'
        
        # Invalid URL should raise validation error
        with pytest.raises(ValidationError):
            source = GovernmentSourceFactory(base_url='invalid-url')
            source.full_clean()
    
    def test_status_choices(self):
        """Test valid status choices."""
        valid_statuses = ['active', 'paused', 'error', 'maintenance']
        
        for status in valid_statuses:
            source = GovernmentSourceFactory(status=status)
            assert source.status == status
    
    def test_scrape_frequency_validation(self):
        """Test scrape frequency validation."""
        # Valid frequencies
        for freq in [6, 12, 24, 48]:
            source = GovernmentSourceFactory(scrape_frequency=freq)
            assert source.scrape_frequency == freq
        
        # Test minimum frequency constraint if it exists
        source = GovernmentSourceFactory(scrape_frequency=1)
        assert source.scrape_frequency == 1
    
    def test_config_json_field(self):
        """Test JSON configuration field."""
        config = {
            'selectors': {
                'title': '.job-title',
                'description': '.job-desc'
            },
            'pagination': {
                'next_page': '.next',
                'max_pages': 5
            }
        }
        
        source = GovernmentSourceFactory(config_json=config)
        
        assert source.config_json == config
        assert source.config_json['selectors']['title'] == '.job-title'
    
    def test_priority_field(self):
        """Test priority field."""
        high_priority = GovernmentSourceFactory(priority=1)
        low_priority = GovernmentSourceFactory(priority=5)
        
        assert high_priority.priority == 1
        assert low_priority.priority == 5
        
        # Test ordering by priority
        sources = GovernmentSource.objects.order_by('priority')
        assert sources.first().priority <= sources.last().priority


@pytest.mark.django_db
class TestGovernmentSourceMethods:
    """Test custom methods on GovernmentSource model."""
    
    def test_is_due_for_scraping_new_source(self):
        """Test is_due_for_scraping for new source."""
        source = GovernmentSourceFactory(last_scraped=None, status='active')
        
        assert source.is_due_for_scraping() is True
    
    def test_is_due_for_scraping_inactive_source(self):
        """Test is_due_for_scraping for inactive source."""
        source = GovernmentSourceFactory(active=False)
        
        assert source.is_due_for_scraping() is False
    
    def test_is_due_for_scraping_error_status(self):
        """Test is_due_for_scraping for source with error status."""
        source = GovernmentSourceFactory(status='error')
        
        assert source.is_due_for_scraping() is False
    
    def test_is_due_for_scraping_recent_scrape(self):
        """Test is_due_for_scraping for recently scraped source."""
        # Source scraped 1 hour ago with 24-hour frequency
        recent_time = timezone.now() - timedelta(hours=1)
        source = GovernmentSourceFactory(
            last_scraped=recent_time,
            scrape_frequency=24,
            status='active'
        )
        
        assert source.is_due_for_scraping() is False
    
    def test_is_due_for_scraping_old_scrape(self):
        """Test is_due_for_scraping for source due for scraping."""
        # Source scraped 25 hours ago with 24-hour frequency
        old_time = timezone.now() - timedelta(hours=25)
        source = GovernmentSourceFactory(
            last_scraped=old_time,
            scrape_frequency=24,
            status='active'
        )
        
        assert source.is_due_for_scraping() is True
    
    @patch('apps.sources.models.logger')
    def test_mark_scrape_started(self, mock_logger):
        """Test marking scrape as started."""
        source = GovernmentSourceFactory(status='paused', last_error='Previous error')
        
        source.mark_scrape_started()
        
        source.refresh_from_db()
        assert source.status == 'active'
        assert source.last_error == ''
        mock_logger.info.assert_called_once()
    
    @patch('apps.sources.models.logger')
    def test_mark_scrape_completed(self, mock_logger):
        """Test marking scrape as completed."""
        source = GovernmentSourceFactory(
            total_jobs_found=50,
            last_error='Some error'
        )
        initial_jobs_count = source.total_jobs_found
        
        source.mark_scrape_completed(jobs_found=10)
        
        source.refresh_from_db()
        assert source.status == 'active'
        assert source.last_error == ''
        assert source.total_jobs_found == initial_jobs_count + 10
        assert source.last_scraped is not None
        mock_logger.info.assert_called_once()
    
    @patch('apps.sources.models.logger')
    def test_mark_scrape_error(self, mock_logger):
        """Test marking scrape error."""
        source = GovernmentSourceFactory(status='active')
        error_message = 'Connection timeout'
        
        source.mark_scrape_error(error_message)
        
        source.refresh_from_db()
        assert source.status == 'error'
        assert source.last_error == error_message
        mock_logger.error.assert_called_once()
    
    def test_get_scraping_config_default(self):
        """Test getting default scraping configuration."""
        source = GovernmentSourceFactory(config_json=None)
        
        config = source.get_scraping_config()
        
        assert 'selectors' in config
        assert 'pagination' in config
        assert config['request_delay'] == 2
        assert config['max_pages'] == 5
        assert config['timeout'] == 30
    
    def test_get_scraping_config_custom(self):
        """Test getting custom scraping configuration."""
        custom_config = {
            'request_delay': 5,
            'max_pages': 10,
            'selectors': {
                'title': '.custom-title'
            }
        }
        source = GovernmentSourceFactory(config_json=custom_config)
        
        config = source.get_scraping_config()
        
        assert config['request_delay'] == 5
        assert config['max_pages'] == 10
        assert config['selectors']['title'] == '.custom-title'
        # Should still have defaults for missing keys
        assert config['timeout'] == 30
    
    @patch('apps.jobs.models.JobPosting.objects.filter')
    def test_get_jobs_count_last_30_days(self, mock_filter):
        """Test getting jobs count for last 30 days."""
        source = GovernmentSourceFactory()
        mock_filter.return_value.count.return_value = 25
        
        count = source.get_jobs_count_last_30_days()
        
        assert count == 25
        mock_filter.assert_called_once()
    
    def test_get_success_rate_last_30_days_no_stats(self):
        """Test success rate calculation with no statistics."""
        source = GovernmentSourceFactory()
        
        # Assuming statistics is a related model that doesn't exist yet
        success_rate = source.get_success_rate_last_30_days()
        
        assert success_rate == 0.0


@pytest.mark.integration
class TestGovernmentSourceIntegration(TestCase):
    """Integration tests for government source functionality."""
    
    def test_source_with_job_postings(self):
        """Test source with related job postings."""
        from tests.factories import JobPostingFactory
        
        source = GovernmentSourceFactory()
        
        # Create jobs for this source
        jobs = [
            JobPostingFactory(source=source, title=f'Job {i}')
            for i in range(5)
        ]
        
        assert source.job_postings.count() == 5
        assert all(job.source == source for job in jobs)
    
    def test_source_deletion_cascade(self):
        """Test that deleting source cascades to job postings."""
        from tests.factories import JobPostingFactory
        from apps.jobs.models import JobPosting
        
        source = GovernmentSourceFactory()
        job = JobPostingFactory(source=source)
        job_id = job.id
        
        source.delete()
        
        # Job should be deleted due to cascade
        with pytest.raises(JobPosting.DoesNotExist):
            JobPosting.objects.get(id=job_id)
    
    def test_bulk_source_operations(self):
        """Test bulk operations on sources."""
        sources = GovernmentSourceFactory.create_batch(5)
        
        assert GovernmentSource.objects.count() == 5
        
        # Bulk update status
        GovernmentSource.objects.all().update(status='maintenance')
        
        for source in GovernmentSource.objects.all():
            assert source.status == 'maintenance'
    
    def test_source_filtering_and_ordering(self):
        """Test complex filtering and ordering of sources."""
        # Create sources with different priorities and statuses
        high_priority_active = GovernmentSourceFactory(
            priority=1, 
            status='active',
            name='HIGH_PRIORITY'
        )
        low_priority_active = GovernmentSourceFactory(
            priority=5,
            status='active', 
            name='LOW_PRIORITY'
        )
        high_priority_paused = GovernmentSourceFactory(
            priority=1,
            status='paused',
            name='HIGH_PAUSED'
        )
        
        # Get active sources ordered by priority
        active_sources = GovernmentSource.objects.filter(
            status='active'
        ).order_by('priority', 'name')
        
        assert list(active_sources) == [high_priority_active, low_priority_active]
        
        # Get all sources by priority regardless of status
        all_by_priority = GovernmentSource.objects.order_by('priority', 'name')
        
        assert all_by_priority.first() in [high_priority_active, high_priority_paused]
    
    def test_source_config_validation(self):
        """Test validation of source configuration."""
        # Valid configuration
        valid_config = {
            'selectors': {
                'title': '.job-title',
                'description': '.job-desc',
                'date': '.job-date'
            },
            'pagination': {
                'next_page': '.next-page',
                'max_pages': 3
            },
            'request_delay': 2
        }
        
        source = GovernmentSourceFactory(config_json=valid_config)
        config = source.get_scraping_config()
        
        assert config['selectors']['title'] == '.job-title'
        assert config['pagination']['max_pages'] == 3
        
        # Invalid configuration (missing required fields) should still work
        # due to defaults being provided
        incomplete_config = {
            'selectors': {
                'title': '.title-only'
            }
        }
        
        source2 = GovernmentSourceFactory(config_json=incomplete_config)
        config2 = source2.get_scraping_config()
        
        assert config2['selectors']['title'] == '.title-only'
        assert 'pagination' in config2  # Should have default