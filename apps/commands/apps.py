from django.apps import AppConfig


class CommandsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.commands'
    verbose_name = 'Commands'
    
    def ready(self):
        """Import signals when app is ready."""
        import apps.commands.signals  # noqa
