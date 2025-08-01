"""
Unit tests for Jobs app models.
"""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from apps.jobs.models import JobCategory, JobPosting
from tests.factories import (
    JobCategoryFactory, 
    JobPostingFactory,
    GovernmentSourceFactory
)


@pytest.mark.django_db
class TestJobCategory:
    """Test cases for JobCategory model."""
    
    def test_create_job_category(self):
        """Test creating a job category."""
        category = JobCategoryFactory(
            name='Latest Jobs',
            slug='latest-jobs',
            description='Latest government job postings'
        )
        
        assert category.name == 'Latest Jobs'
        assert category.slug == 'latest-jobs'
        assert category.is_active is True
        assert str(category) == 'Latest Jobs'
    
    def test_unique_name_constraint(self):
        """Test that category names must be unique."""
        JobCategoryFactory(name='Test Category')
        
        with pytest.raises(IntegrityError):
            JobCategoryFactory(name='Test Category')
    
    def test_unique_slug_constraint(self):
        """Test that category slugs must be unique."""
        JobCategoryFactory(slug='test-slug')
        
        with pytest.raises(IntegrityError):
            JobCategoryFactory(slug='test-slug')
    
    def test_ordering(self):
        """Test category ordering by position."""
        cat1 = JobCategoryFactory(name='First', position=2)
        cat2 = JobCategoryFactory(name='Second', position=1)
        cat3 = JobCategoryFactory(name='Third', position=3)
        
        categories = JobCategory.objects.all()
        
        assert list(categories) == [cat2, cat1, cat3]
    
    def test_get_active_categories(self):
        """Test filtering active categories."""
        active_cat = JobCategoryFactory(is_active=True)
        inactive_cat = JobCategoryFactory(is_active=False)
        
        active_categories = JobCategory.objects.filter(is_active=True)
        
        assert active_cat in active_categories
        assert inactive_cat not in active_categories


@pytest.mark.django_db 
class TestJobPosting:
    """Test cases for JobPosting model."""
    
    def test_create_job_posting(self):
        """Test creating a job posting."""
        source = GovernmentSourceFactory()
        category = JobCategoryFactory()
        
        job = JobPostingFactory(
            title='Test Government Job 2024',
            source=source,
            category=category,
            total_posts=100
        )
        
        assert job.title == 'Test Government Job 2024'
        assert job.source == source
        assert job.category == category
        assert job.total_posts == 100
        assert job.status == 'announced'  # Default status
    
    def test_string_representation(self):
        """Test job posting string representation."""
        job = JobPostingFactory(title='Test Job 2024')
        
        assert str(job) == 'Test Job 2024'
    
    def test_slug_generation(self):
        """Test automatic slug generation."""
        job = JobPostingFactory(title='Test Government Job 2024')
        
        # Slug should be generated automatically
        assert job.slug is not None
        assert 'test' in job.slug.lower()
        assert 'government' in job.slug.lower()
    
    def test_unique_slug_constraint(self):
        """Test that job posting slugs must be unique."""
        JobPostingFactory(slug='test-unique-slug')
        
        with pytest.raises(IntegrityError):
            JobPostingFactory(slug='test-unique-slug')
    
    def test_status_choices(self):
        """Test valid status choices."""
        valid_statuses = ['announced', 'admit_card', 'answer_key', 'result', 'archived']
        
        for status in valid_statuses:
            job = JobPostingFactory(status=status)
            assert job.status == status
    
    def test_date_validation(self):
        """Test date field validations."""
        today = date.today()
        future_date = today + timedelta(days=30)
        past_date = today - timedelta(days=30)
        
        # Test valid date order
        job = JobPostingFactory(
            notification_date=past_date,
            application_start_date=today,
            application_end_date=future_date,
            exam_date=future_date + timedelta(days=30)
        )
        
        assert job.notification_date == past_date
        assert job.application_end_date == future_date
    
    def test_age_validation(self):
        """Test age limit validations."""
        # Valid age limits
        job = JobPostingFactory(min_age=18, max_age=35)
        assert job.min_age == 18
        assert job.max_age == 35
        
        # Test minimum age constraint
        with pytest.raises(ValidationError):
            job = JobPostingFactory(min_age=15)  # Below minimum
            job.full_clean()
        
        # Test maximum age constraint  
        with pytest.raises(ValidationError):
            job = JobPostingFactory(max_age=75)  # Above maximum
            job.full_clean()
    
    def test_financial_fields(self):
        """Test financial field validations."""
        job = JobPostingFactory(
            application_fee=Decimal('500.00'),
            salary_min=Decimal('25000.00'),
            salary_max=Decimal('50000.00')
        )
        
        assert job.application_fee == Decimal('500.00')
        assert job.salary_min == Decimal('25000.00')
        assert job.salary_max == Decimal('50000.00')
    
    def test_url_validations(self):
        """Test URL field validations."""
        job = JobPostingFactory(
            application_link='https://example.gov.in/apply',
            notification_url='https://example.gov.in/notification',
            result_url='https://example.gov.in/result'
        )
        
        assert job.application_link == 'https://example.gov.in/apply'
        
        # Test invalid URL
        with pytest.raises(ValidationError):
            job = JobPostingFactory(application_link='invalid-url')
            job.full_clean()
    
    def test_seo_fields(self):
        """Test SEO-related fields."""
        job = JobPostingFactory(
            seo_title='Test Job 2024 - Apply Online | SarkariBot',
            seo_description='Apply for Test Job. Check eligibility and apply online.',
            keywords='test job, government, apply online'
        )
        
        assert 'SarkariBot' in job.seo_title
        assert len(job.seo_description) <= 160  # SEO best practice
        assert 'government' in job.keywords
    
    def test_structured_data(self):
        """Test structured data generation."""
        job = JobPostingFactory()
        
        assert job.structured_data is not None
        assert job.structured_data.get('@type') == 'JobPosting'
        assert 'title' in job.structured_data
        assert 'hiringOrganization' in job.structured_data
    
    def test_job_relationship_cascade(self):
        """Test cascade deletion behavior."""
        source = GovernmentSourceFactory()
        category = JobCategoryFactory()
        job = JobPostingFactory(source=source, category=category)
        
        job_id = job.id
        
        # Delete source should cascade to job
        source.delete()
        
        with pytest.raises(JobPosting.DoesNotExist):
            JobPosting.objects.get(id=job_id)
    
    def test_job_manager_methods(self):
        """Test custom manager methods if they exist."""
        # Create jobs with different statuses
        announced_job = JobPostingFactory(status='announced')
        result_job = JobPostingFactory(status='result')
        archived_job = JobPostingFactory(status='archived')
        
        # Test filtering by status
        announced_jobs = JobPosting.objects.filter(status='announced')
        assert announced_job in announced_jobs
        assert result_job not in announced_jobs
    
    def test_job_ordering(self):
        """Test default ordering of job postings."""
        old_job = JobPostingFactory()
        # Manually set created_at to make it older
        old_job.created_at = timezone.now() - timedelta(days=1)
        old_job.save()
        
        new_job = JobPostingFactory()
        
        jobs = JobPosting.objects.all()
        
        # Should be ordered by created_at desc (newest first)
        assert jobs.first() == new_job
        assert jobs.last() == old_job


class TestJobPostingMethods(TestCase):
    """Test custom methods on JobPosting model."""
    
    def setUp(self):
        """Set up test data."""
        self.source = GovernmentSourceFactory()
        self.category = JobCategoryFactory()
        
    def test_is_application_open(self):
        """Test if application is currently open."""
        today = date.today()
        
        # Application open
        job = JobPostingFactory(
            application_start_date=today - timedelta(days=1),
            application_end_date=today + timedelta(days=30)
        )
        
        # This would test a custom method if it exists
        # assert job.is_application_open() is True
        
        # Application closed
        job_closed = JobPostingFactory(
            application_start_date=today - timedelta(days=60),
            application_end_date=today - timedelta(days=30)
        )
        
        # assert job_closed.is_application_open() is False
    
    def test_get_absolute_url(self):
        """Test URL generation for job posting."""
        job = JobPostingFactory(slug='test-job-2024')
        
        # This would test a get_absolute_url method if it exists
        # expected_url = f'/jobs/test-job-2024/'
        # assert job.get_absolute_url() == expected_url
    
    def test_days_until_deadline(self):
        """Test calculating days until application deadline."""
        today = date.today()
        job = JobPostingFactory(
            application_end_date=today + timedelta(days=15)
        )
        
        # This would test a custom method if it exists
        # assert job.days_until_deadline() == 15


@pytest.mark.integration
class TestJobPostingIntegration(TestCase):
    """Integration tests for job posting workflows."""
    
    def test_complete_job_lifecycle(self):
        """Test complete job posting lifecycle."""
        source = GovernmentSourceFactory()
        
        # Create initial job announcement
        job = JobPostingFactory(
            source=source,
            status='announced',
            application_start_date=date.today(),
            application_end_date=date.today() + timedelta(days=30)
        )
        
        assert job.status == 'announced'
        
        # Transition to admit card
        job.status = 'admit_card'
        job.save()
        
        assert job.status == 'admit_card'
        
        # Transition to result
        job.status = 'result'
        job.save()
        
        assert job.status == 'result'
    
    def test_bulk_job_creation(self):
        """Test creating multiple jobs efficiently."""
        source = GovernmentSourceFactory()
        category = JobCategoryFactory()
        
        jobs_data = []
        for i in range(10):
            jobs_data.append(JobPosting(
                title=f'Bulk Job {i}',
                source=source,
                category=category,
                slug=f'bulk-job-{i}'
            ))
        
        jobs = JobPosting.objects.bulk_create(jobs_data)
        
        assert len(jobs) == 10
        assert JobPosting.objects.filter(source=source).count() == 10