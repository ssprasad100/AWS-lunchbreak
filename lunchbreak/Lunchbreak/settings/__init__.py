import os

from split_settings.tools import include

TRAVIS_BRANCH = os.environ.get('TRAVIS_BRANCH')


if TRAVIS_BRANCH is None:
    includes = [
        'base.py',
        'branches/%s.py' % os.environ.get('DJANGO_SETTINGS_VERSION'),
        'final.py',
    ]
else:
    includes = [
        'base.py',
        'branches/%s.py' % os.environ.get('DJANGO_SETTINGS_VERSION'),
        'travis.py',
        'final.py',
    ]


# Lazy hack to check whether local.py exists
try:
    from .local import *  # NOQA
    includes.append(
        'local.py'
    )
except ImportError:
    pass

include(
    *includes,
    scope=globals()
)
