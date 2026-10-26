from django.contrib import admin
from .models import AnalyticsEvent

@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'event_name', 'path', 'target', 'ip_prefix')
    list_filter = ('event_name', 'timestamp')
    search_fields = ('path', 'target')
    readonly_fields = ('timestamp', 'event_name', 'path', 'target', 'ip_prefix')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
