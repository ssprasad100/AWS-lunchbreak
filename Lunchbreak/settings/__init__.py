from split_settings.tools import include
import os

TRAVIS_BRANCH = os.environ.get('TRAVIS_BRANCH')

print TRAVIS_BRANCH

print os.environ.get('MYSQL_ROOT_PASSWORD')

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

        'branches/%s.py' % TRAVIS_BRANCH,

        'travis.py',
        'final.py',

        scope=globals()
    )
