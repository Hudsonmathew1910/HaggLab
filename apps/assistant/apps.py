from django.apps import AppConfig


class AssistantConfig(AppConfig):
    """Haggi, the HaggLab Assistant: a small chat that answers from the site's live content."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.assistant'
    label = 'assistant'
    verbose_name = 'Haggi (HaggLab Assistant)'

    def ready(self):
        from . import signals  # noqa: F401  (refresh Haggi's knowledge when content changes)
