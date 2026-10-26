from .base import *

DEBUG = False

# Production never shows unfinished projects
PREVIEW_UNFINISHED_PROJECTS = False

# Rate limits are always on in production
RATELIMIT_ENABLE = True

# Never print visitor input or prompts in production
AI_TRACE = False

if DEBUG:
    raise RuntimeError("Critical Security Violation: DEBUG is enabled in production settings.")

SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('NEON_DB_NAME'),
        'USER': env('NEON_DB_USER'),
        'PASSWORD': env('NEON_DB_PASSWORD'),
        'HOST': env('NEON_DB_HOST'),
        'PORT': env('NEON_DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
    }
}

# Production Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
# Silence HSTS subdomain and preload warnings until domain certs are finalized
SILENCED_SYSTEM_CHECKS = ['security.W005', 'security.W021']


SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# The contact form's spam check must be on in production
if not (TURNSTILE_SITE_KEY and TURNSTILE_SECRET_KEY):
    raise RuntimeError("TURNSTILE_SITE_KEY and TURNSTILE_SECRET_KEY must be set in production.")

# New-inquiry alerts must reach a real inbox in production
if not OWNER_EMAIL or OWNER_EMAIL.endswith('.local'):
    raise RuntimeError("OWNER_EMAIL must be set to a real address in production.")
if not (EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD):
    raise RuntimeError("EMAIL_HOST, EMAIL_HOST_USER and EMAIL_HOST_PASSWORD must be set in production.")
