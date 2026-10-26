"""
Fiverr gig button labels for each project. The gig links themselves live in the admin under
Content > Fiverr gigs: one entry per gig, with every project it covers ticked.
"""
from .models import FiverrGig

GIGS = {
    'documind': ('A document assistant', 'Get a document assistant built'),
    'insightdesk': ('A data dashboard', 'Get a data dashboard built'),
    'shopassist': ('An AI shopping assistant', 'Add an AI shopping assistant'),
    'bookit': ('A booking website', 'Get a booking website built'),
    'supportflow': ('A support triage tool', 'Get a support triage tool built'),
    'forecastboard': ('A prediction model', 'Get a prediction model built'),
    'voicedesk': ('A voice assistant', 'Get a voice assistant built'),
    'pagemind': ('A Chrome extension', 'Get a browser extension built'),
    'deskpilot': ('A desktop or automation tool', 'Get a desktop tool built'),
    'reportbot': ('Automated reports', 'Automate my reports'),
}


def gig_for(project):
    """Return {'name', 'button', 'url'} for a project's Fiverr gig. url is '' until set."""
    name, button = GIGS.get(project.slug, (project.title, 'Order on Fiverr'))
    gig = FiverrGig.objects.filter(active=True, projects=project).order_by('order', 'id').first()
    return {'name': gig.title if gig else name, 'button': button, 'url': gig.url if gig else ''}
