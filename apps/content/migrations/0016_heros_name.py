# Data migration, 2026-11-02: the product is called "Heros" (not "Hero's AI").

from django.db import migrations


def rename(apps, schema_editor):
    apps.get_model('content_app', 'SiteSetting').objects.filter(key='link_heros_ai').update(label='Heros live link')


class Migration(migrations.Migration):

    dependencies = [
        ('content_app', '0015_remove_epicoutlet'),
    ]

    operations = [
        migrations.RunPython(rename, migrations.RunPython.noop),
    ]
