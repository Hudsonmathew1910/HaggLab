# Data migration, 2026-11-02: packages, extras, order questions and FAQs for AI integration and support,
# the one service with no Fiverr gig (apps/content/gig_details.py SERVICES)

from django.db import migrations


def fill(apps, schema_editor):
    from apps.content.gig_details import apply_services
    apply_services(apps.get_model('content_app', 'Solution'), apps.get_model('content_app', 'FAQ'))


class Migration(migrations.Migration):

    dependencies = [
        ('content_app', '0013_service_packages'),
    ]

    operations = [
        migrations.RunPython(fill, migrations.RunPython.noop),
    ]
