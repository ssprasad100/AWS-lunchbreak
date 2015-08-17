from split_settings.tools import optional, include
import os

TRAVIS_BRANCH = os.environ.get('TRAVIS_BRANCH')

if TRAVIS_BRANCH is None:
    include(
        'base.py',

        'branches/%s.py' % os.environ.get('DJANGO_SETTINGS_BRANCH'),

        'final.py',

        scope=globals()
    )
else:
    include(
        'base.py',

        'branches/%s.py' % os.environ.get('DJANGO_SETTINGS_BRANCH'),

        'travis.py',
        'final.py',

        scope=globals()
    )
