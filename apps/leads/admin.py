from django.contrib import admin
from .models import Inquiry

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'service', 'timeline', 'created_at')
    list_filter = ('service', 'timeline', 'created_at')
    search_fields = ('name', 'email', 'problem', 'business')
    readonly_fields = ('uuid', 'created_at', 'ip_address')
