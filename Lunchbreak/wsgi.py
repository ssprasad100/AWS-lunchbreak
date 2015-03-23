import os

from configurations.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lunchbreak.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Development')
configuration = os.environ.get('DJANGO_CONFIGURATION')

application = get_wsgi_application()
