"""
External integrations app configuration.
"""
from django.apps import AppConfig


class IntegrationsExternalConfig(AppConfig):
    """Configuration for external integrations app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.integrations_external'
    verbose_name = 'External Integrations'
    
    def ready(self):
        """Import signals when app is ready."""
        import apps.integrations_external.signals  # noqa
