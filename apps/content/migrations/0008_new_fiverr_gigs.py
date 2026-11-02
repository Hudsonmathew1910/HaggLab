# Data migration, 2026-10-31: the four new Fiverr gigs, one per service. The old gigs are switched off, not deleted.

from django.db import migrations

OLD_GIGS = [
    'https://www.fiverr.com/s/2ppPDx8',
    'https://www.fiverr.com/s/Vrrqdwd',
    'https://www.fiverr.com/s/xrrxmQB',
    'https://www.fiverr.com/s/P44BjG0',
]

# (title, link, projects it sells, service page it shows on)
NEW_GIGS = [
    ('AI chatbots and RAG assistants',
     'https://www.fiverr.com/hudson_mathew_j/build-a-custom-ai-document-assistant-with-rag-for-your-data',
     ['documind', 'insightdesk', 'shopassist', 'pagemind'], 'ai-chatbots-rag-assistants'),
    ('SaaS MVPs and AI web apps',
     'https://www.fiverr.com/hudson_mathew_j/build-a-custom-python-django-web-app-and-mvp-for-your-idea',
     ['bookit', 'mvpstarter'], 'saas-mvps-ai-web-apps'),
    ('NLP and machine learning models',
     'https://www.fiverr.com/hudson_mathew_j/build-nlp-and-machine-learning-models-for-your-business-data',
     ['supportflow', 'forecastboard'], 'nlp-machine-learning-models'),
    ('Python programs and automation',
     'https://www.fiverr.com/hudson_mathew_j/build-custom-python-programs-scripts-and-desktop-applications',
     ['reportbot', 'deskpilot'], 'python-programs-automation'),
]


def use_new_gigs(apps, schema_editor):
    FiverrGig = apps.get_model('content_app', 'FiverrGig')
    Project = apps.get_model('content_app', 'Project')
    Solution = apps.get_model('content_app', 'Solution')
    if not Solution.objects.exists():
        return  # empty database: seed_content creates the gigs

    for url in OLD_GIGS:
        FiverrGig.objects.filter(url__in=[url, url.replace('https://', 'http://')]).update(active=False)

    for order, (title, url, projects, service) in enumerate(NEW_GIGS, 1):
        gig, _ = FiverrGig.objects.update_or_create(url=url, defaults={'title': title, 'order': order, 'active': True})
        gig.projects.set(Project.objects.filter(slug__in=projects))
        gig.services.set(Solution.objects.filter(slug=service))


class Migration(migrations.Migration):

    dependencies = [
        ('content_app', '0007_mvpstarter_try_it'),
    ]

    operations = [
        migrations.RunPython(use_new_gigs, migrations.RunPython.noop),
    ]
