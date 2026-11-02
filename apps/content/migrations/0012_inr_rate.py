# Data migration, 2026-11-02: rupee estimate next to $ prices. Change or empty the value in the admin (Site Settings).

from django.db import migrations


def add_setting(apps, schema_editor):
    apps.get_model('content_app', 'SiteSetting').objects.get_or_create(key='inr_rate', defaults={
        'label': "Rupees per US dollar: shows an estimate like '≈ ₹5,700' next to each $ price. Empty = hide rupees.",
        'value': '95',
    })


class Migration(migrations.Migration):

    dependencies = [
        ('content_app', '0011_fill_gig_details'),
    ]

    operations = [
        migrations.RunPython(add_setting, migrations.RunPython.noop),
    ]
