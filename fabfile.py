import os

from fabric.api import abort, env, local, run, sudo
from fabric.context_managers import cd, prefix

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
		run('git pull --no-edit')
		with prefix('workon lunchbreak'):
			pipInstall = run('pip install -r "' + REMOTE_PATH + '/requirements.txt"')
			if pipInstall.failed:
				abort('Could not install requirements.')
			migration = run('python manage.py migrate lunch --noinput')
			if migration.failed:
				abort('Something went wrong when migrating the database.')
			static = run('python manage.py collectstatic --noinput -c')
			if static.failed:
				abort('Something went wrong when collecting the static files.')

	sudo('service apache2 start')
	local("""
		curl https://opbeat.com/api/v1/organizations/308fe549a8c042429061395a87bb662a/apps/a475a69ed8/releases/ \
			-H "Authorization: Bearer e2e3be25fe41c9323f8f4384549d7c22f8c2422e" \
			-d rev=`git log -n 1 --pretty=format:%H` \
			-d branch=`git rev-parse --abbrev-ref HEAD` \
			-d status=completed
	""")
