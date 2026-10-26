import re

from apps.core.fiverr import fiverr_enabled

class FiverrVisitorMiddleware:
    """
    Detects if a visitor originated from Fiverr via ref=fiverr or utm_source=fiverr.
    Persists detection in the session so they are routed through Path A (Fiverr only)
    and never exposed to direct email/phone or off-platform payment.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not fiverr_enabled():
            # Fiverr is switched off: every visitor uses the contact form
            request.session.pop('is_fiverr', None)
            request.is_fiverr = False
            return self.get_response(request)

        ref = request.GET.get('ref', '').lower()
        utm_source = request.GET.get('utm_source', '').lower()
        
        if ref == 'fiverr' or utm_source == 'fiverr':
            request.session['is_fiverr'] = True

        request.is_fiverr = request.session.get('is_fiverr', False)
        
        response = self.get_response(request)
        return response
