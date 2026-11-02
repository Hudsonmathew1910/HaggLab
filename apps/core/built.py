"""
The studio's own products (admin: Content > Products). Heros is the first; add more in the admin.
EpicOutlet was removed on 2026-11-02 and ZenOS is paused, so neither is listed.
Descriptions state the mechanism, never a guarantee (no uptime or "never fails" claims).

built_products()  -> the first product (kept for templates that show one product)
all_products()    -> every published product
Each is a dict: name, slug, kind, pitch, desc, link, features [{name, kind, desc, link}].
"""
from apps.content.models import Product, SiteSetting

# Used only before the Product table has rows (e.g. a brand-new database before migrate)
HEROS = {
    'name': 'Heros', 'slug': 'heros', 'kind': 'AI assistant platform',
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


def as_dict(name, slug, kind, pitch, description, url, features):
    return {
        'name': name, 'slug': slug, 'kind': kind, 'pitch': pitch, 'desc': description, 'link': (url or '').strip(),
        'features': [{'name': f.get('name', ''), 'kind': f.get('kind', ''), 'desc': f.get('desc', ''),
                      'link': (f.get('url') or '').strip()} for f in (features or []) if f.get('name')],
    }


def all_products():
    rows = list(Product.objects.filter(published=True).order_by('order', 'name'))
    if rows:
        products = [as_dict(p.name, p.slug, p.kind, p.pitch, p.description, p.url, p.features) for p in rows]
    elif Product.objects.exists():
        return []  # products exist but are all unpublished
    else:
        products = [as_dict(**HEROS)]
    # The old link_heros_ai setting still wins for Heros when it is set (it was the link before Products existed)
    legacy = SiteSetting.objects.filter(key='link_heros_ai').values_list('value', flat=True).first()
    for p in products:
        if p['slug'] == 'heros' and (legacy or '').strip():
            p['link'] = legacy.strip()
    return products


def built_products():
    products = all_products()
    return products[0] if products else None
