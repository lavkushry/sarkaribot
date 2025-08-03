"""
Test factories for SarkariBot models using factory-boy.

This module provides factories for creating test instances of all models
with realistic data for comprehensive testing.
"""

import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, LazyAttribute, Iterator
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating test users."""
    
    class Meta:
        model = User
        
    username = Faker('user_name')
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_active = True
    is_staff = False
    is_superuser = False
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or 'testpass123'
        obj.set_password(password)
        obj.save()


class AdminUserFactory(UserFactory):
    """Factory for creating admin users."""
    
    is_staff = True
    is_superuser = True
    username = 'admin'
    email = 'admin@sarkaribot.com'


class JobCategoryFactory(DjangoModelFactory):
    """Factory for creating job categories."""
    
    class Meta:
        model = 'jobs.JobCategory'
        
    name = Iterator([
        'Latest Jobs', 'Admit Card', 'Answer Key', 'Result', 
        'Syllabus', 'Previous Papers', 'Notification'
    ])
    slug = LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    description = Faker('sentence', nb_words=10)
    position = Faker('random_int', min=0, max=10)
    is_active = True
    icon = Iterator(['fas fa-briefcase', 'fas fa-file', 'fas fa-key', 'fas fa-trophy'])


class GovernmentSourceFactory(DjangoModelFactory):
    """Factory for creating government sources."""
    
    class Meta:
        model = 'sources.GovernmentSource'
        
    name = Iterator(['SSC', 'UPSC', 'RRB', 'IBPS', 'SBI', 'LIC', 'ISRO'])
    display_name = LazyAttribute(lambda obj: f"{obj.name} - Staff Selection Commission")
    description = Faker('paragraph', nb_sentences=3)
    base_url = LazyAttribute(lambda obj: f"https://{obj.name.lower()}.nic.in")
    scrape_frequency = Iterator([6, 12, 24, 48])
    status = 'active'
    priority = Faker('random_int', min=1, max=5)
    last_scraped = Faker('date_time_this_month', tzinfo=timezone.get_current_timezone())
    
    @factory.lazy_attribute
    def config_json(self):
        return {
            'selectors': {
                'title': f'.{self.name.lower()}-title',
                'description': f'.{self.name.lower()}-desc',
                'last_date': f'.{self.name.lower()}-date',
                'link': f'.{self.name.lower()}-link'
            },
            'pagination': {
                'next_page': '.pagination .next',
                'max_pages': random.randint(2, 5)
            },
            'headers': {
                'User-Agent': 'SarkariBot/1.0 (+https://sarkaribot.com/bot)'
            },
            'delay': random.randint(1, 3)
        }


class JobPostingFactory(DjangoModelFactory):
    """Factory for creating job postings."""
    
    class Meta:
        model = 'jobs.JobPosting'
        
    title = Faker('sentence', nb_words=6)
    description = Faker('paragraph', nb_sentences=5)
    source = SubFactory(GovernmentSourceFactory)
    category = SubFactory(JobCategoryFactory)
    
    # Job details
    eligibility = Faker('sentence', nb_words=8)
    vacancy_count = Faker('random_int', min=10, max=1000)
    application_fee = Iterator([0, 100, 250, 500, 750, 1000])
    age_limit = Iterator(['18-30', '21-35', '18-35', '21-40', '18-40'])
    salary = Iterator(['25000-50000', '30000-60000', '40000-80000', '20000-40000'])
    
    # Dates
    publication_date = Faker('date_this_month')
    last_date = Faker('date_between', start_date='+30d', end_date='+90d')
    exam_date = Faker('date_between', start_date='+60d', end_date='+120d')
    
    # URLs
    application_link = LazyAttribute(lambda obj: f"{obj.source.base_url}/apply/{obj.id}")
    source_url = LazyAttribute(lambda obj: f"{obj.source.base_url}/notification/{obj.id}")
    
    # Status and SEO
    status = Iterator(['announced', 'admit_card', 'answer_key', 'result'])
    slug = LazyAttribute(lambda obj: f"{obj.title}-{obj.id}".lower().replace(' ', '-'))
    is_featured = Faker('boolean', chance_of_getting_true=20)
    
    # SEO fields (will be auto-generated in real app)
    seo_title = LazyAttribute(lambda obj: f"{obj.title} 2024 - Apply Online | SarkariBot")
    seo_description = LazyAttribute(lambda obj: f"Apply for {obj.title}. Last date: {obj.last_date}. Check eligibility, syllabus & apply online.")
    keywords = LazyAttribute(lambda obj: f"{obj.title}, government job, apply online, {obj.source.name}")
    
    @factory.lazy_attribute
    def structured_data(self):
        return {
            "@context": "https://schema.org/",
            "@type": "JobPosting",
            "title": self.title,
            "description": self.description,
            "hiringOrganization": {
                "@type": "Organization", 
                "name": self.source.display_name
            },
            "datePosted": self.publication_date.isoformat() if self.publication_date else None,
            "validThrough": self.last_date.isoformat() if self.last_date else None,
            "employmentType": "FULL_TIME",
            "jobLocation": {
                "@type": "Place",
                "addressCountry": "IN"
            }
        }


# Utility functions for creating batches of test data
def create_test_job_postings(count=10, **kwargs):
    """Create multiple job postings for testing."""
    return JobPostingFactory.create_batch(count, **kwargs)


def create_test_sources(count=5, **kwargs):
    """Create multiple government sources for testing."""
    return GovernmentSourceFactory.create_batch(count, **kwargs)


def create_complete_job_lifecycle(**kwargs):
    """Create a complete job posting with all related objects."""
    source = GovernmentSourceFactory()
    category = JobCategoryFactory(name='Latest Jobs')
    job = JobPostingFactory(source=source, category=category, **kwargs)
    
    return {
        'job': job,
        'source': source,
        'category': category,
    }