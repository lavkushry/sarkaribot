#!/usr/bin/env python
"""
Script to create sample data for SarkariBot.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_dev')
django.setup()

from apps.jobs.models import JobCategory, JobPosting
from apps.sources.models import GovernmentSource

def create_sample_data():
    """Create sample categories, sources, and job postings."""
    
    print("Creating sample data...")
    
    # Create sample categories
    categories = [
        {
            'name': 'Central Government',
            'slug': 'central-government',
            'description': 'Jobs in central government departments and ministries',
            'position': 1
        },
        {
            'name': 'State Government',
            'slug': 'state-government', 
            'description': 'Jobs in state government departments',
            'position': 2
        },
        {
            'name': 'Bank/Finance',
            'slug': 'bank-finance',
            'description': 'Banking and financial sector jobs',
            'position': 3
        },
        {
            'name': 'Defence',
            'slug': 'defence',
            'description': 'Defence and security related jobs',
            'position': 4
        },
        {
            'name': 'Railway',
            'slug': 'railway',
            'description': 'Indian Railways job opportunities',
            'position': 5
        }
    ]
    
    created_categories = []
    for cat_data in categories:
        category, created = JobCategory.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        created_categories.append(category)
        if created:
            print(f"Created category: {category.name}")
        else:
            print(f"Category already exists: {category.name}")
    
    # Create sample government sources
    sources = [
        {
            'name': 'SSC',
            'display_name': 'Staff Selection Commission',
            'description': 'Staff Selection Commission conducts various competitive exams for recruitment to Group B and Group C posts in Government offices.',
            'base_url': 'https://ssc.nic.in'
        },
        {
            'name': 'UPSC',
            'display_name': 'Union Public Service Commission',
            'description': 'UPSC conducts Civil Services examination and other competitive exams for Group A and Group B services.',
            'base_url': 'https://upsc.gov.in'
        },
        {
            'name': 'IBPS',
            'display_name': 'Institute of Banking Personnel Selection',
            'description': 'IBPS conducts common recruitment process for banking sector.',
            'base_url': 'https://ibps.in'
        },
        {
            'name': 'RRB',
            'display_name': 'Railway Recruitment Board',
            'description': 'Railway Recruitment Boards conduct recruitment for Indian Railways.',
            'base_url': 'https://indianrailways.gov.in'
        },
        {
            'name': 'DRDO',
            'display_name': 'Defence Research and Development Organisation',
            'description': 'DRDO conducts recruitment for defence research positions.',
            'base_url': 'https://drdo.gov.in'
        }
    ]
    
    created_sources = []
    for source_data in sources:
        source, created = GovernmentSource.objects.get_or_create(
            name=source_data['name'],
            defaults=source_data
        )
        created_sources.append(source)
        if created:
            print(f"Created source: {source.display_name}")
        else:
            print(f"Source already exists: {source.display_name}")
    
    # Create sample job postings
    sample_jobs = [
        {
            'title': 'Staff Selection Commission Combined Higher Secondary Level Examination 2024',
            'department': 'Staff Selection Commission',
            'category': created_categories[0],  # Central Government
            'source': created_sources[0],  # SSC
            'qualification': '12th Pass',
            'total_posts': 4500,
            'application_start_date': timezone.now() - timedelta(days=10),
            'application_end_date': timezone.now() + timedelta(days=20),
            'status': 'announced',
            'priority': 5,
            'is_featured': True,
            'description': 'SSC CHSL 2024 notification for recruitment to various Group C posts in different ministries/departments/organizations.',
            'source_url': 'https://ssc.nic.in/chsl2024',
            'application_link': 'https://ssc.nic.in/apply',
            'notification_pdf': 'https://ssc.nic.in/chsl2024.pdf'
        },
        {
            'title': 'UPSC Civil Services Examination 2024',
            'department': 'Union Public Service Commission',
            'category': created_categories[0],  # Central Government
            'source': created_sources[1],  # UPSC
            'qualification': 'Graduate',
            'total_posts': 1000,
            'application_start_date': timezone.now() - timedelta(days=30),
            'application_end_date': timezone.now() + timedelta(days=10),
            'status': 'announced',
            'priority': 5,
            'is_featured': True,
            'description': 'UPSC CSE 2024 for recruitment to All India Services and Group A Central Services.',
            'source_url': 'https://upsc.gov.in/cse2024',
            'application_link': 'https://upsconline.nic.in',
            'notification_pdf': 'https://upsc.gov.in/cse2024.pdf'
        },
        {
            'title': 'IBPS PO/MT XIV Recruitment 2024',
            'department': 'Institute of Banking Personnel Selection',
            'category': created_categories[2],  # Bank/Finance
            'source': created_sources[2],  # IBPS
            'qualification': 'Graduate',
            'total_posts': 6432,
            'application_start_date': timezone.now() - timedelta(days=5),
            'application_end_date': timezone.now() + timedelta(days=25),
            'status': 'announced',
            'priority': 4,
            'is_featured': True,
            'description': 'IBPS PO/MT XIV recruitment for Probationary Officer/Management Trainee posts in participating banks.',
            'source_url': 'https://ibps.in/po2024',
            'application_link': 'https://ibps.in/apply',
            'notification_pdf': 'https://ibps.in/po2024.pdf'
        },
        {
            'title': 'Railway Recruitment Board Group D Recruitment 2024',
            'department': 'Railway Recruitment Board',
            'category': created_categories[4],  # Railway
            'source': created_sources[3],  # RRB
            'qualification': '10th Pass + ITI',
            'total_posts': 35000,
            'application_start_date': timezone.now() - timedelta(days=15),
            'application_end_date': timezone.now() + timedelta(days=15),
            'status': 'announced',
            'priority': 4,
            'is_featured': False,
            'description': 'RRB Group D recruitment for various posts like Track Maintainer, Helper, Assistant Pointsman, etc.',
            'source_url': 'https://indianrailways.gov.in/groupd2024',
            'application_link': 'https://rrbapply.gov.in',
            'notification_pdf': 'https://indianrailways.gov.in/groupd2024.pdf'
        },
        {
            'title': 'DRDO Scientist B Recruitment 2024',
            'department': 'Defence Research and Development Organisation',
            'category': created_categories[3],  # Defence
            'source': created_sources[4],  # DRDO
            'qualification': 'B.Tech/B.E.',
            'total_posts': 1000,
            'application_start_date': timezone.now() - timedelta(days=20),
            'application_end_date': timezone.now() + timedelta(days=5),
            'status': 'announced',
            'priority': 3,
            'is_featured': False,
            'description': 'DRDO Scientist B recruitment for research and development in defence technology.',
            'source_url': 'https://drdo.gov.in/scientist2024',
            'application_link': 'https://drdo.gov.in/apply',
            'notification_pdf': 'https://drdo.gov.in/scientist2024.pdf'
        }
    ]
    
    created_jobs = []
    for job_data in sample_jobs:
        # Generate slug from title
        slug = job_data['title'].lower().replace(' ', '-')[:50]
        
        job, created = JobPosting.objects.get_or_create(
            slug=slug,
            defaults={**job_data, 'slug': slug}
        )
        created_jobs.append(job)
        if created:
            print(f"Created job: {job.title[:50]}...")
        else:
            print(f"Job already exists: {job.title[:50]}...")
    
    print(f"\nSample data creation completed!")
    print(f"Categories created: {len(created_categories)}")
    print(f"Sources created: {len(created_sources)}")
    print(f"Jobs created: {len(created_jobs)}")
    
    return {
        'categories': created_categories,
        'sources': created_sources,
        'jobs': created_jobs
    }

if __name__ == '__main__':
    create_sample_data()
