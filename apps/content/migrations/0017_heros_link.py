# Data migration, 2026-11-02: the live Heros link, shown on the home and About pages. Kept if already set in the admin.

from django.db import migrations

URL = 'https://hero-s-ai.alwaysdata.net/'


def set_link(apps, schema_editor):
    SiteSetting = apps.get_model('content_app', 'SiteSetting')
    setting, _ = SiteSetting.objects.get_or_create(key='link_heros_ai', defaults={'label': 'Heros live link'})
    if not setting.value.strip():
        setting.value = URL
        setting.save(update_fields=['value'])


class Migration(migrations.Migration):

    dependencies = [
        ('content_app', '0016_heros_name'),
    ]

    operations = [
        migrations.RunPython(set_link, migrations.RunPython.noop),
    ]
