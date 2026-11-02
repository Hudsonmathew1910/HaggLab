import os

# One maths thread for numpy (see manage.py): less memory on a small server
for _var in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_var, '1')

from django.core.wsgi import get_wsgi_application  # noqa: E402

# This file is only used by the production server (gunicorn); local work uses manage.py, which defaults to dev.
# Defaulting to prod means a forgotten DJANGO_SETTINGS_MODULE can never run the live site with DEBUG on.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

application = get_wsgi_application()
