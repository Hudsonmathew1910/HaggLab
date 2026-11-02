# Data migration, 2026-11-02: Heros becomes the first row in Products (it was hard-coded in apps/core/built.py).

from django.db import migrations

HEROS = {
    'name': 'Heros', 'slug': 'heros', 'kind': 'AI assistant platform', 'order': 1,
    'pitch': 'our AI assistant platform. Chat, coding help and data analysis in one place, live on the web.',
    'description': 'Our current product: an AI assistant platform with chat, data analysis, a browser extension '
                   'and a music assistant. Built with Django, PostgreSQL and Pinecone.',
    'url': 'https://hero-s-ai.alwaysdata.net/',
    'features': [
        {'name': 'Baymax', 'kind': 'Multi-model AI chat',
         'desc': 'Answers chat, coding, voice and file questions, and falls back across Gemini, OpenRouter and Groq.'},
        {'name': 'Halo', 'kind': 'Task orchestrator',
         'desc': 'Runs multi-step and parallel tasks and switches to another provider when one fails.'},
        {'name': 'Infinsight', 'kind': 'AI data analyst',
         'desc': 'Answers questions about uploaded CSV, Excel and PDF files, using RAG and live pandas analysis.'},
        {'name': 'Zeno', 'kind': 'Browser extension',
         'desc': 'A Chrome, Edge and Brave extension that brings the assistant to any web page.'},
        {'name': 'Zuno', 'kind': 'Music assistant',
         'desc': 'A music and media assistant, as a tab in Zeno and as its own app.'},
    ],
}


def add_heros(apps, schema_editor):
    Product = apps.get_model('content_app', 'Product')
    SiteSetting = apps.get_model('content_app', 'SiteSetting')
    data = dict(HEROS)
    link = SiteSetting.objects.filter(key='link_heros_ai').values_list('value', flat=True).first()
    if (link or '').strip():
        data['url'] = link.strip()
    zeno = SiteSetting.objects.filter(key='link_zeno').values_list('value', flat=True).first()
    if (zeno or '').strip():
        data['features'] = [dict(f, url=zeno.strip()) if f['name'] == 'Zeno' else f for f in data['features']]
    Product.objects.get_or_create(slug='heros', defaults=data)


class Migration(migrations.Migration):

    dependencies = [
        ('content_app', '0019_product'),
    ]

    operations = [
        migrations.RunPython(add_heros, migrations.RunPython.noop),
    ]
