import os

import uwsgi
from django.core.wsgi import get_wsgi_application
from django.utils import autoreload
from uwsgidecorators import timer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lunchbreak.settings')
os.environ.setdefault('DJANGO_SETTINGS_BRANCH', 'development')

application = get_wsgi_application()


@timer(3)
def change_code_graceful_reload(sig):
    if autoreload.code_changed():
        uwsgi.reload()
