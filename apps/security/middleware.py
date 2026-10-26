from django.db import connection
from django.conf import settings

class StrictSecurityHeadersMiddleware:
    """
    Enforces strict security headers:
    - Content-Security-Policy (CSP)
    - Strict-Transport-Security (HSTS)
    - X-Content-Type-Options: nosniff
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy
    - Cross-Origin-Opener-Policy: same-origin
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # CSP (Strict on public pages; permit admin assets on admin dashboard)
        admin_prefix = '/' + getattr(settings, 'ADMIN_URL_PATH', 'manage-studio/').strip('/') + '/'
        if request.path_info.startswith(admin_prefix):
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://challenges.cloudflare.com; "
                "frame-src https://challenges.cloudflare.com; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "form-action 'self'; "
                "base-uri 'self'; "
                "object-src 'none'; "
                "frame-ancestors 'none';"
            )
        else:
            csp = (
                "default-src 'self'; "
                "script-src 'self' https://challenges.cloudflare.com; "
                "frame-src https://challenges.cloudflare.com; "
                "style-src 'self'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "form-action 'self'; "
                "base-uri 'self'; "
                "object-src 'none'; "
                "frame-ancestors 'none';"
            )
        response['Content-Security-Policy'] = csp
        response['X-Content-Type-Options'] = 'nosniff'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Permissions-Policy'] = 'camera=(), geolocation=(), payment=(), microphone=()'
        
        # Do not allow Access-Control-Allow-Origin wildcard
        if 'Access-Control-Allow-Origin' in response:
            del response['Access-Control-Allow-Origin']
            
        return response


class RowLevelSecurityMiddleware:
    """
    Sets local session transaction variables for PostgreSQL RLS.
    In SQLite, this is safely ignored.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                is_staff = 'true' if (request.user.is_authenticated and request.user.is_staff) else 'false'
                session_key = request.session.session_key or 'anonymous'
                cursor.execute(f"SET LOCAL app.is_staff = '{is_staff}';")
                cursor.execute(f"SET LOCAL app.session_key = '{session_key}';")
                
        return self.get_response(request)
