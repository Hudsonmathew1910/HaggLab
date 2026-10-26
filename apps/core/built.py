"""
Products the studio has already built and deployed (facts from Content.md).
Links come from Site Settings and are shown only once set.
"""
from apps.content.models import SiteSetting

BUILT = [
    ('link_heros_ai', 'Hero’s AI', 'AI platform', 'An AI assistant platform that answers questions and analyzes uploaded data.'),
    ('link_epicoutlet', 'EpicOutlet', 'Online store', 'An online store with an AI shopping assistant.'),
    ('link_zenos', 'ZenOS', 'Windows app', 'A Windows assistant that runs everyday computer tasks from one command bar.'),
    ('link_zeno', 'Zeno', 'Browser extension', 'A Chrome and Edge extension for chat and page help.'),
]


def built_products():
    links = dict(SiteSetting.objects.filter(key__in=[b[0] for b in BUILT]).values_list('key', 'value'))
    return [
        {'name': name, 'kind': kind, 'desc': desc, 'link': (links.get(key) or '').strip()}
        for key, name, kind, desc in BUILT
    ]
