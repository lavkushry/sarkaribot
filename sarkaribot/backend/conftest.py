"""
Global test configuration and fixtures for SarkariBot tests.
"""

import pytest
import tempfile
import shutil
from django.conf import settings
from django.test import TestCase
from django.core.management import call_command
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock


@pytest.fixture(scope='session')
def django_db_setup():
    """
    Setup test database for the entire test session.
    """
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


@pytest.fixture
def api_client():
    """
    DRF API client for testing API endpoints.
    """
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """
    API client with authenticated user.
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def user(django_user_model):
    """
    Create a test user.
    """
    return django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(django_user_model):
    """
    Create a test admin user.
    """
    return django_user_model.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def temp_media_root():
    """
    Create temporary media directory for tests.
    """
    temp_dir = tempfile.mkdtemp()
    with patch.object(settings, 'MEDIA_ROOT', temp_dir):
        yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_celery_task():
    """
    Mock Celery task execution.
    """
    with patch('celery.current_app.send_task') as mock_task:
        mock_task.return_value = MagicMock(id='test-task-id')
        yield mock_task


@pytest.fixture
def mock_scraper():
    """
    Mock scraper for testing scraping functionality.
    """
    with patch('apps.scraping.engine.ScrapingEngine') as mock_scraper:
        mock_instance = MagicMock()
        mock_scraper.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_nlp_processor():
    """
    Mock NLP processor for SEO testing.
    """
    with patch('apps.seo.processors.NLPProcessor') as mock_nlp:
        mock_instance = MagicMock()
        mock_nlp.return_value = mock_instance
        yield mock_instance


class BaseTestCase(TestCase):
    """
    Base test case with common functionality.
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Load test fixtures if needed
        call_command('loaddata', 'test_fixtures.json', verbosity=0)
    
    def setUp(self):
        """
        Set up test data before each test.
        """
        super().setUp()
        self.client = APIClient()
        
    def tearDown(self):
        """
        Clean up after each test.
        """
        super().tearDown()
        # Clear any cached data
        from django.core.cache import cache
        cache.clear()


class IntegrationTestCase(BaseTestCase):
    """
    Base class for integration tests with additional setup.
    """
    
    def setUp(self):
        super().setUp()
        # Additional setup for integration tests
        self.setup_test_data()
    
    def setup_test_data(self):
        """
        Create test data for integration tests.
        """
        # This will be implemented by specific test classes
        pass


# Test data utilities
def create_test_job_data(**kwargs):
    """
    Create test job posting data with defaults.
    """
    default_data = {
        'title': 'Test Government Job 2024',
        'description': 'Test job description with requirements and details.',
        'eligibility': 'Graduate degree required',
        'last_date': '2024-12-31',
        'application_link': 'https://example.gov.in/apply',
        'source_url': 'https://example.gov.in/jobs/test-job',
        'status': 'announced',
        'vacancy_count': 100,
        'application_fee': 500,
        'age_limit': '18-30 years',
        'salary': '25000-50000',
    }
    default_data.update(kwargs)
    return default_data


def create_test_source_data(**kwargs):
    """
    Create test government source data with defaults.
    """
    default_data = {
        'name': 'TEST_DEPT',
        'display_name': 'Test Government Department',
        'description': 'Test department for unit testing',
        'base_url': 'https://test-dept.gov.in',
        'scrape_frequency': 24,
        'status': 'active',
        'config_json': {
            'selectors': {
                'title': '.job-title',
                'description': '.job-description',
                'last_date': '.last-date'
            },
            'pagination': {
                'next_page': '.next-page',
                'max_pages': 3
            }
        }
    }
    default_data.update(kwargs)
    return default_data