# Data migration, 2026-11-02: EpicOutlet is no longer shown anywhere; Hero's AI is the studio's only current product.

from django.db import migrations


def remove(apps, schema_editor):
    apps.get_model('content_app', 'SiteSetting').objects.filter(key='link_epicoutlet').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('content_app', '0014_ai_integration_packages'),
    ]

    operations = [
        migrations.RunPython(remove, migrations.RunPython.noop),
    ]
