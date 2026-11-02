"""
Packages, extras, order questions and FAQs of the 4 Fiverr gigs (Gigs A to D), shown on the service pages.

Source: the HaggLab Gig Kit (2 Nov 2026). Fiverr blocks automated reads, so this is copied, not fetched.
The text is in the company voice ("we"), not the first-person voice used on Fiverr.
If a price changes on Fiverr, change it in the admin (Fiverr gigs) so the site matches.

Used by migration 0011 and by seed_content. Keys are the gig links.
"""

GIG_A = 'https://www.fiverr.com/hudson_mathew_j/build-a-custom-ai-document-assistant-with-rag-for-your-data'
GIG_B = 'https://www.fiverr.com/hudson_mathew_j/build-a-custom-python-django-web-app-and-mvp-for-your-idea'
GIG_C = 'https://www.fiverr.com/hudson_mathew_j/build-nlp-and-machine-learning-models-for-your-business-data'
GIG_D = 'https://www.fiverr.com/hudson_mathew_j/build-custom-python-programs-scripts-and-desktop-applications'


def pkg(tier, title, desc, price, days, revisions, included):
    return {'tier': tier, 'title': title, 'desc': desc, 'price': price, 'days': days,
            'revisions': revisions, 'included': included}


def extra(name, price, days, desc=''):
    return {'name': name, 'price': price, 'days': days, 'desc': desc}


def ask(question, kind='Free text', options=None):
    return {'question': question, 'kind': kind, 'options': options or []}


GIGS = {
    GIG_A: {
        'summary': (
            'We build an AI chatbot or assistant that answers from your own content, shows its source, and says '
            '"I don\'t know" when it cannot find the answer. FAQ chatbots, document Q&A over PDFs, CSV and Excel '
            '(RAG), assistants that call tools such as a product search, and fallback across AI providers so it '
            'keeps answering if one is down. Built with Python, Django or FastAPI, LangChain, pgvector or Pinecone. '
            'AI can be wrong, so sensitive replies get a human check.'),
        'packages': [
            pkg('Basic', 'FAQ Chatbot',
                'A website chatbot that answers from your FAQ text, with a clean chat window and source code.',
                60, 3, 1, ['1 LLM provider', 'Answers from your FAQ text', 'Web chat window', 'Source code']),
            pkg('Standard', 'RAG Document Assistant',
                "Answers from your PDFs, CSV or Excel with the source shown, and 'I don't know' when unsure.",
                150, 5, 2, ['Everything in Basic', 'RAG over PDF, CSV or Excel files', 'Source shown with each answer',
                            'pgvector or Pinecone search', 'Handover document']),
            pkg('Premium', 'RAG, Tools and Fallback',
                'RAG assistant with up to 3 tools, fallback across 3 AI providers, web chat and handover docs.',
                250, 8, 3, ['Everything in Standard', 'Up to 3 tools, such as product search',
                            'Fallback across 3 AI providers', 'Human review step for sensitive replies',
                            'Source code and handover document']),
        ],
        'extras': [
            extra('Faster delivery', 20, 2, 'Basic package in 2 days'),
            extra('Faster delivery', 30, 3, 'Standard package in 3 days'),
            extra('Faster delivery', 50, 5, 'Premium package in 5 days'),
            extra('RAG on your files', 90, 2, 'RAG answers from your PDF, CSV or Excel files, with the source shown for each answer.'),
            extra('AI model fine-tuning', 60, 2),
            extra('Desktop application', 40, 1),
            extra('Additional revision', 15, 0),
        ],
        'requirements': [
            ask('What problem should the chatbot solve? For example, answering customer questions or searching your documents.'),
            ask('Where will the chatbot be used?', 'Multiple choice',
                ['On my website', 'Inside my web app', 'Internal use only', 'Not sure yet']),
            ask('What should the chatbot answer from?', 'Multiple choice',
                ['PDFs or documents', 'Spreadsheets (CSV or Excel)', 'A product list', 'FAQ text', 'I have nothing yet']),
            ask('Roughly how many repeat questions, or hours a week, does this cost you today? One rough number is enough.'),
            ask('Attach a small sample of your documents or data. Please remove private or sensitive information first.',
                'Attachment'),
        ],
        'faqs': [
            ('What kinds of AI chatbots can you build?',
             'FAQ chatbots, document Q&A assistants and website support assistants. A chatbot can also search your '
             'product list. Features depend on the package.'),
            ('Can the chatbot make things up?',
             "It can be wrong. It answers only from your content, shows its source and says \"I don't know\" when it "
             'cannot find the answer. We add a human check for sensitive replies.'),
            ('Can you connect it to my documents or data?',
             'Yes. PDF, text, CSV and Excel files are supported. We use pgvector or Pinecone for search, depending on '
             'the project. Please remove private data you do not want us to see.'),
            ('Do I get the source code?',
             'Yes. You own the finished project and its code after final payment, with a plain-language handover document.'),
        ],
    },
    GIG_B: {
        'summary': (
            'We build the first working version of your SaaS idea around one core workflow, show a demo every week, '
            'and hand over code you own. Login, user roles and a database; dashboards, an admin panel and a REST API; '
            'booking, ordering or customer-portal workflows; one AI feature if your idea needs it; and automated tests '
            'for the key rule, such as no double bookings. Built with Python, Django or FastAPI, PostgreSQL or '
            'Supabase. Not included: mobile apps and online payments.'),
        'packages': [
            pkg('Basic', 'Starter Prototype',
                'One core workflow with 2 to 3 pages, login and a database, built on Django.',
                55, 4, 1, ['One core workflow', '2 to 3 pages', 'Login', 'Database', 'Responsive pages', 'Source code']),
            pkg('Standard', 'Working MVP',
                'MVP with user roles, database, REST API and admin panel, plus a demo every week.',
                140, 8, 2, ['Everything in Basic', 'User roles', 'REST API', 'Admin panel', 'Dashboard', 'Weekly demo',
                            'Handover document']),
            pkg('Premium', 'MVP, AI and Tests',
                'MVP plus one AI feature, automated tests, deployment help and handover documents.',
                300, 14, 3, ['Everything in Standard', 'One AI feature', 'Automated tests for the key rule',
                             'Deployment help', 'Handover walkthrough']),
        ],
        'extras': [
            extra('Faster delivery', 20, 3, 'Basic package in 3 days'),
            extra('Faster delivery', 30, 5, 'Standard package in 5 days'),
            extra('Faster delivery', 50, 9, 'Premium package in 9 days'),
            extra('Roles, API, admin', 85, 4, 'User roles, a REST API and an admin panel added to the starter app.'),
            extra('Additional page', 60, 2),
            extra('Detailed code comments', 55, 3),
            extra('Content upload', 45, 1),
            extra('Additional revision', 15, 0),
        ],
        'requirements': [
            ask('Describe your idea in 2 or 3 sentences and say who will use it.'),
            ask('What is the one workflow the first version must do? For example, a customer books a free time slot.'),
            ask('Do users need to log in?', 'Multiple choice',
                ['Yes, one type of user', 'Yes, several roles (for example admin and customer)', 'No login needed']),
            ask('Do you have a design or wireframe?', 'Multiple choice',
                ['Yes, I will attach it', 'Only rough notes', 'No, please suggest one']),
            ask('What is your deadline, and which tools or systems must it connect to?'),
            ask('Attach any notes, sketches or examples of apps you like (optional).', 'Attachment'),
        ],
        'faqs': [
            ('Can you build a custom web app from my idea?',
             'Yes. We pick one core workflow first, such as a customer booking a slot, and build a working first '
             'version with a demo each week.'),
            ('Which technology do you use?',
             'Python with Django or FastAPI, PostgreSQL or Supabase and REST APIs. If a React or Next.js front end is '
             'needed, we build it with AI-assisted coding and test it.'),
            ('Will I receive the source code?',
             'Yes, and you own it after final payment. You also get a plain-language document that explains how to run it.'),
            ('Do you build mobile apps or take online payments?',
             'Not yet. We focus on web apps with login, database, dashboards and APIs. Online payments and mobile apps '
             'are not included.'),
        ],
    },
    GIG_C: {
        'summary': (
            'We clean your data, build a simple baseline first, then a stronger model, and show you honestly which '
            'one works better. Text and intent classification, such as sorting messages by topic or urgency; sales or '
            'demand forecasts from CSV or Excel history; a results report with the error stated next to the baseline; '
            'and a FastAPI endpoint so other tools can use the model. Built with Python, Pandas, scikit-learn, XGBoost '
            'and CatBoost. No model is right every time, and we show where it fails.'),
        'packages': [
            pkg('Basic', 'Clean Data and Baseline',
                'Data cleaning, EDA and one baseline model with a short results report.',
                90, 3, 1, ['Data cleaning', 'EDA with charts', 'One baseline model', 'Short results report', 'Source code']),
            pkg('Standard', 'Tuned Model and Report',
                'Text classifier or forecast, tuned and compared with a baseline, with a full report.',
                120, 6, 2, ['Everything in Basic', 'Feature engineering', 'Tuned NLP or forecasting model',
                            'Error shown next to a baseline', 'Full report']),
            pkg('Premium', 'Model, API and Docs',
                'Tuned model served by a FastAPI endpoint, with charts, source code and handover documents.',
                260, 10, 3, ['Everything in Standard', 'FastAPI endpoint', 'Charts', 'Handover documents',
                             'LLM fine-tuning discussed on request']),
        ],
        'extras': [
            extra('Faster delivery', 20, 2, 'Basic package in 2 days'),
            extra('Faster delivery', 30, 4, 'Standard package in 4 days'),
            extra('Faster delivery', 50, 6, 'Premium package in 6 days'),
            extra('API integration', 60, 2),
            extra('Cloud deployment', 40, 1),
            extra('Model documentation', 30, 3),
            extra('Fine tuning', 25, 1),
            extra('Performance monitoring', 15, 0),
            extra('Additional revision', 15, 0),
        ],
        'requirements': [
            ask("What do you want to predict or sort? For example, label support messages by urgency, or forecast "
                "next month's sales."),
            ask('What kind of data do you have?', 'Multiple choice',
                ['Text messages, tickets or reviews', 'Sales or stock history', 'A spreadsheet with mixed columns', 'Not sure']),
            ask('Roughly how many rows or messages do you have?', 'Multiple choice',
                ['Under 1,000', '1,000 to 10,000', 'Over 10,000', 'Not sure']),
            ask('What do you need delivered?', 'Multiple choice', ['A report only', 'A report and an API', 'Not sure']),
            ask('What result would make this worthwhile? For example, hours saved a week or a forecast error you can live with.'),
            ask('Attach a small sample file (CSV or Excel). Please remove personal data first.', 'Attachment'),
        ],
        'faqs': [
            ('What can your NLP and ML models do?',
             'Text and intent classification, sorting messages by topic or urgency, and sales or demand forecasts from '
             'CSV or Excel history.'),
            ('How accurate will the model be?',
             'We show its error next to a simple baseline, including when it does not beat it. No model is right every '
             'time, so we also show where it fails.'),
            ('What data do I need to share?',
             'A CSV or Excel file, or text exported from your tools. A small sample is enough to start. Please remove '
             'personal data you do not want us to see.'),
            ('Can you fine-tune an LLM or give me an API?',
             'LLM fine-tuning is available on request when it suits your task. The Premium package includes a FastAPI '
             'endpoint so other tools can use the model.'),
        ],
    },
    GIG_D: {
        'summary': (
            'If your team copies numbers, renames files or builds the same report every week, we write a Python '
            'program that does it. It asks before anything risky and keeps a log of what it did. Scripts for one '
            'repeat task, Excel and CSV processing with charts and reports, file organizing tools, and Windows desktop '
            'tools with an action log and undo for file moves. Built with Python, Pandas, Matplotlib and SQL. '
            'Not included: mobile apps, phone-call bots and online payments.'),
        'packages': [
            pkg('Basic', 'Script for One Task',
                'One Python script that automates a single repeat task, with source code and usage notes.',
                50, 3, 1, ['One script for one task', 'Source code', 'Simple run instructions']),
            pkg('Standard', 'Automation and Report',
                'Excel or CSV automation with charts and a report, plus a log of every run.',
                130, 6, 2, ['Everything in Basic', 'Excel or CSV input', 'Charts and a report', 'Run log', 'Handover notes']),
            pkg('Premium', 'Windows Desktop Tool',
                'Windows tool with a simple window, action log, undo for file moves and full source code.',
                280, 10, 3, ['Everything in Standard', 'Simple desktop window', 'Action log', 'Undo for file moves',
                             'Optional AI summary step', 'Short walkthrough']),
        ],
        'extras': [
            extra('Faster delivery', 20, 2, 'Basic package in 2 days'),
            extra('Faster delivery', 30, 4, 'Standard package in 4 days'),
            extra('Faster delivery', 50, 6, 'Premium package in 6 days'),
            extra('Excel report, charts', 80, 3, 'Excel or CSV input with charts, a report and a log of every run.'),
            extra('Design customization', 60, 2),
            extra('Detailed code comments', 50, 1),
            extra('Responsive design', 40, 1),
            extra('Additional revision', 15, 0),
        ],
        'requirements': [
            ask('Which repeat task should the program do? Describe the steps you do by hand today.'),
            ask('What does the task work with?', 'Multiple choice',
                ['Excel or CSV files', 'Folders and file names', 'PDFs or documents', 'Something else']),
            ask('Where will the program run?', 'Multiple choice', ['Windows PC', 'Mac or Linux', 'On a server', 'Not sure']),
            ask('How many hours a week does this task take now? One rough number is enough.'),
            ask('Attach a sample file or a screenshot of the task. Please remove private data first.', 'Attachment'),
        ],
        'faqs': [
            ("How will I run the program if I don't know Python?",
             'We give you simple step-by-step instructions. For the Premium package we build a Windows desktop tool '
             'with a window, so you can click to run it.'),
            ('Do I get the source code?',
             'Yes. Full source code and plain-language notes are included, and you own the finished tool after final payment.'),
            ('Will it change my files without asking?',
             'No. Risky steps ask first, every run is logged, and file moves can be undone in the Premium desktop tool.'),
            ('Does it run on Mac?',
             'The desktop tool is built for Windows. Scripts can run on other systems if Python is installed.'),
        ],
    },
}


# Services with no Fiverr gig keep their packages on the service itself (Solution.packages).
# AI integration and support: written 2 Nov 2026 to sit between Gigs A and B on price and scope.
SERVICES = {
    'ai-integration-support': {
        'summary': (
            'We add AI to the Python app or website you already have, and keep it running. We review your app, '
            'connect an LLM where it helps, add fallback across AI providers and rate limits so it keeps answering, '
            'put automated tests around it, and fix what breaks live. Built with Python, Django or FastAPI, '
            'LangChain and PostgreSQL. We work on Python apps only, and we review the code before we agree a price.'),
        'packages': [
            pkg('Basic', 'Add One AI Feature',
                'One LLM API connected to one place in your existing Python app, with keys kept out of the code.',
                70, 4, 1, ['Review of your existing app', 'One LLM API connection (Gemini, OpenRouter or Groq)',
                           'API keys kept out of the code', 'Code changes and short notes']),
            pkg('Standard', 'AI with Fallback and Tests',
                'One AI feature with fallback across 3 providers, rate limits and automated tests around it.',
                160, 7, 2, ['Everything in Basic', 'Fallback across 3 AI providers', 'Rate limiting',
                            'Automated tests around the AI feature', 'Handover notes']),
            pkg('Premium', 'Production Fix and Support',
                'Fallback, tests and encrypted keys, plus debugging of live errors and deployment help.',
                290, 12, 3, ['Everything in Standard', 'Debugging of live errors in your app', 'Encrypted API keys',
                             'Deployment help', 'Handover walkthrough']),
        ],
        'extras': [
            extra('Faster delivery', 20, 3, 'Basic package in 3 days'),
            extra('Faster delivery', 30, 5, 'Standard package in 5 days'),
            extra('Faster delivery', 50, 9, 'Premium package in 9 days'),
            extra('LangChain workflow', 70, 3, 'A multi-step LangChain workflow, such as look up, then answer.'),
            extra('Extra AI provider', 30, 1, 'One more provider added to the fallback chain.'),
            extra('Detailed code comments', 50, 1),
            extra('Additional revision', 15, 0),
        ],
        'requirements': [
            ask('What does your app do today, and where should AI help? For example, draft replies in the support inbox.'),
            ask('What is your app built with?', 'Multiple choice',
                ['Django', 'FastAPI', 'Other Python', 'Not Python or not sure']),
            ask('Where does it run now?', 'Multiple choice',
                ['Vercel', 'Render or a similar host', 'My own server', 'Not live yet']),
            ask('What goes wrong today, if anything? For example, the AI stops answering or errors appear only live.'),
            ask('Share read access to your code or attach the files involved. Remove keys and passwords first.',
                'Attachment'),
        ],
        'faqs': [
            ('Can you work on an app someone else built?',
             'Yes, if it is a Python app (Django or FastAPI). We review the code first and tell you what we can and '
             'cannot change before you pay.'),
            ('What happens if an AI provider goes down?',
             'The feature switches to the next provider in the chain, so it keeps answering. Standard and Premium '
             'include fallback across 3 providers.'),
            ('Do you need my API keys?',
             'The AI runs on your own provider accounts. Keys are kept in environment settings or encrypted, never in '
             'the code. Please do not send keys in chat.'),
            ('Do you offer ongoing support?',
             'Premium includes debugging of live errors found during the work. Longer support is agreed separately.'),
        ],
    },
}


def apply_services(Solution, FAQ, only_empty=False):
    """Fill packages for services with no Fiverr gig and add their FAQs. only_empty keeps admin edits."""
    for slug, data in SERVICES.items():
        solution = Solution.objects.filter(slug=slug).first()
        if not solution or (only_empty and solution.packages):
            continue
        solution.package_summary = data['summary']
        solution.packages = data['packages']
        solution.extras = data['extras']
        solution.requirements = data['requirements']
        solution.save(update_fields=['package_summary', 'packages', 'extras', 'requirements'])
        for order, (question, answer) in enumerate(data['faqs'], 1):
            FAQ.objects.update_or_create(
                question=question, solution_slug=slug,
                defaults={'answer': answer, 'page': 'solution', 'order': order, 'published': True})


def apply(FiverrGig, FAQ, only_empty=False):
    """Fill each gig's details and add its FAQs to its service page. Safe to run again: FAQs are matched by question.
    only_empty skips gigs that already have packages, so edits made in the admin are kept."""
    for url, data in GIGS.items():
        gig = FiverrGig.objects.filter(url=url).first()
        if not gig or (only_empty and gig.packages):
            continue
        gig.summary = data['summary']
        gig.packages = data['packages']
        gig.extras = data['extras']
        gig.requirements = data['requirements']
        gig.save(update_fields=['summary', 'packages', 'extras', 'requirements'])
        for slug in gig.services.values_list('slug', flat=True):
            for order, (question, answer) in enumerate(data['faqs'], 1):
                FAQ.objects.update_or_create(
                    question=question, solution_slug=slug,
                    defaults={'answer': answer, 'page': 'solution', 'order': order, 'published': True})
