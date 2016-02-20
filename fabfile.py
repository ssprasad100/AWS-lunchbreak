import os

from fabric.api import abort, env, local, sudo
from fabric.context_managers import cd

env.shell = '/bin/bash -c -l'

BRANCH = os.environ.get('TRAVIS_BRANCH') or \
    local('git rev-parse --abbrev-ref HEAD', capture=True)


def deploy():
    host = os.environ.get('LUNCHBREAK_HOST', None)

    if not host:
        abort('No valid LUNCHBREAK_HOST env variable given.')

    env.host_string = '{user}@{host}'.format(
        user='lunchbreak',
        host=host
    )

    with cd('lunchbreak'):
        local('tox -e py27')

    sudo(
        'salt-call --local state.highstate pillar=\'{"specified_branches": ["{branch}"]}\''.format(
            branch=BRANCH
        )
    )
