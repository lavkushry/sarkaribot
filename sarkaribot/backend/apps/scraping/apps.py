"""
Scraping app configuration for SarkariBot.
"""

from django.apps import AppConfig


class ScrapingConfig(AppConfig):
    """Scraping application configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.scraping'
    verbose_name = 'Web Scraping Engine'
