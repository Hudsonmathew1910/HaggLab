import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Safe by default: debug is OFF unless DEBUG=True is set, and without debug a real SECRET_KEY and
# ALLOWED_HOSTS must be set, or the app refuses to start. Run locally with:  DEBUG=True python manage.py runserver
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'documind-local-dev-only-key' if DEBUG else '')
if not SECRET_KEY:
    raise RuntimeError('Set SECRET_KEY (and ALLOWED_HOSTS) in the environment, or DEBUG=True for local use.')
ALLOWED_HOSTS = ['*'] if DEBUG else [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'documind',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'documind.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'documind.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

PRIVATE_STORAGE_ROOT = BASE_DIR / 'private_uploads'
os.makedirs(PRIVATE_STORAGE_ROOT, exist_ok=True)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
