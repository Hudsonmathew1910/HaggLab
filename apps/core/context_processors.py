from django.conf import settings

from apps.content.models import SiteSetting, Solution, Project
from apps.core.fiverr import fiverr_contact_url, fiverr_enabled

FIVERR_FALLBACK_URL = 'https://www.fiverr.com/'


def studio_context(request):
    """
    Expose studio name and non-sensitive configuration to templates globally.
    Never exposes secrets, owner email to Fiverr visitors, or unvalidated data.

    SITE holds only the Site Settings that have a value, so templates can write
    {% if SITE.reply_time %} and an empty setting keeps its block hidden.
    """
    fiverr_on = fiverr_enabled()
    is_fiverr = fiverr_on and (getattr(request, 'is_fiverr', False) or request.session.get('is_fiverr', False))

    site = {
        key: value.strip()
        for key, value in SiteSetting.objects.exclude(value='').values_list('key', 'value')
        if value.strip()
    }

    return {
        'STUDIO_NAME': getattr(settings, 'STUDIO_NAME', 'HaggLab'),
        'SITE_URL': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        'TURNSTILE_SITE_KEY': getattr(settings, 'TURNSTILE_SITE_KEY', ''),
        'IS_FIVERR': is_fiverr,
        # Admin switch: when off, no Fiverr link, gig button or Fiverr page is shown anywhere
        'FIVERR_ON': fiverr_on,
        # Only expose owner email if NOT a Fiverr visitor
        'OWNER_EMAIL': '' if is_fiverr else getattr(settings, 'OWNER_EMAIL', ''),
        'SITE': site,
        # Fiverr profile link from the admin; falls back to Fiverr's home page until it is set
        'FIVERR_URL': fiverr_contact_url() if fiverr_on else FIVERR_FALLBACK_URL,
        # Navigation and footer lists come from the content models, never hard-coded
        'NAV_SOLUTIONS': Solution.objects.filter(published=True).order_by('order'),
        'NAV_PROJECTS': Project.objects.public().order_by('order'),
    }
