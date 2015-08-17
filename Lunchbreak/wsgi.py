import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_VERSION', 'development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lunchbreak.settings')

application = get_wsgi_application()
