from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.monitoring'
    verbose_name = 'System Monitoring'

    def ready(self):
        """Initialize monitoring components when Django starts."""
        # Import signal handlers
        from . import signals  # noqa: F401