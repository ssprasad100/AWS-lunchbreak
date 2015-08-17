from split_settings.tools import optional, include
import os

include(
    'base.py',
    optional('branches/%s.py' % os.environ.get('DJANGO_SETTINGS_BRANCH')),
    'final.py',

    scope=globals()
)
