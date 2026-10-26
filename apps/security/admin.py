from django.contrib import admin
from .models import AuditEvent

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'actor', 'action', 'object_repr', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('actor', 'object_repr', 'details')
    readonly_fields = ('timestamp', 'actor', 'action', 'object_repr', 'ip_address', 'details')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
