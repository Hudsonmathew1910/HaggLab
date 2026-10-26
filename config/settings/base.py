import os
import sys
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR is the tenet/ directory root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Add apps directory to sys.path so apps can be imported cleanly
sys.path.insert(0, str(BASE_DIR / 'apps'))

env = environ.Env(
    DEBUG=(bool, False),
    STUDIO_NAME=(str, "HaggLab"),
    ADMIN_URL_PATH=(str, "studio-portal-access/"),
    SITE_URL=(str, "http://localhost:8000"),
    TURNSTILE_SITE_KEY=(str, ""),  # empty = spam check off (local dev); required in production
    TURNSTILE_SECRET_KEY=(str, ""),
    HEROS_API_URL=(str, "https://hero-s-ai.alwaysdata.net/api/v1"),
    HEROS_API_KEY_1=(str, ""),
    HEROS_API_KEY_2=(str, ""),
    HEROS_API_KEY_3=(str, ""),
    GEMINI_API_KEY_1=(str, ""),
    GEMINI_API_KEY_2=(str, ""),
    GEMINI_MODEL=(str, "gemini-3.5-flash"),
    HEROS_MODEL=(str, "baymax-4.5"),
    PINECONE_API_KEY=(str, ""),
    PINECONE_INDEX=(str, "hagglab-db"),
    PREVIEW_UNFINISHED_PROJECTS=(bool, False),
    OWNER_EMAIL=(str, ""),
    EMAIL_HOST=(str, ""),
    EMAIL_PORT=(int, 587),
    EMAIL_HOST_USER=(str, ""),
    EMAIL_HOST_PASSWORD=(str, ""),
    EMAIL_USE_TLS=(bool, True),
    EMAIL_USE_SSL=(bool, False),
    DEFAULT_FROM_EMAIL=(str, ""),
)

# Read .env if present
environ.Env.read_env(BASE_DIR / '.env')

_raw_secret_key = env('SECRET_KEY', default='').strip()
SECRET_KEY = _raw_secret_key or 'django-insecure-hagglab-local-dev-fallback-key-strictly-dev-only'
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '[::1]'])

# Company name is fixed in code so an old STUDIO_NAME in .env cannot override the brand
STUDIO_NAME = 'HaggLab'

# Cloudflare Turnstile spam check for the contact form (empty = off)
TURNSTILE_SITE_KEY = env('TURNSTILE_SITE_KEY')
TURNSTILE_SECRET_KEY = env('TURNSTILE_SECRET_KEY')

# Hero's AI API: powers every project's Try it page. Called from the server only; the key never reaches the browser.
HEROS_API_URL = env('HEROS_API_URL')
HEROS_API_KEYS = [k for k in (env('HEROS_API_KEY_1'), env('HEROS_API_KEY_2'), env('HEROS_API_KEY_3')) if k]
HEROS_MODEL = env('HEROS_MODEL')

# Google Gemini, the second AI provider (REST generateContent, called from the server only)
GEMINI_API_KEYS = [k for k in (env('GEMINI_API_KEY_1'), env('GEMINI_API_KEY_2')) if k]
GEMINI_MODEL = env('GEMINI_MODEL')
GEMINI_API_TIMEOUT = 30

# Fallback order: the providers take turns, key by key, until one answers:
# Gemini 1 -> Hero 1 -> Gemini 2 -> Hero 2 -> Hero 3 (Gemini first: it answers in seconds) (see apps/tryit/hero_client.py, provider_chain)
HEROS_API_TIMEOUT = 60  # Hero's AI usually needs 25-40 s; it is the backup after Gemini

# Show projects whose Try it page is not ready yet (local development only)
PREVIEW_UNFINISHED_PROJECTS = env('PREVIEW_UNFINISHED_PROJECTS')

# Pinecone vector database for RAG (see apps/tryit/rag.py). The index embeds the text itself.
PINECONE_API_KEY = env('PINECONE_API_KEY')
PINECONE_INDEX = env('PINECONE_INDEX')
# How many chunks to send to the AI per question, per project
RAG_TOP_K = {'documind': 5, 'shopassist': 10, 'supportflow': 4, 'supportflow-tickets': 8, 'voicedesk': 5,
             'deskpilot': 4}

# Email: new-inquiry alerts go to OWNER_EMAIL, sent through this SMTP account (e.g. Gmail with an app password)
OWNER_EMAIL = env('OWNER_EMAIL')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_USE_SSL = env('EMAIL_USE_SSL')
EMAIL_TIMEOUT = 15
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL') or (f'HaggLab <{EMAIL_HOST_USER}>' if EMAIL_HOST_USER else 'webmaster@localhost')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Print each Try it request's AI steps to the server terminal (on in dev.py, off here)
AI_TRACE = False
AI_TRACE_DETAIL = False  # True also prints prompts, AI replies and results

# Site-wide limit on AI calls per day (UTC), to protect API keys and bills. 0 = no limit.
AI_DAILY_CAP = env.int('AI_DAILY_CAP', default=300)

# Try it pages: tries per visitor (IP) per hour
TRY_RATE = '10/h'
ADMIN_URL_PATH = (env('ADMIN_URL_PATH', default='manage-studio/') or 'manage-studio/').strip('/') + '/'
SITE_URL = env('SITE_URL', default='http://localhost:8000') or 'http://localhost:8000'

# Application definition
INSTALLED_APPS = [
    # Admin theme (must precede django.contrib.admin)
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    
    # 2FA
    'django_otp',
    'django_otp.plugins.otp_totp',

    # Studio Apps
    'apps.core',
    'apps.content',
    'apps.leads',
    'apps.security',
    'apps.analytics',
    'apps.tryit',
]

MIDDLEWARE = [
    'apps.security.middleware.StrictSecurityHeadersMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.leads.middleware.FiverrVisitorMiddleware',
    'apps.security.middleware.RowLevelSecurityMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.studio_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database defaults to SQLite for local dev
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'ATOMIC_REQUESTS': True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Private upload storage outside static
PRIVATE_STORAGE_ROOT = BASE_DIR / 'private_uploads'
os.makedirs(PRIVATE_STORAGE_ROOT, exist_ok=True)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session & Cookie Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Rate Limiting
RATELIMIT_VIEW = 'apps.core.views.rate_limited_view'

# Public routes allowlist for route security check
PUBLIC_ROUTES = [
    'home',
    'solutions_hub',
    'solution_detail',
    'projects_hub',
    'project_detail',
    'process',
    'security_data',
    'about',
    'faq',
    'hire_fiverr',
    'start_project',
    'thank_you',
    'privacy_policy',
    'terms_of_service',
    'styleguide',
    'health_check',
    'analytics_event',
    'try_project',
    'try_api',
    'sitemap',
    'robots',
]

# Jazzmin Admin Dashboard Theme Settings
JAZZMIN_SETTINGS = {
    "site_title": "HaggLab Admin",
    "site_header": "HaggLab",
    "site_brand": "HaggLab",
    "site_icon": "img/v2/favicon.svg",
    "site_logo": "img/brand-hagglab/hagglab-mark-light.svg",
    "login_logo": "img/brand-hagglab/hagglab-mark.svg",
    "welcome_sign": "Welcome to HaggLab Admin",
    "copyright": "HaggLab",
    "search_model": ["content.Project", "content.Solution"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Live Site", "url": "/"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["content", "leads", "auth", "otp_totp"],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user-shield",
        "auth.Group": "fas fa-users",
        "content.Solution": "fas fa-layer-group",
        "content.Project": "fas fa-laptop-code",
        "content.FAQ": "fas fa-question-circle",
        "leads.Inquiry": "fas fa-envelope-open-text",
        "otp_totp.TOTPDevice": "fas fa-key",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": True,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-teal",
    "navbar": "navbar-dark navbar-navy",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-navy",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}
