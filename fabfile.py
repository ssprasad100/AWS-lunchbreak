import os

from fabric.api import abort, env, local, run, sudo
from fabric.context_managers import hide, lcd
from fabric.contrib.files import exists
from fabric.operations import put

env.shell = '/bin/bash -c -l'

BRANCH = os.environ.get('TRAVIS_BRANCH') or \
    local('git rev-parse --abbrev-ref HEAD', capture=True)
HOST = os.environ.get('LUNCHBREAK_HOST', None)


def setup():
    '''
    Setup salt on the remote machine.
    '''

    env.host_string = '{user}@{host}'.format(
        user='root',
        host=HOST
    )

    salt_ran = exists('/srv/salt')
    if salt_ran:
        abort('/src/salt exists, but the root user is still accessible!')

    run('curl -L https://bootstrap.saltstack.com -o install_salt.sh')
    run('sudo sh install_salt.sh')

    update(change_user=False)


def update(change_user=True):
    '''
    Upload salt files to /srv.
    '''

    if change_user:
        env.host_string = '{user}@{host}'.format(
            user='lunchbreak',
            host=HOST
        )

    secret_remote = '/srv/pillar/secret.sls'
    secret_local = 'salt/synced/pillar/secret.sls'

    secret_added = exists(secret_remote, use_sudo=True)
    if not secret_added:
        if os.path.isfile(secret_local):
            print 'Found secret file, uploading...'
            secret_folder = os.path.dirname(secret_remote)
            if not exists(secret_folder, use_sudo=True):
                sudo(
                    'mkdir -p {folder}'.format(
                        folder=secret_folder
                    )
                )
            result = put(
                secret_local,
                secret_remote,
                use_sudo=True
            )
            if result.failed:
                abort('Could not upload secret file.')
        else:
            abort('Server contains no secret file and there is not one locally.')

    result = put('salt/minion', '/etc/salt/minion', use_sudo=True)
    if result.failed:
        abort('Could not upload minion config.')

    result = put('salt/synced/*', '/srv', use_sudo=True)
    if result.failed:
        abort('Could not upload all salt files.')

    sudo(
        'salt-call --local state.highstate pillar=\'{{"specified_branches":'
        ' ["{branch}"]}}\''.format(
            branch=BRANCH
        )
    )


def deploy():
    if not HOST:
        abort('No valid LUNCHBREAK_HOST env variable given.')

    with lcd('lunchbreak'):
        local('tox -e py27')

    with hide('warnings', 'running', 'stdout', 'stderr'):
        update()
