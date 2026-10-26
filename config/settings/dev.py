from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Locally, show every project, including ones whose Try it page is still being built
PREVIEW_UNFINISHED_PROJECTS = True

# Locally, no rate limits (Try it pages, contact form, analytics) so you can test freely.
# Production keeps them: prod.py does not change this, so django-ratelimit's default (on) applies.
RATELIMIT_ENABLE = False
AI_DAILY_CAP = 0  # no daily AI limit while testing locally

# Print how each Try it question flows to Hero's AI and back (see apps/tryit/trace.py)
AI_TRACE = True
# Set to True to also see the prompts, AI replies and results under each step
AI_TRACE_DETAIL = False

# Wrong addresses show the HaggLab 404 page here too, as on the live site.
# Remove this line to see Django's yellow debug page (lists every URL) instead.
MIDDLEWARE += ['apps.core.middleware.FriendlyNotFoundMiddleware']

# Use Neon PostgreSQL whenever NEON_DB_HOST is provided in .env
NEON_HOST = env('NEON_DB_HOST', default=None)
if NEON_HOST:
    DATABASES['default'] = {
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
    }

