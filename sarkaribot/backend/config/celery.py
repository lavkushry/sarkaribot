"""
Celery configuration for SarkariBot project.
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('sarkaribot')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'scrape-all-sources': {
        'task': 'apps.scraping.tasks.scrape_all_sources',
        'schedule': 3600.0,  # Every hour
    },
    'cleanup-old-jobs': {
        'task': 'apps.jobs.tasks.cleanup_old_jobs',
        'schedule': 86400.0,  # Daily
    },
    'generate-sitemap': {
        'task': 'apps.seo.tasks.generate_sitemap',
        'schedule': 86400.0,  # Daily
    },
    'health-check': {
        'task': 'apps.core.tasks.health_check',
        'schedule': 900.0,  # Every 15 minutes
    },
}

app.conf.timezone = 'Asia/Kolkata'


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery functionality."""
    print(f'Request: {self.request!r}')
