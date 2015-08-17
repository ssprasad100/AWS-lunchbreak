from split_settings.tools import optional, include
import os

include(
    'base.py',
    optional('versions/%s.py' % os.environ.get('DJANGO_SETTINGS_VERSION')),
    'final.py',

    scope=globals()
)
