from django.core.management.base import BaseCommand
from apps.content.models import Solution, Project, FAQ, SiteSetting, FiverrGig
from apps.content import gig_details
from apps.content.project_fit import PROJECT_FIT

class Command(BaseCommand):
    help = ('Seed solutions, projects, FAQs and site settings from Content.md. '
            'By default only missing rows are created, so edits made in the admin are kept. '
            'Use --reset to overwrite existing rows with the seed text.')

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true',
                            help='Overwrite existing solutions, projects and FAQs (admin edits are lost).')

    def handle(self, *args, **options):
        reset = options['reset']

        def save(model, lookup, defaults):
            if reset:
                return model.objects.update_or_create(**lookup, defaults=defaults)
            return model.objects.get_or_create(**lookup, defaults=defaults)

        self.stdout.write("Seeding SiteSettings...")
        settings_data = [
            ("reply_time", "Real reply time for inquiries", ""),
            ("budget_bands", "Budget band selections", ""),
            ("code_ownership_terms", "Code ownership terms statement", ""),
            ("support_window", "Post-handover support duration", ""),
            ("build_timeline_average", "Average build duration", ""),
            ("nda_policy", "NDA availability terms", ""),
            ("deletion_contact", "Direct instructions for data deletion", ""),
            ("fiverr_enabled", "Fiverr: auto = show Fiverr where a gig link exists, off = hide it, on = always show", "auto"),
            ("fiverr_profile_url", "Fiverr profile link (used by every Fiverr button)", ""),
            ("github_url", "GitHub profile link", ""),
            ("revisions_per_tier", "Revisions included (per package tier)", ""),
            ("link_heros_ai", "Heros live link", "https://hero-s-ai.alwaysdata.net/"),
            ("link_zeno", "Zeno extension link (store or repository)", ""),
            ("assistant_enabled", "Haggi chat assistant: on = show the chat on every page, off = hide it", "on"),
            ("inr_rate", "Rupees per US dollar: shows an estimate like '≈ ₹5,700' next to each $ price. Empty = hide rupees.", "95"),
        ]
        # get_or_create: re-running the seed on deploy must not wipe values entered in the admin
        for key, label, val in settings_data:
            SiteSetting.objects.get_or_create(key=key, defaults={'label': label, 'value': val})

        self.stdout.write("Seeding Solutions...")
        solutions_data = [
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

        solutions_dict = {}
        for s_data in solutions_data:
            sol, _ = save(Solution, {'slug': s_data['slug']}, s_data)
            solutions_dict[sol.slug] = sol

        self.stdout.write("Seeding Projects...")
        projects_data = [
            {
                "title": "DocuMind",
                "slug": "documind",
                "headline": "Answers from your own documents, with the source shown",
                "status": "Concept",
                "problem": "Staff and customers keep asking questions that are already answered in long PDFs.",
                "cost_today": "Someone searches the files and copies the answer, or guesses.",
                "step1_title": "Upload documents",
                "step1_desc": "Upload your handbook or policy documents.",
                "step2_title": "Ask questions",
                "step2_desc": "Ask questions in plain English.",
                "step3_title": "Get verified answers",
                "step3_desc": "Get the answer and the page it came from. If it is not in the documents, it says so.",
                "demo_url": "",  # enter the real demo address in the admin once deployed
                "demo_note": "A sample college handbook. Demo data.",
                "measured_text": "",
                "expected_text": "Fewer repeat questions reach staff.",
                "inside_text": "Django, document search with embeddings, model fallback, upload limits, files deleted after 24 hours.",
                "fiverr_gig_slug": "documind",
                "order": 1,
                "solutions": ["ai-chatbots-rag-assistants"]
            },
            {
                "title": "InsightDesk",
                "slug": "insightdesk",
                "headline": "Ask your spreadsheet questions in plain English",
                "status": "Concept",
                "problem": "You have sales data in Excel but no analyst to read it.",
                "cost_today": "Questions wait for days, and the answers are hard to check.",
                "step1_title": "Upload spreadsheet",
                "step1_desc": "Upload a CSV or Excel file.",
                "step2_title": "Ask questions",
                "step2_desc": "Ask a question in plain English.",
                "step3_title": "Inspect code & chart",
                "step3_desc": "Get a table or chart, and see the code that produced it.",
                "demo_url": "",  # enter the real demo address in the admin once deployed
                "demo_note": "A sample sales file. Demo data.",
                "measured_text": "",
                "expected_text": "Answers in minutes, with a calculation you can check.",
                "inside_text": "Pandas, safe code execution, model fallback, charts.",
                "fiverr_gig_slug": "insightdesk",
                "order": 2,
                "solutions": ["ai-chatbots-rag-assistants"]
            },
            {
                "title": "ShopAssist",
                "slug": "shopassist",
                "headline": "Help shoppers find the right product in one chat",
                "status": "Concept",
                "problem": "Visitors leave when they cannot find the right product fast.",
                "cost_today": "They scroll, filter and give up.",
                "step1_title": "Connect catalog",
                "step1_desc": "Connect your product list.",
                "step2_title": "Customer chat",
                "step2_desc": "The shopper says what they want in chat.",
                "step3_title": "Curated matches",
                "step3_desc": "The assistant shows matching products with direct links.",
                "demo_url": "",  # enter the real demo address in the admin once deployed
                "demo_note": "A small demo store.",
                "measured_text": "",
                "expected_text": "Easier product discovery. Track: chat-to-product-click rate.",
                "inside_text": "Django, an AI model that can call a product search, a catalog API.",
                "fiverr_gig_slug": "shopassist",
                "order": 3,
                "solutions": ["ai-chatbots-rag-assistants"]
            },
            {
                "title": "BookIt",
                "slug": "bookit",
                "headline": "Online bookings without double bookings",
                "status": "Concept",
                "problem": "Bookings by phone and chat get mixed up.",
                "cost_today": "Notebooks, missed calls and double-booked slots.",
                "step1_title": "Pick a slot",
                "step1_desc": "The customer picks a free slot.",
                "step2_title": "Automatic block",
                "step2_desc": "The system blocks double bookings and confirms by email.",
                "step3_title": "Unified schedule",
                "step3_desc": "You see the day on a dashboard.",
                "demo_url": "",
                "demo_note": "A fictional venue, Demo Turf. Bookings reset daily.",
                "measured_text": "",
                "expected_text": "Fewer double bookings; more bookings made online.",
                "inside_text": "Django, user roles, mobile-first pages.",
                "fiverr_gig_slug": "bookit",
                "order": 4,
                "solutions": ["saas-mvps-ai-web-apps"]
            },
            {
                "title": "MVPStarter",
                "slug": "mvpstarter",
                "headline": "Your idea as a working first version",
                "status": "Concept",
                "problem": "You have an app idea but no developer, and a large quote scares you off.",
                "cost_today": "The idea stays in notes, or a long project starts before anyone has tested it.",
                "step1_title": "Core workflow",
                "step1_desc": "Agree one core workflow.",
                "step2_title": "Weekly demo",
                "step2_desc": "We build it, with a working demo every week.",
                "step3_title": "Code and documents",
                "step3_desc": "You get the code and plain-language documents.",
                "demo_url": "",
                "demo_note": "FixRight Home Services, a sample company. Your requests are private to you.",
                "measured_text": "",
                "expected_text": "A first version real users can try.",
                "inside_text": "Django or FastAPI, PostgreSQL, user roles, a status workflow with rules, a dashboard, a REST API.",
                "fiverr_gig_slug": "mvpstarter",
                "order": 5,
                "solutions": ["saas-mvps-ai-web-apps"]
            },
            {
                "title": "SupportFlow",
                "slug": "supportflow",
                "headline": "Sort support messages by urgency, with replies drafted",
                "status": "Concept",
                "problem": "Messages arrive mixed together and get answered in random order.",
                "cost_today": "Urgent messages sit under easy ones.",
                "step1_title": "Ingest tickets",
                "step1_desc": "Messages come in from forms or email.",
                "step2_title": "Triage & draft",
                "step2_desc": "The tool labels the topic and urgency and drafts a reply.",
                "step3_title": "Staff approval",
                "step3_desc": "A person approves the draft.",
                "demo_url": "",
                "demo_note": "50 sample messages.",
                "measured_text": "",
                "expected_text": "Faster first reply; urgent messages found first.",
                "inside_text": "An intent classifier with model fallback, Django, charts.",
                "fiverr_gig_slug": "supportflow",
                "order": 6,
                "solutions": ["nlp-machine-learning-models"]
            },
            {
                "title": "ForecastBoard",
                "slug": "forecastboard",
                "headline": "See next month's demand before you order stock",
                "status": "Concept",
                "problem": "Stock orders are guesses, so shelves are too full or empty.",
                "cost_today": "Gut feeling and last year's numbers.",
                "step1_title": "Upload history",
                "step1_desc": "Upload past sales records.",
                "step2_title": "Compare baselines",
                "step2_desc": "The tool compares a simple method with stronger ones.",
                "step3_title": "Honest forecast",
                "step3_desc": "You get a forecast with its error range and a plain summary.",
                "demo_url": "",
                "demo_note": "A public or sample dataset, labelled.",
                "measured_text": "",
                "expected_text": "A forecast whose accuracy is stated.",
                "inside_text": "scikit-learn, XGBoost, pandas.",
                "fiverr_gig_slug": "forecastboard",
                "order": 7,
                "solutions": ["nlp-machine-learning-models"]
            },
            {
                "title": "PageMind",
                "slug": "pagemind",
                "headline": "Ask any web page a question",
                "status": "Concept",
                "problem": "Teams copy text from pages into chat tools all day.",
                "cost_today": "Copy, switch tab, paste, repeat.",
                "step1_title": "Open page",
                "step1_desc": "Open any article or documentation page.",
                "step2_title": "Ask or highlight",
                "step2_desc": "Ask a question, or select text and right-click.",
                "step3_title": "Instant summary",
                "step3_desc": "Get a summary or answer, and keep the research history.",
                "demo_url": "",
                "demo_note": "A screen recording of the extension.",
                "measured_text": "",
                "expected_text": "Less copy-paste. Track: time per research task.",
                "inside_text": "A Chrome and Edge extension, a Django backend, a privacy page.",
                "fiverr_gig_slug": "pagemind",
                "order": 10,
                "solutions": ["ai-integration-support"]
            },
            {
                "title": "DeskPilot",
                "slug": "deskpilot",
                "headline": "One command bar for the boring computer tasks",
                "status": "Concept",
                "problem": "Office staff repeat the same file and email tasks every day.",
                "cost_today": "Open, rename, move, draft, repeat.",
                "step1_title": "Type the task",
                "step1_desc": "Type the task in plain words.",
                "step2_title": "Safe tool action",
                "step2_desc": "The assistant picks a safe action from its tool list and asks before anything risky.",
                "step3_title": "Audit log",
                "step3_desc": "It logs what it did, and file moves can be undone.",
                "demo_url": "",
                "demo_note": "A screen recording using a practice folder. Windows only.",
                "measured_text": "",
                "expected_text": "Hours saved on the named task.",
                "inside_text": "Python, a desktop window toolkit, a tool list the AI can call.",
                "fiverr_gig_slug": "deskpilot",
                "order": 9,
                "solutions": ["python-programs-automation"]
            },
            {
                "title": "ReportBot",
                "slug": "reportbot",
                "headline": "The weekly report that writes itself",
                "status": "Concept",
                "problem": "Managers spend hours each week copying numbers into a report.",
                "cost_today": "Open files, copy figures, fix the charts, send.",
                "step1_title": "Connect sheet",
                "step1_desc": "Connect a sheet or upload an export file.",
                "step2_title": "Code calculation",
                "step2_desc": "The tool calculates figures with code, draws charts, and adds a separate short summary.",
                "step3_title": "PDF & dashboard",
                "step3_desc": "You get a PDF and a dashboard on a set schedule.",
                "demo_url": "",
                "demo_note": "A sample sheet and an on-demand report button.",
                "measured_text": "",
                "expected_text": "Hours saved every week.",
                "inside_text": "Pandas, charts, read-only Google Sheets access, a scheduler.",
                "fiverr_gig_slug": "reportbot",
                "order": 8,
                "solutions": ["python-programs-automation"]
            }
        ]

        for p_data in projects_data:
            sol_slugs = p_data.pop('solutions')
            proj, created = save(Project, {'slug': p_data['slug']}, p_data)
            for s_slug in sol_slugs if (created or reset) else []:
                if s_slug in solutions_dict:
                    proj.solutions.add(solutions_dict[s_slug])

        self.stdout.write("Seeding FAQs...")
        faqs_data = [
            ("Can I try something before I hire?", "Yes. Every project has a Try it page that runs on sample data. Click a project and try it.", "home", 2),
            ("How do I order?", "If you found us on Fiverr, please chat and order there. Otherwise, use the Start a project form.", "home", 3),
            ("Who owns the code?", "You own the finished project deliverables after final payment.", "home", 4),
            ("What if the AI gives a wrong answer?", "It can. We test with questions written for your case, show where it fails, and add I don't know answers and a human check for sensitive items. No AI tool is right every time.", "home", 5),
            ("What happens to my data?", "See Security and data. The demos run on built-in sample data and do not accept file uploads.", "faq", 8),
            ("What do you not build?", "Mobile apps, phone-call bots, online payment systems, WordPress or Shopify work, and Ruby on Rails.", "faq", 9),
        ]

        for q, a, page, order in faqs_data:
            save(FAQ, {'question': q}, {'answer': a, 'page': page, 'order': order})

        # Confirmed policy (2026-10-22): set it wherever the admin value is still blank
        SiteSetting.objects.filter(key="code_ownership_terms", value="").update(value="You own the finished project and its code after final payment.")

        # "Built for" and "Use cases": fill only where still blank, so admin edits win
        for slug, (built_for, uses) in PROJECT_FIT.items():
            proj = Project.objects.filter(slug=slug).first()
            if proj and not proj.built_for:
                proj.built_for = built_for
            if proj and not proj.use_cases:
                proj.use_cases = chr(10).join(uses)
            if proj:
                proj.save(update_fields=['built_for', 'use_cases'])

        # Projects are presented by their Try it pages, so the old demo/concept wording is retired
        wording = {
            "Can I try something before I hire?": "Yes. Every project has a Try it page that runs on sample data. Click a project and try it.",
            "Do the demos use real data?": None,
            "What happens to my data?": "See Security and data. The Try it pages run on sample data and text you type. They do not accept file uploads.",
        }
        for question, answer in wording.items():
            if answer is None:
                FAQ.objects.filter(question=question).update(published=False)
            else:
                FAQ.objects.filter(question=question).update(answer=answer)
        FAQ.objects.get_or_create(question="Do the Try it pages use real data?", defaults={
            'answer': "No. They use made-up or public sample data. Please don't enter passwords or confidential information.",
            'page': 'home', 'order': 6})

        # Fiverr gigs. Each one is added once, when no gig with that link exists yet; after that it is edited
        # in the admin (Content > Fiverr gigs). To hide a gig, untick Active rather than deleting it.
        # One gig per service (Gigs A to D in Hagglab_services_projects_gigs.md). AI integration and support
        # has no gig of its own: PageMind is sold as an add-on on the AI assistant gig.
        KNOWN_GIGS = [
            ('AI chatbots and RAG assistants',
             'https://www.fiverr.com/hudson_mathew_j/build-a-custom-ai-document-assistant-with-rag-for-your-data',
             ['documind', 'insightdesk', 'shopassist', 'pagemind'], ['ai-chatbots-rag-assistants']),
            ('SaaS MVPs and AI web apps',
             'https://www.fiverr.com/hudson_mathew_j/build-a-custom-python-django-web-app-and-mvp-for-your-idea',
             ['bookit', 'mvpstarter'], ['saas-mvps-ai-web-apps']),
            ('NLP and machine learning models',
             'https://www.fiverr.com/hudson_mathew_j/build-nlp-and-machine-learning-models-for-your-business-data',
             ['supportflow', 'forecastboard'], ['nlp-machine-learning-models']),
            ('Python programs and automation',
             'https://www.fiverr.com/hudson_mathew_j/build-custom-python-programs-scripts-and-desktop-applications',
             ['reportbot', 'deskpilot'], ['python-programs-automation']),
        ]
        for order, (title, url, slugs, service_slugs) in enumerate(KNOWN_GIGS, 1):
            gig = FiverrGig.objects.filter(url__in=[url, url.replace('https://', 'http://')]).first()
            if not gig:
                gig = FiverrGig.objects.create(title=title, url=url, order=order)
                gig.projects.set(Project.objects.filter(slug__in=slugs))
            if not gig.services.exists():  # fill the service page once; admin edits are kept
                gig.services.set(Solution.objects.filter(slug__in=service_slugs))
        # Packages, extras, order questions and FAQs shown on the service pages (apps/content/gig_details.py)
        gig_details.apply(FiverrGig, FAQ, only_empty=True)  # admin edits are kept
        gig_details.apply_services(Solution, FAQ, only_empty=True)
        # The old default was "off"; switch it to "auto" so Fiverr follows the gig links
        SiteSetting.objects.filter(key='fiverr_enabled', value='off').update(value='auto')

        # Corrections that always apply, even without --reset (rows are hidden or fixed, never deleted)
        # The site speaks as a company: hide the old personal FAQ
        FAQ.objects.filter(question="Do you work alone?").update(published=False)
        # Build time is not known until real builds are done (Content.md: fill in after the first demos)
        FAQ.objects.filter(question="How long does a build take?").update(published=False)
        # The demos do not accept uploads, so the old 24-hour upload answer was not true
        FAQ.objects.filter(question="What happens to my data?", answer__contains="deleted after 24 hours").update(
            answer="See Security and data. The demos run on built-in sample data and do not accept file uploads.")

        self.stdout.write(self.style.SUCCESS("Database seeded successfully with verified Content.md entries."))
