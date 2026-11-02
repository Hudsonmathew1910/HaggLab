# Data migration, 2026-10-31: VoiceDesk is removed for good (it was unpublished in 0006)

from django.db import migrations


def delete_voicedesk(apps, schema_editor):
    apps.get_model('content_app', 'Project').objects.filter(slug='voicedesk').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('content_app', '0008_new_fiverr_gigs'),
    ]

    operations = [
        migrations.RunPython(delete_voicedesk, migrations.RunPython.noop),
    ]
