"""
What each project's Try it page accepts. The API refuses any field not listed here,
and trims text to its max length, before anything is sent to Hero's AI.

kind:   which interface to use (templates/tryit/<kind>.html)
fields: name -> (type, max length, allowed choices, or (min, max))
"""
from datetime import date

TEXT, CHOICE, DATE, INT = 'text', 'choice', 'date', 'int'

SAMPLE_DATASETS = [
    ('retail-sales', 'Retail shop sales (Apr 2025 - Sep 2026)'),
    ('cafe-orders', 'Cafe chain orders (Oct 2025 - Sep 2026)'),
]
CATEGORIES = [('all', 'All categories'), ('Audio', 'Audio'), ('Computer Accessories', 'Computer accessories'),
              ('Office Furniture', 'Office furniture'), ('Apparel', 'Apparel'), ('Home & Kitchen', 'Home and kitchen'),
              ('Fitness', 'Fitness')]
COURTS = [('turf-a', 'Turf A (5-a-side)'), ('turf-b', 'Turf B (5-a-side)'), ('turf-c', 'Turf C (7-a-side)'),
          ('badminton-1', 'Badminton Court 1'), ('badminton-2', 'Badminton Court 2')]
SAMPLE_PAGES = [
    ('remote_work_policy_update', 'News: a company updates its hybrid work policy'),
    ('small_business_ai_guide', 'Blog: five places a small business can use AI'),
    ('product_launch_announcement', 'Press release: same-day delivery launch'),
]
PERIODS = [('last-week', 'Last week'), ('last-month', 'Last month'), ('last-quarter', 'Last quarter')]

SPECS = {
    'documind': {
        'examples': ['How many days of annual leave do I get?', 'Can I carry over unused leave?', 'What is the daily meal allowance when travelling?'],
        'kind': 'chat',
        'intro': 'Ask a question about the staff handbook of Northwind Supplies, a sample company, or paste your own text and ask about it.',
        'placeholder': 'How many days of annual leave do staff get?',
        'fields': {'message': (TEXT, 600), 'document': (TEXT, 8000)},
        'with_document': True,
    },
    'insightdesk': {
        'examples': ['Which region sold the most in Q3?', 'Which product gives us a loss?', 'What were the top 5 products by revenue last month?'],
        'kind': 'data',
        'intro': 'Pick a sample dataset and ask a question in plain English. You get the answer, the numbers and the code that calculated them.',
        'placeholder': 'Which region sold the most in Q3?',
        'fields': {'dataset': (CHOICE, SAMPLE_DATASETS), 'message': (TEXT, 400)},
    },
    'shopassist': {
        'examples': ['Noise-cancelling headphones under $150', 'A waterproof jacket for hiking', 'A gift for someone who works from home'],
        'kind': 'chat',
        'intro': 'Tell the shopping assistant what you are looking for in the sample store.',
        'placeholder': 'Noise-cancelling headphones for my home office, under $150',
        'fields': {'message': (TEXT, 400)},
    },
    'bookit': {
        'kind': 'booking',
        'intro': 'Pick a court and a date at Green Field Sports Arena, a sample venue, to see free slots. Then book one.',
        'fields': {'action': (CHOICE, [('slots', ''), ('book', '')]), 'resource': (CHOICE, COURTS), 'date': (DATE, None),
                   'slot': (TEXT, 20), 'name': (TEXT, 80)},
    },
    'supportflow': {
        'examples': ['My order arrived broken and I need it before Friday.', 'You charged my card twice for order 55012!', 'How do I change the email on my account?'],
        'kind': 'triage',
        'intro': 'Paste a customer message. The tool labels its topic and urgency and drafts a reply for a person to approve.',
        'placeholder': 'Hi, my order arrived broken and I need it replaced before Friday.',
        'fields': {'message': (TEXT, 2000)},
    },
    'forecastboard': {
        'kind': 'forecast',
        'intro': 'Pick a product category and how many weeks ahead to forecast. The forecast is tested on recent weeks and shows its error.',
        'fields': {'category': (CHOICE, CATEGORIES), 'weeks': (INT, (1, 12))},
    },
    'voicedesk': {
        'examples': ['Are you open on Saturday morning?', 'How much is a cholesterol test?', 'How do I book a vaccination?'],
        'kind': 'chat',
        'intro': 'Ask the sample clinic assistant a question, as a visitor would after hours.',
        'placeholder': 'Are you open on Saturday morning?',
        'fields': {'message': (TEXT, 400)},
    },
    'pagemind': {
        'examples': ['Summarise this page in 3 points', 'What does it cost?', 'When does it start?'],
        'kind': 'page',
        'intro': 'Pick a sample page or paste the text of any web page, then ask for a summary or a question about it.',
        'placeholder': 'Summarise this page in 3 points',
        'fields': {'sample': (CHOICE, SAMPLE_PAGES), 'page_text': (TEXT, 12000), 'message': (TEXT, 400)},
    },
    'deskpilot': {
        'examples': ['Rename every invoice PDF by its date', 'File the supplier invoices that arrived today', 'Make a list of all contracts signed this month'],
        'kind': 'task',
        'intro': 'Describe a repeat computer task. The tool shows the steps it would take and which ones need your approval.',
        'placeholder': 'Rename every invoice PDF in my folder by its date',
        'fields': {'message': (TEXT, 600)},
    },
    'reportbot': {
        'kind': 'report',
        'intro': 'Pick a sample business and a period. The numbers are calculated from the data; the summary is written by AI.',
        'fields': {'dataset': (CHOICE, SAMPLE_DATASETS), 'period': (CHOICE, PERIODS)},
    },
}


class InvalidInput(ValueError):
    """Bad visitor input. The message is safe to show on the page."""


def clean_payload(slug, data):
    """Keep only allowed fields and check types and limits."""
    spec = SPECS.get(slug)
    if not spec:
        raise InvalidInput('This tool is not available.')
    clean = {}
    for name, (ftype, rule) in spec['fields'].items():
        value = data.get(name)
        if value in (None, ''):
            continue
        if ftype == TEXT:
            text = str(value).strip()[:rule]
            if text:
                clean[name] = text
        elif ftype == CHOICE:
            if value not in [key for key, _ in rule]:
                raise InvalidInput('Please pick one of the listed options.')
            clean[name] = value
        elif ftype == INT:
            try:
                number = int(value)
            except (TypeError, ValueError):
                raise InvalidInput('Please enter a whole number.')
            low, high = rule
            if not low <= number <= high:
                raise InvalidInput(f'Please pick a number from {low} to {high}.')
            clean[name] = number
        elif ftype == DATE:
            try:
                clean[name] = date.fromisoformat(str(value)).isoformat()
            except ValueError:
                raise InvalidInput('Please pick a valid date.')
    if not clean:
        raise InvalidInput('Please type something first.')
    return clean
