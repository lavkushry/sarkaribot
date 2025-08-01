"""
Jobs app configuration for SarkariBot.
"""

from django.apps import AppConfig


class JobsConfig(AppConfig):
    """Jobs application configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.jobs'
    verbose_name = 'Job Postings'
    
    def ready(self):
        """Import signal handlers when the app is ready."""
        import apps.jobs.signals  # noqa
