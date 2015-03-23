import os

from fabric.api import abort, env, local, run, settings
from fabric.context_managers import cd, hide, prefix
from fabric.contrib import files
from Lunchbreak.config import Base, Beta, Development, Staging, UWSGI
from fabric.operations import reboot

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
	run('cp %s/default/nginx %s' % (PATH, availableFile,))

	# Replace the variables
	files.sed(availableFile, '{upstream}', BRANCH)
	files.sed(availableFile, '{port}', CONFIG.PORT)
	files.sed(availableFile, '{domain}', CONFIG.HOST)
	files.sed(availableFile, '{path}', PATH)

	# Link the available site configuration with the enabled one
	run('ln -s %s %s' % (availableFile, enabledDir,))


def installations(rebooted=False):
	with hide('stdout'):
		run('apt-get update')
		run('apt-get -y upgrade')

		# Autofill mysql-server passwords
		run('debconf-set-selections <<< "mysql-server mysql-server/root_password password %s"' % MYSQL_ROOT_PASSWORD)
		run('debconf-set-selections <<< "mysql-server mysql-server/root_password_again password %s"' % MYSQL_ROOT_PASSWORD)

		run('apt-get -y install %s' % ' '.join(PACKAGES))

		# Clear autofillers after in case they weren't used
		run('echo PURGE | debconf-communicate mysql-server')

		if files.exists('/var/run/reboot-required.pkgs'):  # File exists if a reboot is required after an installation
			if rebooted:
				abort('I might be stuck in a reboot loop, come have a look sysadmin.')
			reboot(wait=180)  # We are gonna reboot the system and give it 3 minutes at max to reboot, else there's something wrong.
			installations(rebooted=True)
			return

		# Install pip
		run('wget https://bootstrap.pypa.io/get-pip.py')
		run('python get-pip.py')

		# Globally install pip packages
		run('pip install %s' % ' '.join(PIP_PACKAGES))


def prerequisites():
	run('export DJANGO_CONFIGURATION=%s' % CONFIG.__name__)
	run('export DJANGO_SETTINGS_MODULE=Lunchbreak.settings')
	local('python manage.py test lunch')


def updateProject():
	if not files.exists(PATH):
		with settings(hide('stdout'), warn_only=True):
			if run('git clone git@github.com:AndreasBackx/Lunchbreak-API.git %s' % PATH).failed:
				abort('The public key has not been added to Github yet: %s' % getPublicKey(HOME))

	# Update the files first inside of the remote path
	with cd(PATH):
		run('git fetch --all')
		run('git reset --hard origin/%s' % BRANCH)

		run('cp %s/default/.bashrc %s/.bashrc' % (PATH, HOME,))

		with prefix('source %s' % HOME + '/.bashrc'):
			with settings(warn_only=True):
				output = run('lsvirtualenv | grep %s' % BRANCH)
				if output.failed:  # Virtualenv doesn't exist, so create it
					if run('mkvirtualenv -a %s %s' % (PATH, CONFIG.HOST,)).failed:
						abort('Could not create virtualenv.')

		# Use the branch as a virtualenv and migrate everything
		with prefix('workon %s' % CONFIG.HOST):
			with hide('stdout'):
				run('pip install -r requirements.txt')
				run('python manage.py migrate lunch --noinput')
				run('python manage.py collectstatic --noinput -c')


def getPublicKey(home):
	return run('cat %s/.ssh/id_rsa.pub' % home)


def mysql():
	# key_buffer is deprecated and generates warnings, must be changed to key_buffer_size
	files.sed('/etc/mysql/my.cnf', r'key_buffer\s+', 'key_buffer_size ')
	run('service mysql restart')


def deploy():
	prerequisites()

	# Create the user
	with settings(warn_only=True):
		run('useradd %s --create-home --home %s' % (USER, HOME,))
		run('nginx')

	# Generate public/private key if it doesn't exist
	key = '/root/.ssh/id_rsa'
	if not files.exists(key):
		run('ssh-keygen -b 2048 -t rsa -f %s -q -N ""' % key)
		abort('The public key needs to be added to Github: %s' % getPublicKey('/root'))
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
