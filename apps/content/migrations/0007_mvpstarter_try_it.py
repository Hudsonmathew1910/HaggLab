# Data migration, 2026-10-31: MVPStarter now has a Try it page (a client request portal for a sample company)

from django.db import migrations


def describe_try_page(apps, schema_editor):
    Project = apps.get_model('content_app', 'Project')
    Project.objects.filter(slug='mvpstarter', demo_note='A small sample workflow built for the Try it page.').update(
        demo_note='FixRight Home Services, a sample company. Your requests are private to you.')
    Project.objects.filter(slug='mvpstarter', inside_text='Django or FastAPI, PostgreSQL, login and roles, a REST API.').update(
        inside_text='Django or FastAPI, PostgreSQL, user roles, a status workflow with rules, a dashboard, a REST API.')


class Migration(migrations.Migration):

    dependencies = [
        ('content_app', '0006_new_services_and_projects'),
    ]

    operations = [
        migrations.RunPython(describe_try_page, migrations.RunPython.noop),
    ]
