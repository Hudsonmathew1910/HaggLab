# Data migration, 2026-11-02: an admin switch for Haggi, the HaggLab Assistant chat (on by default).

from django.db import migrations


def add_setting(apps, schema_editor):
    apps.get_model('content_app', 'SiteSetting').objects.get_or_create(key='assistant_enabled', defaults={
        'label': 'Haggi chat assistant: on = show the chat on every page, off = hide it', 'value': 'on'})


class Migration(migrations.Migration):

    dependencies = [
        ('content_app', '0017_heros_link'),
    ]

    operations = [
        migrations.RunPython(add_setting, migrations.RunPython.noop),
    ]
