# Data migration, 2026-10-31: the five services and ten projects from Hagglab_services_projects_gigs.md

from django.db import migrations

# Each old service row is kept (so its links stay) and renamed to the closest new service
OLD_TO_NEW = {
    'answer-customers-staff-faster': 'ai-chatbots-rag-assistants',
    'turn-idea-into-working-product': 'saas-mvps-ai-web-apps',
    'turn-numbers-into-decisions': 'nlp-machine-learning-models',
    'remove-repetitive-work': 'python-programs-automation',
    'help-visitors-buy-or-book': 'ai-integration-support',
}

SOLUTIONS = [
    {
        "title": "AI chatbots, RAG assistants and LLM apps",
        "slug": "ai-chatbots-rag-assistants",
        "headline": "Stop answering the same questions all day",
        "problem": "Customers and staff ask the same things again and again. The answers sit in long documents, spreadsheets and old messages.",
        "cost_today": "Someone searches files, copies an answer or replies from memory. Replies are slow and uneven.",
        "step1_title": "Connect sources",
        "step1_desc": "Connect your documents, FAQs, product list or data.",
        "step2_title": "Answer with sources",
        "step2_desc": "The assistant answers only from your own content and shows its source. If it cannot find the answer, it says \"I don't know\".",
        "step3_title": "Human check",
        "step3_desc": "A person approves anything unsure or sensitive.",
        "expected_outcome": "Fewer repeat questions reach staff; a faster first reply.",
        "metrics": "repeat questions per week, share answered without staff",
        "order": 1
    },
    {
        "title": "SaaS MVPs and full-stack AI web apps",
        "slug": "saas-mvps-ai-web-apps",
        "headline": "Turn your idea into a working first version",
        "problem": "You have an app or portal idea but no developer. Big quotes scare you off before you see anything working.",
        "cost_today": "The idea stays in notes, or a long agency project starts before anyone has tested the idea.",
        "step1_title": "Core workflow",
        "step1_desc": "Agree one core workflow, for example \"a customer books a slot\".",
        "step2_title": "Weekly demo",
        "step2_desc": "We build a first working version, with a demo every week.",
        "step3_title": "Clean handover",
        "step3_desc": "Handover with plain-language documents. You own the code.",
        "expected_outcome": "A first version real users can try; a clear list of what to build next.",
        "metrics": "the core workflow works end to end, feedback from first test users",
        "order": 2
    },
    {
        "title": "NLP and machine learning models",
        "slug": "nlp-machine-learning-models",
        "headline": "Turn your messy text and spreadsheets into predictions",
        "problem": "You have text, tickets or sales history, and nobody has time to read it or predict from it.",
        "cost_today": "Messages are sorted by hand. Stock and demand are ordered by gut feeling and last year's numbers.",
        "step1_title": "Share your data",
        "step1_desc": "Share your data as CSV, Excel or text.",
        "step2_title": "Baseline first",
        "step2_desc": "We clean it, build a simple baseline first, then a stronger model, and compare them.",
        "step3_title": "Honest results",
        "step3_desc": "You get the model, a results report with its error stated, and an API if you want one.",
        "expected_outcome": "A prediction or classifier whose accuracy is stated next to a simple baseline, including when it does not beat it.",
        "metrics": "model error compared with a simple baseline",
        "order": 3
    },
    {
        "title": "Custom Python programs and workflow automation",
        "slug": "python-programs-automation",
        "headline": "Stop the copy-paste. Let a tool do the repeat work.",
        "problem": "Staff spend hours copying numbers, renaming files, building the same report and summarizing pages.",
        "cost_today": "The same steps repeat every week. Small copy errors slip in, and nobody enjoys the task.",
        "step1_title": "Name the task",
        "step1_desc": "Name the repeated task.",
        "step2_title": "Safe automation",
        "step2_desc": "We build a Python tool that does the steps and asks before anything risky.",
        "step3_title": "Logged actions",
        "step3_desc": "It keeps a log of what it did, and file moves can be undone.",
        "expected_outcome": "Hours saved on the named task; fewer copy-paste errors.",
        "metrics": "hours per week before and after, errors per month",
        "order": 4
    },
    {
        "title": "AI integration, orchestration and production support",
        "slug": "ai-integration-support",
        "headline": "Add AI to what you already have, and keep it running",
        "problem": "You already have a website or app. Adding AI breaks things, one model provider goes down, or something works on a laptop but fails live.",
        "cost_today": "A single AI provider, no fallback, no tests, and bugs found by customers.",
        "step1_title": "Review your app",
        "step1_desc": "We review your existing app and the one place AI should go.",
        "step2_title": "Add AI safely",
        "step2_desc": "We add it with a fallback between AI models, rate limits and automated tests around it.",
        "step3_title": "Keep it running",
        "step3_desc": "We debug what fails in production and hand over notes.",
        "expected_outcome": "An AI feature that keeps answering when one provider fails; fewer live errors.",
        "metrics": "share of AI requests answered when one provider fails, live errors per week",
        "order": 5
    }
]

# Project -> (order, service)
PROJECTS = {
    'documind': (1, 'ai-chatbots-rag-assistants'),
    'insightdesk': (2, 'ai-chatbots-rag-assistants'),
    'shopassist': (3, 'ai-chatbots-rag-assistants'),
    'bookit': (4, 'saas-mvps-ai-web-apps'),
    'mvpstarter': (5, 'saas-mvps-ai-web-apps'),
    'supportflow': (6, 'nlp-machine-learning-models'),
    'forecastboard': (7, 'nlp-machine-learning-models'),
    'reportbot': (8, 'python-programs-automation'),
    'deskpilot': (9, 'python-programs-automation'),
    'pagemind': (10, 'ai-integration-support'),
}

MVPSTARTER = {
    'title': 'MVPStarter',
    'headline': 'Your idea as a working first version',
    'status': 'Concept',
    'problem': 'You have an app idea but no developer, and a large quote scares you off.',
    'cost_today': 'The idea stays in notes, or a long project starts before anyone has tested it.',
    'step1_title': 'Core workflow',
    'step1_desc': 'Agree one core workflow.',
    'step2_title': 'Weekly demo',
    'step2_desc': 'We build it, with a working demo every week.',
    'step3_title': 'Code and documents',
    'step3_desc': 'You get the code and plain-language documents.',
    'demo_note': 'A small sample workflow built for the Try it page.',
    'expected_text': 'A first version real users can try.',
    'inside_text': 'Django or FastAPI, PostgreSQL, login and roles, a REST API.',
    'fiverr_gig_slug': 'mvpstarter',
    'built_for': 'Startups · Small businesses · Founders with an app idea',
    'use_cases': chr(10).join([
        'A startup tests its booking idea with real users before a full build.',
        'A small business turns a spreadsheet process into a web portal with logins.',
        'A team sees a working demo every week and decides what to build next.',
    ]),
    'try_ready': False,  # hidden until its Try it page works
}

# Gig link -> (services it shows on, projects it sells). One gig per service page.
GIGS = {
    'https://www.fiverr.com/s/2ppPDx8': (['ai-chatbots-rag-assistants'], ['documind', 'supportflow']),
    'https://www.fiverr.com/s/Vrrqdwd': (['nlp-machine-learning-models'], ['insightdesk', 'reportbot', 'forecastboard']),
    'https://www.fiverr.com/s/xrrxmQB': ([], ['bookit']),
    'https://www.fiverr.com/s/P44BjG0': (['saas-mvps-ai-web-apps'], ['mvpstarter']),
}


def apply_new_catalog(apps, schema_editor):
    Solution = apps.get_model('content_app', 'Solution')
    Project = apps.get_model('content_app', 'Project')
    FAQ = apps.get_model('content_app', 'FAQ')
    FiverrGig = apps.get_model('content_app', 'FiverrGig')

    for old, new in OLD_TO_NEW.items():
        if not Solution.objects.filter(slug=new).exists():
            Solution.objects.filter(slug=old).update(slug=new)
        FAQ.objects.filter(solution_slug=old).update(solution_slug=new)

    if not Solution.objects.exists():
        return  # empty database: seed_content creates everything

    solutions = {}
    for data in SOLUTIONS:
        sol, _ = Solution.objects.update_or_create(slug=data['slug'], defaults=data)
        solutions[sol.slug] = sol

    # VoiceDesk is removed from the catalog: hidden, not deleted
    Project.objects.filter(slug='voicedesk').update(published=False, try_ready=False)
    for project in Project.objects.filter(slug='voicedesk'):
        project.solutions.clear()
    Project.objects.get_or_create(slug='mvpstarter', defaults=MVPSTARTER)

    for slug, (order, service) in PROJECTS.items():
        project = Project.objects.filter(slug=slug).first()
        if project:
            project.order = order
            project.save(update_fields=['order'])
            project.solutions.set([solutions[service]])

    Project.objects.filter(slug='bookit', step3_desc__contains='QR code').update(
        step3_desc='You see the day on a dashboard.')
    FAQ.objects.filter(question='What do you not build?',
                       answer='Mobile apps, phone-call bots, online payment systems, and WordPress or Shopify work.').update(
        answer='Mobile apps, phone-call bots, online payment systems, WordPress or Shopify work, and Ruby on Rails.')

    for gig in FiverrGig.objects.all():
        mapping = GIGS.get(gig.url.replace('http://', 'https://'))
        gig.projects.remove(*Project.objects.filter(slug='voicedesk'))
        if mapping:
            services, projects = mapping
            gig.services.set(Solution.objects.filter(slug__in=services))
            gig.projects.add(*Project.objects.filter(slug__in=projects))


class Migration(migrations.Migration):

    dependencies = [
        ('content_app', '0005_clear_old_demo_links'),
    ]

    operations = [
        migrations.RunPython(apply_new_catalog, migrations.RunPython.noop),
    ]
