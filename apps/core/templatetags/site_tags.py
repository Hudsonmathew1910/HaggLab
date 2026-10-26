from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

from django import template

register = template.Library()


@register.filter
def utm(url, campaign='site'):
    """
    Add studio UTM tags to an outbound link, keeping any query it already has.
    Example: {{ FIVERR_URL|utm:"documind" }}
    """
    if not url:
        return url
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query))
    query.update({'utm_source': 'studio-site', 'utm_campaign': campaign})
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


@register.filter
def service(solution):
    """Service name, one-line description and icon for a Solution. Example: {% with m=s|service %}"""
    from apps.content.services import service_for
    return service_for(solution)


@register.filter
def public_projects(solution):
    """A solution's projects that visitors may see. Example: {% with projs=s|public_projects %}"""
    return solution.projects.public().order_by('order')


@register.filter
def service_name(solution):
    """Short service name for a Solution, e.g. "AI assistants and support tools"."""
    from apps.content.services import service_for
    return service_for(solution)['name']
