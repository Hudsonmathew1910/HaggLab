from django.conf import settings
from django.contrib import admin

from .models import AiUsage


@admin.register(AiUsage)
class AiUsageAdmin(admin.ModelAdmin):
    """Read-only view of how many AI calls the site made each day, against the daily limit."""
    list_display = ('day', 'calls', 'limit')
    readonly_fields = ('day', 'calls')

    @admin.display(description='Daily limit')
    def limit(self, obj):
        return getattr(settings, 'AI_DAILY_CAP', 0) or 'no limit'

    def has_add_permission(self, request):
        return False
