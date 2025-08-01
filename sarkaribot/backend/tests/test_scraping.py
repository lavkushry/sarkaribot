"""
Unit tests for Scraping functionality.
"""

import pytest
from django.test import TestCase
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta

from apps.scraping.models import ScrapeLog
from apps.scraping.tasks import scrape_government_source, process_scraping_results
from tests.factories import GovernmentSourceFactory, JobPostingFactory


@pytest.mark.django_db
class TestScrapingTasks:
    """Test scraping Celery tasks."""
    
    @patch('apps.scraping.tasks.get_scraper')
    def test_scrape_government_source_success(self, mock_get_scraper):
        """Test successful scraping task."""
        source = GovernmentSourceFactory()
        
        # Mock scraper
        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = [
            {
                'title': 'Test Job 1',
                'description': 'Test description 1',
                'url': 'https://test.gov.in/job1'
            },
            {
                'title': 'Test Job 2', 
                'description': 'Test description 2',
                'url': 'https://test.gov.in/job2'
            }
        ]
        mock_get_scraper.return_value = mock_scraper
        
        # Test scraping task
        with patch('apps.scraping.tasks.process_job_data') as mock_process:
            mock_process.return_value = (MagicMock(), True)  # job, created
            
            result = scrape_government_source(source.id)
            
            assert result['source'] == source.name
            assert result['jobs_found'] == 2
            assert result['created'] == 2
            assert result['updated'] == 0
    
    @patch('apps.scraping.tasks.get_scraper')
    def test_scrape_government_source_failure(self, mock_get_scraper):
        """Test scraping task failure and retry."""
        source = GovernmentSourceFactory()
        
        # Mock scraper to raise exception
        mock_scraper = MagicMock()
        mock_scraper.scrape.side_effect = Exception("Connection timeout")
        mock_get_scraper.return_value = mock_scraper
        
        with patch('apps.scraping.tasks.scrape_government_source.retry') as mock_retry:
            mock_retry.side_effect = Exception("Max retries exceeded")
            
            with pytest.raises(Exception):
                scrape_government_source(source.id)
            
            # Should attempt retry
            mock_retry.assert_called_once()
    
    @patch('apps.scraping.tasks.logger')
    def test_scraping_logging(self, mock_logger):
        """Test scraping task logging."""
        source = GovernmentSourceFactory()
        
        with patch('apps.scraping.tasks.get_scraper') as mock_get_scraper:
            mock_scraper = MagicMock()
            mock_scraper.scrape.return_value = []
            mock_get_scraper.return_value = mock_scraper
            
            scrape_government_source(source.id)
            
            # Should log start of scraping
            mock_logger.info.assert_called()


@pytest.mark.django_db
class TestScrapingEngine:
    """Test scraping engine functionality."""
    
    def setup_method(self):
        """Set up test data."""
        self.source = GovernmentSourceFactory(
            config_json={
                'selectors': {
                    'title': '.job-title',
                    'description': '.job-desc',
                    'date': '.job-date'
                },
                'base_url': 'https://test.gov.in'
            }
        )
    
    @patch('apps.scraping.engine.requests.get')
    def test_basic_scraping(self, mock_requests):
        """Test basic scraping functionality."""
        # Skip if scraping engine is not implemented
        try:
            from apps.scraping.engine import ScrapingEngine
        except ImportError:
            pytest.skip("Scraping engine not implemented yet")
        
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.text = """
        <div class="job-title">Test Government Job</div>
        <div class="job-desc">Job description here</div>
        <div class="job-date">2024-03-15</div>
        """
        mock_response.status_code = 200
        mock_requests.return_value = mock_response
        
        engine = ScrapingEngine(self.source)
        results = engine.scrape()
        
        assert len(results) > 0
        assert 'title' in results[0]
    
    def test_scraper_selection(self):
        """Test scraper selection based on source config."""
        try:
            from apps.scraping.engine import get_scraper
        except ImportError:
            pytest.skip("Scraper selection not implemented")
        
        # Test simple scraper selection
        simple_config = {'requires_js': False}
        scraper = get_scraper(simple_config)
        
        assert scraper is not None
        
        # Test JavaScript scraper selection
        js_config = {'requires_js': True}
        js_scraper = get_scraper(js_config)
        
        assert js_scraper is not None
    
    @patch('apps.scraping.scrapers.requests_scraper.requests.get')
    def test_requests_scraper(self, mock_get):
        """Test requests-based scraper."""
        try:
            from apps.scraping.scrapers.requests_scraper import RequestsScraper
        except ImportError:
            pytest.skip("RequestsScraper not implemented")
        
        # Mock response
        mock_response = MagicMock()
        mock_response.text = """
        <div class="job-list">
            <div class="job-item">
                <h3 class="job-title">Software Engineer</h3>
                <p class="job-desc">Description here</p>
            </div>
        </div>
        """
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        scraper = RequestsScraper(self.source.get_scraping_config())
        results = scraper.scrape('https://test.gov.in/jobs')
        
        assert isinstance(results, list)
    
    @patch('apps.scraping.scrapers.playwright_scraper.sync_playwright')
    def test_playwright_scraper(self, mock_playwright):
        """Test Playwright-based scraper."""
        try:
            from apps.scraping.scrapers.playwright_scraper import PlaywrightScraper
        except ImportError:
            pytest.skip("PlaywrightScraper not implemented")
        
        # Mock Playwright browser
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_page.content.return_value = """
        <div class="job-title">Test Job</div>
        <div class="job-desc">Test Description</div>
        """
        mock_browser.new_page.return_value = mock_page
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        
        scraper = PlaywrightScraper(self.source.get_scraping_config())
        results = scraper.scrape('https://test.gov.in/jobs')
        
        assert isinstance(results, list)


@pytest.mark.django_db
class TestJobDataProcessing:
    """Test job data processing from scraping."""
    
    def setup_method(self):
        """Set up test data."""
        self.source = GovernmentSourceFactory()
    
    def test_process_new_job_data(self):
        """Test processing new job data."""
        try:
            from apps.scraping.processors import process_job_data
        except ImportError:
            pytest.skip("Job data processor not implemented")
        
        job_data = {
            'title': 'New Government Job 2024',
            'description': 'Job description here',
            'url': 'https://test.gov.in/job/123',
            'last_date': '2024-12-31'
        }
        
        job, created = process_job_data(job_data, self.source)
        
        assert created is True
        assert job.title == 'New Government Job 2024'
        assert job.source == self.source
    
    def test_process_existing_job_data(self):
        """Test processing existing job data (update)."""
        try:
            from apps.scraping.processors import process_job_data
        except ImportError:
            pytest.skip("Job data processor not implemented")
        
        # Create existing job
        existing_job = JobPostingFactory(
            source=self.source,
            title='Existing Job',
            slug='existing-job'
        )
        
        # Updated data
        job_data = {
            'title': 'Existing Job - Updated',
            'description': 'Updated description',
            'url': existing_job.source_url,
            'slug': 'existing-job'
        }
        
        job, created = process_job_data(job_data, self.source)
        
        assert created is False
        assert job.id == existing_job.id
        assert 'Updated' in job.title
    
    def test_duplicate_detection(self):
        """Test duplicate job detection."""
        try:
            from apps.scraping.processors import is_duplicate_job
        except ImportError:
            pytest.skip("Duplicate detection not implemented")
        
        # Create existing job
        existing_job = JobPostingFactory(
            title='Software Engineer Position',
            source=self.source
        )
        
        # Test similar job data
        similar_data = {
            'title': 'Software Engineer Position',
            'source_url': existing_job.source_url
        }
        
        is_duplicate = is_duplicate_job(similar_data, self.source)
        assert is_duplicate is True
        
        # Test different job data
        different_data = {
            'title': 'Data Analyst Position', 
            'source_url': 'https://different-url.gov.in'
        }
        
        is_duplicate = is_duplicate_job(different_data, self.source)
        assert is_duplicate is False


@pytest.mark.integration
class TestScrapingIntegration(TestCase):
    """Integration tests for complete scraping workflow."""
    
    def setUp(self):
        """Set up test data."""
        self.source = GovernmentSourceFactory(
            name='TEST_INTEGRATION',
            base_url='https://test-integration.gov.in',
            config_json={
                'selectors': {
                    'title': '.job-title',
                    'description': '.job-description',
                    'link': '.job-link'
                },
                'pagination': {
                    'next_page': '.next-page',
                    'max_pages': 2
                }
            }
        )
    
    @patch('apps.scraping.tasks.get_scraper')
    def test_complete_scraping_workflow(self, mock_get_scraper):
        """Test complete scraping workflow from task to job creation."""
        # Mock scraper return data
        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = [
            {
                'title': 'Integration Test Job 1',
                'description': 'Test job description 1',
                'url': 'https://test.gov.in/job1',
                'last_date': '2024-12-31'
            },
            {
                'title': 'Integration Test Job 2',
                'description': 'Test job description 2',
                'url': 'https://test.gov.in/job2',
                'last_date': '2025-01-15'
            }
        ]
        mock_get_scraper.return_value = mock_scraper
        
        # Run scraping task
        initial_job_count = self.source.job_postings.count()
        
        with patch('apps.scraping.tasks.process_job_data') as mock_process:
            # Mock job creation
            mock_job1 = MagicMock()
            mock_job2 = MagicMock()
            mock_process.side_effect = [
                (mock_job1, True),  # First job created
                (mock_job2, True)   # Second job created
            ]
            
            result = scrape_government_source(self.source.id)
            
            assert result['jobs_found'] == 2
            assert result['created'] == 2
            assert result['updated'] == 0
    
    def test_error_handling_and_logging(self):
        """Test error handling and logging in scraping."""
        with patch('apps.scraping.tasks.get_scraper') as mock_get_scraper:
            # Mock scraper that raises exception
            mock_scraper = MagicMock()
            mock_scraper.scrape.side_effect = ConnectionError("Network error")
            mock_get_scraper.return_value = mock_scraper
            
            with patch('apps.scraping.tasks.logger') as mock_logger:
                with pytest.raises(Exception):
                    scrape_government_source(self.source.id)
                
                # Should log the error
                mock_logger.error.assert_called()
    
    def test_scraping_frequency_respect(self):
        """Test that scraping respects frequency settings."""
        from django.utils import timezone
        
        # Set recent scrape time
        self.source.last_scraped = timezone.now() - timedelta(hours=1)
        self.source.scrape_frequency = 24  # 24 hours
        self.source.save()
        
        # Should not be due for scraping
        assert not self.source.is_due_for_scraping()
        
        # Set old scrape time
        self.source.last_scraped = timezone.now() - timedelta(hours=25)
        self.source.save()
        
        # Should be due for scraping
        assert self.source.is_due_for_scraping()
    
    @patch('apps.scraping.tasks.scrape_government_source.delay')
    def test_scheduled_scraping_trigger(self, mock_delay):
        """Test triggering scheduled scraping for due sources."""
        try:
            from apps.scraping.tasks import schedule_due_scraping
        except ImportError:
            pytest.skip("Scheduled scraping not implemented")
        
        # Create sources with different scrape times
        due_source = GovernmentSourceFactory(
            last_scraped=timezone.now() - timedelta(hours=25),
            scrape_frequency=24,
            status='active'
        )
        
        not_due_source = GovernmentSourceFactory(
            last_scraped=timezone.now() - timedelta(hours=1),
            scrape_frequency=24,
            status='active'
        )
        
        # Run scheduling task
        schedule_due_scraping()
        
        # Should schedule scraping for due source only
        mock_delay.assert_called_once_with(due_source.id)