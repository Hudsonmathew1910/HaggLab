from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Inquiry, InquiryFile


class InquiryFileInline(admin.TabularInline):
    model = InquiryFile
    extra = 0
    can_delete = True
    fields = ('download', 'question', 'size_label', 'uploaded_at')
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description='File')
    def download(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('inquiry_file', args=[obj.pk]), obj.original_name)

    @admin.display(description='Size')
    def size_label(self, obj):
        return obj.size_label()


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'service', 'package', 'timeline', 'file_count', 'created_at')
    list_filter = ('service', 'timeline', 'created_at')
    search_fields = ('name', 'email', 'problem', 'business')
    readonly_fields = ('uuid', 'created_at', 'ip_address')
    inlines = [InquiryFileInline]

    @admin.display(description='Files')
    def file_count(self, obj):
        return obj.files.count() or '-'
