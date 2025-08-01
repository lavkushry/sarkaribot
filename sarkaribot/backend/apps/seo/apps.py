"""
SEO App Configuration for SarkariBot.
"""

from django.apps import AppConfig


class SeoConfig(AppConfig):
    """Configuration for the SEO automation app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.seo'
    verbose_name = 'SEO Automation'
    
    def ready(self):
        """Initialize app when Django starts."""
        pass
