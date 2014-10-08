import os
import sys  
import site

site.addsitedir('/home/lunchbreak/.virtualenvs/lunchbreak/local/lib/python2.7/site-packages')

sys.path.append('/home/lunchbreak/public_html/lunchbreak/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Lunchbreak.settings'

activate_env=os.path.expanduser('/home/lunchbreak/.virtualenvs/lunchbreak/bin/activate_this.py')
execfile(activate_env, dict(__file__=activate_env))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
