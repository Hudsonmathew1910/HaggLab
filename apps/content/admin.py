from django.contrib import admin
from .models import Solution, Project, FAQ, SiteSetting, FiverrGig
from apps.security.models import AuditEvent

class AuditedModelAdmin(admin.ModelAdmin):
    """Logs object changes to AuditEvent."""
    def save_model(self, request, obj, form, change):
        action = 'UPDATE' if change else 'CREATE'
        super().save_model(request, obj, form, change)
        actor = request.user.username if request.user.is_authenticated else 'system'
        AuditEvent.objects.create(
            actor=actor,
            action=f"{obj._meta.model_name.upper()}_{action}",
            object_repr=str(obj),
            ip_address=request.META.get('REMOTE_ADDR', ''),
            details=f"Admin {action.lower()} on {obj._meta.verbose_name}: {obj}"
        )

    def delete_model(self, request, obj):
        actor = request.user.username if request.user.is_authenticated else 'system'
        AuditEvent.objects.create(
            actor=actor,
            action=f"{obj._meta.model_name.upper()}_DELETE",
            object_repr=str(obj),
            ip_address=request.META.get('REMOTE_ADDR', ''),
            details=f"Admin deleted {obj._meta.verbose_name}: {obj}"
        )
        super().delete_model(request, obj)


@admin.register(SiteSetting)
class SiteSettingAdmin(AuditedModelAdmin):
    list_display = ('key', 'label', 'value')
    search_fields = ('key', 'label', 'value')


@admin.register(Solution)
class SolutionAdmin(AuditedModelAdmin):
    list_display = ('title', 'slug', 'order', 'published')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('order', 'published')
    search_fields = ('title', 'headline', 'problem')


@admin.register(Project)
class ProjectAdmin(AuditedModelAdmin):
    # Try ready is the switch that makes a project public on the live site: tick it here for several at once
    list_display = ('title', 'try_ready', 'published', 'order', 'delivered_count', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('try_ready', 'published')
    list_editable = ('try_ready', 'published', 'order')
    search_fields = ('title', 'headline', 'problem', 'inside_text')
    filter_horizontal = ('solutions',)
    # The Try it page replaced demo links; hiding the old field keeps it from blocking saves
    exclude = ('demo_url',)


@admin.register(FAQ)
class FAQAdmin(AuditedModelAdmin):
    list_display = ('question', 'page', 'solution_slug', 'order', 'published')
    list_filter = ('page', 'published')
    list_editable = ('order', 'published')
    search_fields = ('question', 'answer')


@admin.register(FiverrGig)
class FiverrGigAdmin(AuditedModelAdmin):
    list_display = ('title', 'url', 'covers', 'service_pages', 'order', 'active')
    list_editable = ('order', 'active')
    filter_horizontal = ('projects', 'services')
    search_fields = ('title', 'url')

    @admin.display(description='Service pages')
    def service_pages(self, obj):
        return ', '.join(s.title for s in obj.services.all()) or '-'

    @admin.display(description='Projects')
    def covers(self, obj):
        return ', '.join(p.title for p in obj.projects.all()) or '-'
