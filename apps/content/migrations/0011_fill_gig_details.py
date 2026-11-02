# Data migration, 2026-11-02: packages, extras, order questions and FAQs of Gigs A to D (from the Gig Kit)

from django.db import migrations


def fill(apps, schema_editor):
    from apps.content.gig_details import apply
    apply(apps.get_model('content_app', 'FiverrGig'), apps.get_model('content_app', 'FAQ'))


class Migration(migrations.Migration):

    dependencies = [
        ('content_app', '0010_gig_details'),
    ]

    operations = [
        migrations.RunPython(fill, migrations.RunPython.noop),
    ]
