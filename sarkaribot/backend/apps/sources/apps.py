"""
Sources app configuration for SarkariBot.
"""

from django.apps import AppConfig


class SourcesConfig(AppConfig):
    """Sources application configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sources'
    verbose_name = 'Government Sources'
