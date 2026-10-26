"""
Fiverr on the site follows the gig links you enter in the admin.

Admin:
  Content > Fiverr gigs                  one entry per gig: its title, its link, and the projects it covers
  Site settings > fiverr_profile_url     optional; used for "Message us on Fiverr" (falls back to the first gig)
  Site settings > fiverr_enabled         "auto" (default): Fiverr appears once at least one gig link is set, and each project
                         or service shows a Fiverr button only if it has its own gig.
                         "off": hide Fiverr everywhere.  "on": show the general Fiverr links even without gigs.
"""
from apps.content.models import FiverrGig, SiteSetting

# FAQ answers to use while Fiverr is off; other FAQs that mention Fiverr are hidden
ANSWERS_WITHOUT_FIVERR = {
    'How do I order?': ('Use the Start a project form. Describe the problem in a few sentences and we reply with '
                        'what is possible and a one-page scope before any work starts.'),
}


def _settings(prefix='fiverr_'):
    return {key: value.strip() for key, value in
            SiteSetting.objects.filter(key__startswith=prefix).values_list('key', 'value') if value.strip()}


def gig_links():
    """{project_slug: gig url} for every project covered by an active gig (the first gig wins)."""
    links = {}
    for gig in FiverrGig.objects.filter(active=True).prefetch_related('projects').order_by('order', 'id'):
        for project in gig.projects.all():
            links.setdefault(project.slug, gig.url)
    return links


def fiverr_mode():
    value = _settings().get('fiverr_enabled', 'auto').lower()
    if value in {'off', 'no', 'false', '0'}:
        return 'off'
    if value in {'on', 'yes', 'true', '1'}:
        return 'on'
    return 'auto'


def fiverr_enabled():
    """True when the site should show Fiverr at all."""
    mode = fiverr_mode()
    return mode == 'on' or (mode == 'auto' and bool(gig_links()))


def fiverr_contact_url():
    """Where "Message us on Fiverr" goes: the profile, else the first gig, else Fiverr's home page."""
    settings = _settings()
    if settings.get('fiverr_profile_url'):
        return settings['fiverr_profile_url']
    first = FiverrGig.objects.filter(active=True).order_by('order', 'id').first()
    return first.url if first else 'https://www.fiverr.com/'


def faqs_for_site(faqs):
    """The FAQ list as visitors should see it: unchanged when Fiverr is on, Fiverr-free when it is off."""
    faqs = list(faqs)
    if fiverr_enabled():
        return faqs
    shown = []
    for faq in faqs:
        if faq.question in ANSWERS_WITHOUT_FIVERR:
            faq.answer = ANSWERS_WITHOUT_FIVERR[faq.question]
        elif 'fiverr' in f'{faq.question} {faq.answer}'.lower():
            continue
        shown.append(faq)
    return shown
