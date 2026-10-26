from django.conf import settings

from .views import custom_404_view


class FriendlyNotFoundMiddleware:
    """
    Local only (added in dev.py). With DEBUG on, Django replaces every 404 with its yellow debug page,
    so a wrong address looked different on this computer than on the live site. This swaps that page
    for the HaggLab 404 page. JSON 404s from the API are left alone. In production (DEBUG off) Django
    already uses handler404, so this does nothing there.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (settings.DEBUG and response.status_code == 404
                and response.get('Content-Type', '').startswith('text/html')):
            return custom_404_view(request)
        return response
