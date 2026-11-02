"""
Packages and extras a visitor can pick on /start, read from each service's active Fiverr gig
(admin: Fiverr gigs). Prices are in US dollars; a rupee estimate is added when the inr_rate setting is set.
"""
from apps.content.models import FiverrGig, SiteSetting, Solution

# Inquiry.service code -> service page (Solution) slug
SERVICE_SLUGS = {
    'ai_chatbots': 'ai-chatbots-rag-assistants',
    'saas_mvp': 'saas-mvps-ai-web-apps',
    'nlp_ml': 'nlp-machine-learning-models',
    'python_automation': 'python-programs-automation',
    'ai_integration': 'ai-integration-support',
}
SLUG_SERVICES = {slug: code for code, slug in SERVICE_SLUGS.items()}


def inr_rate():
    """Rupees per US dollar from the inr_rate setting, or None when it is empty or not a number."""
    value = SiteSetting.objects.filter(key='inr_rate').values_list('value', flat=True).first() or ''
    try:
        rate = float(value.strip().replace(',', ''))
    except ValueError:
        return None
    return rate if rate > 0 else None


def inr_text(usd, rate):
    """'≈ ₹5,700' (rounded to the nearest ₹100), or '' when there is no rate."""
    if not rate:
        return ''
    try:
        rupees = int(float(usd) * rate / 100.0 + 0.5) * 100  # half up: 14,250 -> 14,300
    except (TypeError, ValueError):
        return ''
    return f'≈ ₹{rupees:,}'


def money(usd, rate):
    inr = inr_text(usd, rate)
    return f'${usd} {inr}' if inr else f'${usd}'


def offer_for(solution):
    """The packages shown for a service: from its active Fiverr gig when that has packages (so the site and Fiverr
    match), otherwise from the service itself. None when there are none."""
    for gig in FiverrGig.objects.filter(active=True, services=solution).order_by('order', 'id'):
        if gig.packages:
            return {'summary': gig.summary, 'packages': gig.packages, 'extras': gig.extras or [],
                    'requirements': gig.requirements or [], 'gig': gig}
    if solution.packages:
        return {'summary': solution.package_summary, 'packages': solution.packages, 'extras': solution.extras or [],
                'requirements': solution.requirements or [], 'gig': None}
    return None


def lead_service_for_project(project):
    """The /start service code for a project page: its first service."""
    for solution in project.solutions.order_by('order'):
        if solution.slug in SLUG_SERVICES:
            return SLUG_SERVICES[solution.slug]
    return ''


def offers():
    """One entry per service with packages, in the order of the service list, for the /start form."""
    rate = inr_rate()
    by_code = {}
    for solution in Solution.objects.filter(published=True, slug__in=SLUG_SERVICES):
        offer = offer_for(solution)
        if not offer:
            continue
        code = SLUG_SERVICES[solution.slug]
        packages = [dict(p, value=f'{code}|{p.get("tier", "")}', inr=inr_text(p.get('price'), rate),
                         label=f'{p.get("tier")}: {p.get("title")} ({money(p.get("price"), rate)})')
                    for p in offer['packages']]
        extras = []
        for i, e in enumerate(offer['extras']):
            if e.get('name') == 'Faster delivery':  # its description already says the new delivery time
                name, when = f'Faster delivery: {e.get("desc") or e.get("days")}', ''
            else:
                days = e.get('days')
                name, when = e.get('name'), (f', +{days} day' + ('' if days == 1 else 's') if days else ', no extra time')
            extras.append({'value': f'{code}|{i}', 'price': e.get('price', 0),
                           'label': f'{name} (+{money(e.get("price"), rate)}{when})'})
        by_code[code] = {'code': code, 'name': solution.title, 'packages': packages, 'extras': extras,
                         'requirements': offer['requirements']}
    return [by_code[c] for c in SERVICE_SLUGS if c in by_code]
