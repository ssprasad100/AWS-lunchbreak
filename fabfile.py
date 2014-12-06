from fabric.api import abort, env, run, sudo
from fabric.context_managers import cd, prefix

import os

REMOTE_PATH_VAR = 'LUNCHBREAK_PATH'
HOST_STRING_VAR = 'LUNCHBREAK_HOST_STRING'
REMOTE_PATH = os.environ.get(REMOTE_PATH_VAR)
HOST_STRING = os.environ.get(HOST_STRING_VAR)
env.host_string = HOST_STRING


def deploy():
	if REMOTE_PATH is None:
		abort('No system variable "' + REMOTE_PATH_VAR + '" set.')

	if HOST_STRING is None:
		abort('No system variable "' + HOST_STRING_VAR + '" set.')

	sudo('service apache2 graceful-stop')

	with cd(REMOTE_PATH):
		run('git pull')
		with prefix('workon lunchbreak'):
			pipInstall = run('pip install -r "' + REMOTE_PATH + '/requirements.txt"')
			if pipInstall.failed:
				abort('Could not install requirements.')
			migration = run('python manage.py migrate lunch')
			if migration.failed:
				abort('Something went wrong when migrating the database.')
			static = run('python manage.py collectstatic --noinput -c')
			if static.failed:
				abort('Something went wrong when collecting the static files.')

	sudo('service apache2 start')
