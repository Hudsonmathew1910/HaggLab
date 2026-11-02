from django.contrib.admin.apps import AdminConfig


class StudioAdminConfig(AdminConfig):
    """django.contrib.admin, but with the two-factor admin site (apps/security/admin_site.py)."""
    default_site = 'apps.security.admin_site.StudioAdminSite'
