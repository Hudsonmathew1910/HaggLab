"""
Haggi's knowledge: the site's live content turned into short passages ("chunks"), each with a title and a link.

Nothing here is typed in by hand. Every passage is built from what the site shows right now:
- services, their packages, prices, extras and order questions (Solution + FiverrGig, via apps.leads.offers),
- projects (only the public ones), FAQs, the Heros product (apps.core.built),
- the About, Process, Security, Privacy and Terms pages (rendered from their templates, so a page edit counts too).

So a change in the admin (a new price, a project switched on, an FAQ edited) is what Haggi knows on the next
question. The built list is cached for CACHE_SECONDS and cleared at once when content is saved (signals.py).

    python manage.py assistant_knowledge          # list every passage Haggi can use
    python manage.py assistant_knowledge "price"  # show the passages a question would get
"""
import logging
import re
from html.parser import HTMLParser

from django.conf import settings
from django.core.cache import cache
from django.urls import reverse

logger = logging.getLogger(__name__)

CACHE_KEY = 'assistant:knowledge:v1'
CACHE_SECONDS = 1800         # a safety net: every content save clears it at once (signals.py)
MAX_CHUNK = 1400             # characters; longer page sections are split


def chunk(title, url, text, kind):
    text = re.sub(r'[ \t]+', ' ', text).strip()
    return {'title': title, 'url': url, 'text': text, 'kind': kind}


def money(usd, rate):
    from apps.leads.offers import money as fmt
    return fmt(usd, rate)


# ---------------------------------------------------------------- the company and its product
def company_chunks():
    from apps.content.models import SiteSetting
    from apps.core.built import all_products
    from apps.core.fiverr import fiverr_enabled

    studio = getattr(settings, 'STUDIO_NAME', 'HaggLab')
    site = {k: v.strip() for k, v in SiteSetting.objects.exclude(value='').values_list('key', 'value')}
    products = all_products()
    out = []

    lines = [
        f'{studio} is a software and AI studio. It builds working tools for small businesses and startups: '
        'AI chatbots and assistants, SaaS MVPs and web apps, NLP and machine learning models, Python programs and '
        'automation, and AI integration for existing apps. It fixes one business problem at a time, shows a working '
        'demo before you hire, gives a working demo every week during a build, and hands over the code.',
        'Visitors can try sample versions of the projects on the Try it pages before hiring.',
        f'How to start: describe the problem on the Start a project form ({reverse("start_project")}). '
        'Picking a service shows its packages and prices; the scope and price are agreed before any work starts.',
    ]
    if fiverr_enabled():
        lines.append(f'{studio} also takes orders on Fiverr, where chat, orders and payment stay on Fiverr '
                     f'(see {reverse("hire_fiverr")}).')
    if site.get('reply_time'):
        lines.append(f'Reply time to new messages: {site["reply_time"]}.')
    if site.get('support_window'):
        lines.append(f'Support after handover: {site["support_window"]}.')
    if site.get('code_ownership_terms'):
        lines.append(f'Code ownership: {site["code_ownership_terms"]}.')
    if site.get('nda_policy'):
        lines.append(f'NDA: {site["nda_policy"]}.')
    out.append(chunk(f'About {studio}', reverse('about'), ' '.join(lines), 'company'))

    if products:
        names = ', '.join(f'{p["name"]} ({p["kind"]}{", " + p["link"] if p["link"] else ""})' for p in products)
        out.append(chunk(
            'All our products', reverse('about') + '#built-title',
            f'{studio}\'s own products (built and run by the studio, not client work): {names}. '
            'Client projects are listed separately under Projects.', 'overview'))
    for p in products:
        features = '; '.join(f'{f["name"]} ({f["kind"]}): {f["desc"]}{" Link: " + f["link"] if f["link"] else ""}'
                             for f in p['features'])
        out.append(chunk(
            f'Product: {p["name"]}', p['link'] or reverse('about') + '#built-title',
            f'{p["name"]} is {studio}\'s own product: {p["kind"]}. {p["desc"]} '
            + (f'Live at {p["link"]}. ' if p['link'] else '')
            + (f'Features and apps inside {p["name"]}: {features}.' if features else ''), 'product'))
    return out


# ---------------------------------------------------------------- services, packages, prices
def service_chunks():
    from urllib.parse import urlencode

    from apps.content.models import Solution
    from apps.content.services import service_for
    from apps.core.fiverr import fiverr_enabled
    from apps.leads.offers import SLUG_SERVICES, inr_rate, offer_for

    rate = inr_rate()
    fiverr_on = fiverr_enabled()
    start = reverse('start_project')
    out, overview = [], []
    for s in Solution.objects.filter(published=True).order_by('order'):
        meta = service_for(s)
        url = reverse('solution_detail', args=[s.slug])
        code = SLUG_SERVICES.get(s.slug, '')
        start_url = f'{start}?service={code}' if code else start
        projects = ', '.join(f'{p.title} ({reverse("try_project", args=[p.slug])})'
                             for p in s.projects.public().order_by('order'))
        offer = offer_for(s)
        prices = sorted(p.get('price', 0) for p in offer['packages']) if offer else []
        overview.append(f'{meta["name"]}: {meta["desc"]}'
                        + (f' From {money(prices[0], rate)}.' if prices else '') + f' Page: {url}')
        out.append(chunk(
            f'Service: {meta["name"]}', url,
            f'{meta["name"]}: {meta["desc"]} Headline: {s.headline}. The problem: {s.problem} '
            f'How it is done today: {s.cost_today} The fix: 1) {s.step1_title}: {s.step1_desc} '
            f'2) {s.step2_title}: {s.step2_desc} 3) {s.step3_title}: {s.step3_desc} '
            f'Expected (not guaranteed): {s.expected_outcome} What we track: {s.metrics}. '
            + (f'Related projects you can try: {projects}. ' if projects else '')
            + f'Service page: {url}. Start a project for this service: {start_url}.', 'service'))

        if not offer:
            continue
        pkgs = []
        for p in offer['packages']:
            choose = f'{start}?' + urlencode({'service': code, 'package_choice': f'{code}|{p.get("tier", "")}'}) \
                if code else start
            pkgs.append(f'{p.get("tier")} "{p.get("title")}": {money(p.get("price"), rate)}, '
                        f'{p.get("days")} days delivery, {p.get("revisions")} revisions. {p.get("desc", "")} '
                        f'Includes: {"; ".join(p.get("included") or [])}. Choose it: {choose}.')
        gig = offer['gig']
        where = (f' Order through the Start a project form, or on Fiverr: {gig.url}' if gig and fiverr_on
                 else ' Order through the Start a project form.')
        out.append(chunk(
            f'Packages and prices: {meta["name"]}', url + '#pkg-title',
            f'{meta["name"]} packages (prices in US dollars{", rupees are estimates" if rate else ""}). '
            f'{offer["summary"]} ' + ' '.join(pkgs) + where, 'pricing'))

        if offer['extras']:
            extras = '; '.join(f'{e.get("name")}{": " + e["desc"] if e.get("desc") else ""} '
                               f'(+{money(e.get("price"), rate)}, {"+" + str(e["days"]) + " days" if e.get("days") else "no extra time"})'
                               for e in offer['extras'])
            out.append(chunk(f'Extras: {meta["name"]}', url + '#pkg-title',
                             f'Optional extras for {meta["name"]}: {extras}.', 'pricing'))
        if offer['requirements']:
            asks = '; '.join(q.get('question', '') + (f' ({q.get("kind")}: {", ".join(q["options"])})'
                                                       if q.get('options') else f' ({q.get("kind", "Free text")})')
                             for q in offer['requirements'])
            out.append(chunk(f'What we ask when you order: {meta["name"]}', start_url,
                             f'When you order {meta["name"]}, the Start a project form asks: {asks}', 'pricing'))
    if overview:
        out.insert(0, chunk('All our services', reverse('solutions_hub'),
                            f'{len(overview)} services. ' + ' | '.join(overview), 'overview'))
    return out


# ---------------------------------------------------------------- projects
def project_chunks():
    from apps.content.gigs import gig_for
    from apps.content.models import Project
    from apps.core.fiverr import fiverr_enabled
    from apps.leads.offers import inr_rate, offer_for

    rate = inr_rate()

    fiverr_on = fiverr_enabled()
    out, overview = [], []
    for p in Project.objects.public().order_by('order'):
        services = ', '.join(f'{s.title} ({reverse("solution_detail", args=[s.slug])})' for s in p.solutions.all())
        page, try_url = reverse('project_detail', args=[p.slug]), reverse('try_project', args=[p.slug])
        overview.append(f'{p.title} ({p.status}): {p.headline}. Try it: {try_url}')
        parts = [
            f'{p.title} ({p.status}): {p.headline}. The problem: {p.problem} How it is done today: {p.cost_today}',
            f'How it works: 1) {p.step1_title}: {p.step1_desc} 2) {p.step2_title}: {p.step2_desc} '
            f'3) {p.step3_title}: {p.step3_desc}',
        ]
        if p.built_for:
            parts.append(f'Suits: {p.built_for}.')
        if p.use_cases:
            parts.append('Examples: ' + '; '.join(line.strip() for line in p.use_cases.splitlines() if line.strip()) + '.')
        if p.expected_text:
            parts.append(f'Expected (not guaranteed): {p.expected_text}')
        if p.measured_text:
            parts.append(f'Measured in testing: {p.measured_text}')
        if p.inside_text:
            parts.append(f'What is inside: {p.inside_text}')
        priced = []
        for s in p.solutions.filter(published=True).order_by('order'):
            offer = offer_for(s)
            if offer and offer['packages']:
                prices = sorted(x.get('price', 0) for x in offer['packages'])
                priced.append(f'{s.title} packages, {money(prices[0], rate)} to {money(prices[-1], rate)} '
                              f'({reverse("solution_detail", args=[s.slug])}#pkg-title)')
        if priced:
            parts.append(f'Price: a tool like {p.title} for your business is built under the {"; ".join(priced)}. '
                         'The exact price depends on the scope, agreed before work starts.')
        parts.append(f'Service: {services}. Try it free with sample data ({p.demo_note}): {try_url}. '
                     f'How it works in detail: {page}.')
        gig = gig_for(p)
        if fiverr_on and gig['url']:
            parts.append(f'Order it on Fiverr ("{gig["button"]}"): {gig["url"]}')
        out.append(chunk(f'Project: {p.title}', try_url, ' '.join(parts), 'project'))
    if overview:
        out.insert(0, chunk('All our projects', reverse('projects_hub'),
                            f'{len(overview)} projects you can try for free with sample data. ' + ' | '.join(overview)
                            + ' Status meanings: Concept = designed, not built yet; Prototype = working demo; '
                              'Live demo = running publicly; Delivered = real client work.', 'overview'))
    return out


# ---------------------------------------------------------------- FAQs
def faq_chunks():
    from apps.content.models import FAQ
    from apps.core.fiverr import faqs_for_site

    out = []
    for f in faqs_for_site(FAQ.objects.filter(published=True).order_by('order')):
        url = reverse('solution_detail', args=[f.solution_slug]) if f.solution_slug else reverse('faq')
        out.append(chunk(f'FAQ: {f.question}', url, f'Q: {f.question} A: {f.answer}', 'faq'))
    return out


# ---------------------------------------------------------------- policy and info pages
class _MainText(HTMLParser):
    """Text of <main>, split into sections at each h2 (h1 starts the first one). Skips scripts, svg and forms."""
    SKIP = {'script', 'style', 'svg', 'form', 'nav', 'button'}

    def __init__(self):
        super().__init__()
        self.in_main = 0
        self.skip = 0
        self.heading = None
        self.sections = []  # [title, [text, ...]]

    def handle_starttag(self, tag, attrs):
        if tag == 'main':
            self.in_main += 1
        elif self.in_main and tag in self.SKIP:
            self.skip += 1
        elif self.in_main and not self.skip and tag in ('h1', 'h2'):
            self.heading = []
        elif self.in_main and tag in ('p', 'li', 'dd', 'dt', 'h3', 'tr', 'br'):
            if self.sections:
                self.sections[-1][1].append('\n')

    def handle_endtag(self, tag):
        if tag == 'main':
            self.in_main -= 1
        elif self.in_main and tag in self.SKIP and self.skip:
            self.skip -= 1
        elif self.heading is not None and tag in ('h1', 'h2'):
            self.sections.append([' '.join(''.join(self.heading).split()), []])
            self.heading = None

    def handle_data(self, data):
        if not self.in_main or self.skip:
            return
        if self.heading is not None:
            self.heading.append(data)
        elif self.sections:
            self.sections[-1][1].append(data)


PAGES = [  # (url name, title)
    ('about', 'About'),
    ('process', 'How a project works'),
    ('security_data', 'Security and data'),
    ('privacy_policy', 'Privacy policy'),
    ('terms_of_service', 'Terms of service'),
]


def render_page(url_name):
    """Render a page the way a first-time visitor sees it, without touching the database or analytics."""
    from django.contrib.auth.models import AnonymousUser
    from django.contrib.sessions.backends.signed_cookies import SessionStore
    from django.test import RequestFactory
    from django.urls import resolve

    path = reverse(url_name)
    request = RequestFactory().get(path)
    request.session = SessionStore()
    request.user = AnonymousUser()
    request.is_fiverr = False
    response = resolve(path).func(request)
    return response.content.decode('utf-8', errors='ignore')


def split_long(title, url, text, kind):
    if len(text) <= MAX_CHUNK:
        return [chunk(title, url, text, kind)]
    out, part = [], ''
    for para in [p.strip() for p in text.split('\n') if p.strip()]:
        if part and len(part) + len(para) > MAX_CHUNK:
            out.append(chunk(title, url, part, kind))
            part = ''
        part = f'{part} {para}'.strip()
    if part:
        out.append(chunk(title, url, part, kind))
    return out


def page_chunks():
    out = []
    for url_name, page_title in PAGES:
        try:
            html = render_page(url_name)
        except Exception:  # one broken page must not take Haggi down
            logger.exception('Haggi could not read the %s page', url_name)
            continue
        parser = _MainText()
        parser.feed(html)
        url = reverse(url_name)
        for heading, parts in parser.sections:
            text = re.sub(r'\s*\n\s*', '\n', ''.join(parts)).strip()
            if len(text) < 40 or heading.lower().startswith('tell us the problem'):
                continue  # too short, or the "Tell us the problem" sign-up box repeated on every page
            title = page_title if heading.lower() == page_title.lower() else f'{page_title}: {heading}'
            out.extend(split_long(title, url, text, 'page'))
    return out


# ---------------------------------------------------------------- site directory: every page and its link
def directory():
    """A compact list of every public page, sent with every question so Haggi can always link correctly."""
    from apps.content.models import Project, Solution
    from apps.content.services import service_for
    from apps.core.built import all_products
    from apps.core.fiverr import fiverr_enabled

    lines = [f'Home: {reverse("home")}', f'All services: {reverse("solutions_hub")}']
    lines += [f'- {service_for(s)["name"]}: {reverse("solution_detail", args=[s.slug])} '
              f'(packages and prices: {reverse("solution_detail", args=[s.slug])}#pkg-title)'
              for s in Solution.objects.filter(published=True).order_by('order')]
    lines.append(f'All projects: {reverse("projects_hub")}')
    lines += [f'- {p.title}: try it {reverse("try_project", args=[p.slug])}, details {reverse("project_detail", args=[p.slug])}'
              for p in Project.objects.public().order_by('order')]
    lines += [f'Product {p["name"]}: {p["link"] or reverse("about")}' for p in all_products()]
    lines += [f'Start a project (form, packages, prices): {reverse("start_project")}',
              f'How a project works: {reverse("process")}', f'About: {reverse("about")}',
              f'FAQ: {reverse("faq")}', f'Security and data: {reverse("security_data")}',
              f'Privacy policy: {reverse("privacy_policy")}', f'Terms of service: {reverse("terms_of_service")}']
    if fiverr_enabled():
        lines.append(f'Hire on Fiverr: {reverse("hire_fiverr")}')
    return '\n'.join(lines)


# ---------------------------------------------------------------- all of it
PAGE_SECONDS = 3600  # rendered pages only change when the site is deployed
_pages = {'built_at': -PAGE_SECONDS, 'chunks': []}


def cached_page_chunks():
    """The slowest source (it renders 5 pages), so it is kept for an hour instead of rebuilt on every admin save."""
    import time
    if time.monotonic() - _pages['built_at'] >= PAGE_SECONDS or not _pages['chunks']:
        _pages.update(built_at=time.monotonic(), chunks=page_chunks())
    return [dict(c) for c in _pages['chunks']]


SOURCES = [company_chunks, service_chunks, project_chunks, faq_chunks, cached_page_chunks]


def build():
    chunks = []
    for source in SOURCES:
        try:
            chunks.extend(source())
        except Exception:
            logger.exception('Haggi knowledge source %s failed', source.__name__)
    for i, c in enumerate(chunks):
        c['id'] = i
    return chunks


_memory = {'version': None, 'built_at': 0.0, 'chunks': [], 'directory': ''}


def current_version():
    """A number that changes whenever content is saved (signals.py calls clear()). Shared through the cache."""
    version = cache.get(CACHE_KEY)
    if version is None:
        version = 1
        cache.set(CACHE_KEY, version, None)
    return version


def get_chunks():
    """(version, passages). Built once and kept in memory until content changes or CACHE_SECONDS pass."""
    import time
    version = current_version()
    fresh = time.monotonic() - _memory['built_at'] < CACHE_SECONDS
    if _memory['version'] != version or not fresh:
        try:
            site_map = directory()
        except Exception:
            logger.exception('Haggi site directory failed')
            site_map = ''
        _memory.update(version=version, built_at=time.monotonic(), chunks=build(), directory=site_map)
    return version, _memory['chunks']


def get_directory():
    get_chunks()
    return _memory['directory']


def clear():
    """Called when content changes: every worker rebuilds on its next question."""
    try:
        cache.incr(CACHE_KEY)
    except ValueError:
        cache.set(CACHE_KEY, 2, None)
    _memory['version'] = None
