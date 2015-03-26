import os

from configurations.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_CONFIGURATION', 'Development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lunchbreak.settings')

application = get_wsgi_application()
