"""
What Hero's AI is told for each project: its role, its sample data (context) and the reply format.

Context comes from Pinecone (RAG): only the chunks most relevant to the question are sent to the AI.
The chunks are uploaded from datasets/<project>/ with `python manage.py rag_ingest` (see apps/tryit/rag.py).
If Pinecone is unreachable or a namespace is empty, the whole data file is used instead, so nothing breaks.
PageMind does not use RAG: a page is short, and summaries need the whole page.

Projects whose answers are numbers (InsightDesk, ForecastBoard, ReportBot) or bookings (BookIt)
are not answered by the AI alone: the numbers must be calculated in Python first. Until that
code exists they raise NotReady and the Try it page says the tool is busy.
"""
import csv
import re
from functools import lru_cache
from pathlib import Path

from . import rag, system_prompts as sp, trace

DATA_DIR = Path(__file__).resolve().parents[2] / 'datasets'

NEEDS_CALCULATION = {'insightdesk', 'forecastboard', 'reportbot', 'bookit'}

class NotReady(Exception):
    """This project needs calculation code before it can answer."""


class MissingInput(ValueError):
    """The visitor left out something this project needs. The message is safe to show."""


@lru_cache(maxsize=None)
def load(name):
    return (DATA_DIR / name).read_text(encoding='utf-8')


@lru_cache(maxsize=None)
def ticket_examples():
    """One labelled example ticket per topic and urgency, to show the model the expected style."""
    seen, blocks = set(), []
    with open(DATA_DIR / 'supportflow' / 'tickets.csv', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            key = (row['topic'], row['urgency'])
            if key in seen:
                continue
            seen.add(key)
            blocks.append(f"Message: {row['message']}\nTopic: {row['topic']} | Urgency: {row['urgency']}\n"
                          f"Reply: {row['agent_reply']}")
    return '\n\n'.join(blocks)


def wrap(data, message):
    """The user message: reference data and the visitor's text, clearly fenced as untrusted."""
    return f'<data>\n{data}\n</data>\n\n<input>\n{message}\n</input>'


def documind(p):
    message = p.get('message', '')
    if p.get('document'):
        trace.show('   Using the text the visitor pasted (no search needed)')
        system = sp.DOCUMIND.format(source_note=' (text the visitor pasted)', source_label='Your pasted text')
        return system, wrap(p['document'], message), 0.1
    sections = rag.context('documind', message, lambda: load('documind/staff_handbook.md'))
    system = sp.DOCUMIND.format(source_note=' (sections of the Northwind Supplies staff handbook)',
                                source_label='Staff handbook, section <number and title>')
    return system, wrap(sections, message), 0.1


def shopassist(p):
    message = p.get('message', '')
    products = rag.context('shopassist', message, lambda: load('shopassist/products.csv'))
    return sp.SHOPASSIST, wrap(products, message), 0.2


def supportflow(p):
    message = p.get('message', '')
    policy = rag.context('supportflow', message, lambda: load('supportflow/support_policy.md'))
    examples = rag.context('supportflow-tickets', message, ticket_examples)
    context = f'# Store policy (relevant parts)\n{policy}\n\n# Similar past tickets\n{examples}'
    return sp.SUPPORTFLOW, wrap(context, message), 0.3


def voicedesk(p):
    message = p.get('message', '')
    context = rag.context('voicedesk', message,
                          lambda: f'{load("voicedesk/clinic_faq.md")}\n\n# Services and fees (CSV)\n{load("voicedesk/services.csv")}')
    return sp.VOICEDESK, wrap(context, message), 0.2


def pagemind(p):
    question = p.get('message') or 'Summarise this page.'
    page = p.get('page_text') or (load(f"pagemind/{p['sample']}.md") if p.get('sample') else '')
    if not page:
        raise MissingInput('Please pick a sample page or paste some page text.')
    return sp.PAGEMIND, wrap(page, question), 0.2


def deskpilot(p):
    message = p.get('message', '')
    sops = rag.context('deskpilot', message, lambda: load('deskpilot/office_sops.md'))
    return sp.DESKPILOT, wrap(sops, message), 0.2


BUILDERS = {
    'documind': documind,
    'shopassist': shopassist,
    'supportflow': supportflow,
    'voicedesk': voicedesk,
    'pagemind': pagemind,
    'deskpilot': deskpilot,
}


def build_messages(slug, payload):
    """Return (messages, temperature) for a project. Raises NotReady for calculation projects."""
    if slug in NEEDS_CALCULATION or slug not in BUILDERS:
        raise NotReady(slug)
    system, user, temperature = BUILDERS[slug](payload)
    return [
        {'role': 'system', 'content': f'{system}\n\n{sp.SECURITY}\n\n{sp.JSON_ONLY}'},
        {'role': 'user', 'content': user},
    ], temperature


# ---------------------------------------------------------------------------
# Output guards: checks on the AI's reply before it reaches the page
# ---------------------------------------------------------------------------
TOPICS = ('Returns', 'Delivery', 'Payment', 'Account', 'Product question', 'Other')
URGENCY = ('Urgent', 'Normal', 'Low')
DRAFT_NOTE = '[Draft: a person checks this before it is sent]'
RISKY_TOOLS = ('rename_file', 'move_file', 'copy_file', 'create_folder', 'draft_email', 'make_spreadsheet')
# A step is unsafe when its action starts with one of these verbs (\"do not delete ...\" is fine)
FORBIDDEN = re.compile(r'^\s*(delete|remove|erase|format|wipe|uninstall|install|overwrite|empty)\b'
                       r'|\b(registry|password)\b', re.I)


@lru_cache(maxsize=None)
def catalog_names():
    with open(DATA_DIR / 'shopassist' / 'products.csv', encoding='utf-8') as f:
        return {row['name'].strip().lower(): row for row in csv.DictReader(f)}


def guard_shopassist(reply):
    """Drop recommendations that are not real catalog products or are out of stock."""
    kept, dropped = [], 0
    for item in reply.get('items') or []:
        row = catalog_names().get(str(item.get('title', '')).strip().lower())
        if row and row['availability'] != 'Out of stock':
            kept.append({'title': row['name'],
                         'meta': f"{float(row['price_usd']):.2f} USD | rating {row['rating']} | {row['availability']}"})
        else:
            dropped += 1
    if dropped:
        trace.show(f'   Guard: removed {dropped} recommendation(s) not available in the catalog')
    reply['items'] = kept[:4]
    if not kept and 'text' not in reply:
        reply['text'] = 'I could not find a matching product in the catalog. Try describing it another way.'
    return reply


def guard_supportflow(reply):
    """Exactly one valid topic and one valid urgency; the draft note is always present."""
    labels = [str(x).strip() for x in reply.get('labels') or []]
    topic = next((t for t in TOPICS if any(t.lower() == l.lower() for l in labels)), 'Other')
    urgency = next((u for u in URGENCY if any(u.lower() == l.lower() for l in labels)), 'Normal')
    reply['labels'] = [topic, urgency]
    text = str(reply.get('text', '')).strip()
    if DRAFT_NOTE not in text:
        text = f'{text}\n\n{DRAFT_NOTE}'.strip()
    reply['text'] = text
    return reply


def guard_deskpilot(reply):
    """Every step uses an allowed tool, risky steps always ask first, forbidden actions never appear."""
    steps = []
    for step in reply.get('steps') or []:
        text = str(step.get('text', '')).strip() if isinstance(step, dict) else str(step).strip()
        tool, _, action = (part.strip() for part in text.partition(':'))
        tool = tool.lower()
        if tool not in sp.DESKPILOT_TOOLS or FORBIDDEN.search(action):
            trace.show(f'   Guard: removed a step that is not allowed: {text[:60]}')
            continue
        steps.append({'text': text, 'needs_approval': tool in RISKY_TOOLS or bool(step.get('needs_approval'))})
    reply['steps'] = steps
    note = 'This is a plan; nothing has been run.'
    if not str(reply.get('text', '')).startswith(note):
        reply['text'] = f"{note} {reply.get('text', '')}".strip()
    return reply


GUARDS = {
    'shopassist': guard_shopassist,
    'supportflow': guard_supportflow,
    'deskpilot': guard_deskpilot,
}


def guard(slug, reply):
    return GUARDS[slug](reply) if slug in GUARDS else reply
