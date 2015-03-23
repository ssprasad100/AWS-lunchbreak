import os

from fabric.api import abort, env, local, run, settings
from fabric.context_managers import cd, prefix
from fabric.contrib import files
from Lunchbreak.config import Base, Beta, Development, Staging, UWSGI

PACKAGES = [
	'git',
	'nginx',
	'python',
	'python2.7-dev',  # Compilation of uWSGI
	'build-essential',  # Compilation of uWSGI
	'mysql-server',
	'libmysqlclient-dev',  # MySQL-python pip module
	'libffi-dev'  # cffi pip module
]
PIP_PACKAGES = ['uwsgi', 'virtualenvwrapper']
BRANCH = local('git rev-parse --abbrev-ref HEAD', capture=True)
CONFIGS = {
	'master': Base,
	'beta': Beta,
	'staging': Staging,
	'development': Development,
	'uwsgi': UWSGI
}
CONFIG = CONFIGS[BRANCH]
BRANCH = CONFIG.BRANCH

USER = BRANCH
HOME = '/home/%s' % USER
PATH = '%s/%s' % (HOME, CONFIG.HOST,)

MYSQL_ROOT_PASSWORD_VAR = 'MYSQL_ROOT_PASSWORD'
os.environ.setdefault('MYSQL_ROOT_PASSWORD_VAR', 'password')
MYSQL_ROOT_PASSWORD = os.environ.get(MYSQL_ROOT_PASSWORD_VAR)

env.host_string = '%s@%s' % ('root', CONFIG.HOST,)
print env.host_string


def nginx():
	nginxDir = '/etc/nginx'
	availableFile = '%s/sites-available/%s' % (nginxDir, CONFIG.HOST,)
	enabledDir = '%s/sites-enabled/' % nginxDir

	# Remove the default site configuration
	run('rm %s/sites-available/default' % nginxDir)
	# Copy Lunchbreak's default site configuration
	run('cp %s/nginx-default %s' % (PATH, availableFile,))

	# Replace the variables
	files.sed(availableFile, '{upstream}', BRANCH)
	files.sed(availableFile, '{port}', CONFIG.PORT)
	files.sed(availableFile, '{domain}', CONFIG.HOST)
	files.sed(availableFile, '{path}', PATH)

	# Link the available site configuration with the enabled one
	run('ln -s %s %s' % (availableFile, enabledDir,))


def installations():
	run('apt-get update')
	run('apt-get -y upgrade')

	# Autofill mysql-server passwords
	run('debconf-set-selections <<< "mysql-server mysql-server/root_password password %s"' % MYSQL_ROOT_PASSWORD)
	run('debconf-set-selections <<< "mysql-server mysql-server/root_password_again password %s"' % MYSQL_ROOT_PASSWORD)

	run('apt-get -y install %s' % ' '.join(PACKAGES))

	# Clear autofillers after in case they weren't used
	run('echo PURGE | debconf-communicate packagename')

	# Install pip
	run('wget https://bootstrap.pypa.io/get-pip.py')
	run('python get-pip.py')

	# Globally install pip packages
	run('pip install %s' % ' '.join(PIP_PACKAGES))


def prerequisites():
	run('export DJANGO_CONFIGURATION=%s' % CONFIG.__name__)
	run('export DJANGO_SETTINGS_MODULE=Lunchbreak.settings')
	# test()


def test():
	test = local('python manage.py test lunch')

	if test.failed:
		abort('The tests did not pass.')


def updateProject():
	if not files.exists(PATH):
		with settings(warn_only=True):
			if run('git clone git@github.com:AndreasBackx/Lunchbreak-API.git %s' % PATH).failed:
				publicKey = run('cat %s/.ssh/id_rsa.pub' % HOME)
				abort('publicKey has not been added: %s' % publicKey)

	# Update the files first inside of the remote path
	with cd(PATH):
		run('git fetch --all')
		run('git reset --hard origin/%s' % BRANCH)

		run('cp %s/bashrc-default %s/.bashrc' % (PATH, HOME,))

		with prefix('source %s' % HOME + '/.bashrc'):
			with settings(warn_only=True):
				output = local('lsvirtualenv | grep %s' % BRANCH, capture=True)
				if output.failed:  # Virtualenv doesn't exist, so create it
					if run('mkvirtualenv -a %s %s' % (PATH, CONFIG.HOST,)).failed:
						abort('Could not create virtualenv.')

		# Use the branch as a virtualenv and migrate everything
		with prefix('workon %s' % CONFIG.HOST):
			run('pip install -r requirements.txt')
			run('python manage.py migrate lunch --noinput')
			run('python manage.py collectstatic --noinput -c')


def mysql():
	pass


def deploy():
	prerequisites()

	# Create the user
	with settings(warn_only=True):
		run('useradd %s --create-home --home %s' % (USER, HOME,))
		run('nginx')
	key = '/root/.ssh/id_rsa'
	if not files.exists(key):
		run('ssh-keygen -b 2048 -t rsa -f %s -q -N ""' % key)
	run('cp -r /root/.ssh %s/.ssh' % HOME)
	run('ssh-keyscan -H github.com > %s/.ssh/known_hosts' % HOME)
	run('chown -R %s:%s %s/.ssh' % (USER, USER, HOME,))

	installations()
	run('nginx -s quit')
	# Disable the Host key checking (will still alert if it changes)

	# Use that account via SSH now
	env.host_string = '%s@%s' % (USER, CONFIG.HOST,)

	updateProject()
	mysql()

	# We need root privileges
	env.host_string = '%s@%s' % ('root', CONFIG.HOST,)

	nginx()
	run('nginx -s start')


def opbeatRelease():
	local("""
		curl https://opbeat.com/api/v1/organizations/308fe549a8c042429061395a87bb662a/apps/a475a69ed8/releases/ \
			-H "Authorization: Bearer e2e3be25fe41c9323f8f4384549d7c22f8c2422e" \
			-d rev=`git log -n 1 --pretty=format:%H` \
			-d branch=`git rev-parse --abbrev-ref HEAD` \
			-d status=completed
	""")
