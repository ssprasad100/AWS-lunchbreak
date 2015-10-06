import os
import random

from fabric.api import abort, env, local, run, settings
from fabric.context_managers import cd, hide, prefix
from fabric.contrib import files
from fabric.operations import put, reboot
from fabric.utils import warn

PYTHON_VERSION = '2.7.10'  # Used in Pyenv
PYTHON_VERSION_FULL = 'Python 2.7.10'  # Returned by `python --version`

PACKAGES = [
    'git',
    'nginx',
    'python',
    'python2.7-dev',  # Compilation of uWSGI
    'build-essential',  # Compilation of uWSGI
    'mysql-server',
    'libmysqlclient-dev',  # MySQL-python pip module
    'libffi-dev',  # cffi pip module
    'libpcre3',  # uWSGI internal routing support
    'libpcre3-dev',  # uWSGI internal routing support

    # Python compiling
    # Python readline extension
    'libreadline6',
    'libreadline6-dev',
    # Python bz2 extension
    'libbz2-dev',
    # Python sqlite3 extension
    'libsqlite3-dev',
    # Python ssl extension
    'libssl-dev',
]
PIP_PACKAGES = ['uwsgi', 'virtualenvwrapper']

BRANCH = os.environ.get('TRAVIS_BRANCH') or local('git rev-parse --abbrev-ref HEAD', capture=True)
os.environ.setdefault('DJANGO_SETTINGS_BRANCH', BRANCH)

from Lunchbreak.settings import *

CONFIG = globals()

APNS_FOLDER = '/etc/lunchbreak/apns/'
CERT_TYPE = 'development' if CONFIG['DEBUG'] else 'production'
BUSINESS_APNS_CERTIFICATE = APNS_FOLDER + 'business_{certType}.pem'.format(
    certType=CERT_TYPE
)
CUSTOMERS_APNS_CERTIFICATE = APNS_FOLDER + 'customers_{certType}.pem'.format(
    certType=CERT_TYPE
)

NGINX = '/etc/init.d/nginx'

USER = BRANCH
HOME = '/home/%s' % USER
PATH = '%s/%s' % (HOME, CONFIG['HOST'],)

MYSQL_USER = CONFIG['DATABASES']['default']['USER']
MYSQL_DATABASE = CONFIG['DATABASES']['default']['NAME']
MYSQL_HOST = CONFIG['DATABASES']['default']['HOST']
MYSQL_USER_PASSWORD = None

MYSQL_ROOT_PASSWORD_VAR = 'MYSQL_ROOT_PASSWORD'
MYSQL_ROOT_PASSWORD = 'password'

env.host_string = '%s@%s' % ('root', CONFIG['HOST'],)
env.shell = '/bin/bash -c -l'

characters = 'ABCDEFGHIJKLMNOPQRSTUVWabcdefghijklmnopqrstuvwxyz0123456789'


def generateString(length):
    return ''.join(random.choice(characters) for a in xrange(length))


def getSysvar(key):
    with hide('running', 'stdout'):
        output = run('echo $%s' % key)
    return None if not output else output


def setSysvar(key, value):
    if getSysvar(key) is None:
        command = 'export %s="%s"' % (key, value,)
        run(command)
        files.append('%s/.bash_profile' % HOME, command)


def getPublicKey(home):
    return run('cat %s/.ssh/id_rsa.pub' % home)


def runQuery(query, user='root', password=None):
    password = password if password is not None else MYSQL_ROOT_PASSWORD
    with hide('stdout'):
        return run('mysql -u %s  --password="%s" -e \'%s\'' % (user, password, query,))


def prerequisites():
    local('tox')
    put('default/.bash_profile', '~/.bash_profile')


def sedFile(f, variables):
    for key, value in variables.iteritems():
        with hide('stdout', 'running'):
            files.sed(f, '\{%s\}' % key, value)


def installations(rebooted=False):
    with hide('stdout'):
        run('apt-get -qq update')
        run('apt-get -yqq upgrade')

        # Autofill mysql-server passwords
        with hide('stdout', 'running'):
            run('debconf-set-selections <<< "mysql-server mysql-server/root_password password %s"' % MYSQL_ROOT_PASSWORD)
            run('debconf-set-selections <<< "mysql-server mysql-server/root_password_again password %s"' % MYSQL_ROOT_PASSWORD)

        run('apt-get -yqq install %s' % ' '.join(PACKAGES))

        # Clear autofillers after in case they weren't used
        run('echo PURGE | debconf-communicate mysql-server')

        timezoneFile = '/etc/timezone'
        correctTimezone = run('cat %s' % timezoneFile) == CONFIG['TIME_ZONE']
        if not correctTimezone:
            run('echo "%s" | tee %s' % (CONFIG['TIME_ZONE'], timezoneFile,))
            run('dpkg-reconfigure --frontend noninteractive tzdata')

        if files.exists('/var/run/reboot-required.pkgs'):  # File exists if a reboot is required after an installation
            if rebooted:
                abort('I might be stuck in a reboot loop, come have a look sysadmin.')
            reboot(wait=180)  # We are gonna reboot the system and give it 3 minutes at max to reboot, else there's something wrong.
            installations(rebooted=True)
            return
        elif not correctTimezone:
            run('service cron restart')  # If the timezone was incorrect, restart the cron service just in case, but not when there is a reboot

        run('apt-get -qq autoremove')
        run('apt-get -qq autoclean')


def python():
    with hide('stdout'):
        # Install Pyenv
        with settings(warn_only=True):
            which = run('which pyenv')
            installed = which.return_code == 0
            if not installed:
                run('curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash')
                run('pyenv update')

        run('pyenv install -s {python_version}'.format(
                    python_version=PYTHON_VERSION
                )
            )
        run('pyenv global {python_version}'.format(
                    python_version=PYTHON_VERSION
                )
            )

        assert run('python --version') == PYTHON_VERSION_FULL, 'Python version not successfully installed.'

        # Install pip
        run('wget https://bootstrap.pypa.io/get-pip.py')
        run('python get-pip.py')

        # Globally install pip packages
        run('pip install %s' % ' '.join(PIP_PACKAGES))


def firewall():
    run('ufw default deny incoming')
    run('ufw default allow outgoing')
    run('ufw allow ssh')
    run('ufw allow 443/tcp')
    run('ufw disable')
    run('ufw --force enable')


def updateProject():
    if not files.exists(PATH):
        with settings(hide('stdout'), warn_only=True):
            if run('git clone git@github.com:AndreasBackx/Lunchbreak-API.git %s' % PATH).failed:
                abort('The public key has not been added to Github yet: %s' % getPublicKey(HOME))

    virtualEnv = BRANCH

    # Update the files first inside of the remote path
    with cd(PATH):
        run('git fetch --all')
        run('git reset --hard origin/%s' % BRANCH)

        bash_profile = '%s/.bash_profile' % HOME
        if not files.exists(bash_profile):
            put('default/.bash_profile', '~/.bash_profile')
        mysql()

        with settings(warn_only=True):
            output = run('lsvirtualenv | grep %s' % virtualEnv)
            if output.failed:  # Virtualenv doesn't exist, so create it
                if run('mkvirtualenv -a %s %s' % (PATH, virtualEnv,)).failed:
                    abort('Could not create virtualenv.')

        # Use the branch as a virtualenv and migrate everything
        with prefix('workon %s' % virtualEnv):
            run('pip install --upgrade pip')
            run('pip install -r requirements.txt --exists-action w')

            setSysvar('DJANGO_SETTINGS_BRANCH', BRANCH)
            setSysvar('DJANGO_SETTINGS_MODULE', 'Lunchbreak.settings')
            setSysvar('BUSINESS_APNS_CERTIFICATE', BUSINESS_APNS_CERTIFICATE)
            setSysvar('CUSTOMERS_APNS_CERTIFICATE', CUSTOMERS_APNS_CERTIFICATE)

            run('python manage.py migrate --noinput')
            staticRoot = '%s/%s%s' % (HOME, CONFIG['HOST'], CONFIG['STATIC_RELATIVE'],)
            if not files.exists(staticRoot):
                run('mkdir -p "%s"' % staticRoot)
            run('python manage.py collectstatic --noinput -c')


def mysql():
    env.host_string = '%s@%s' % ('root', CONFIG['HOST'],)
    # key_buffer is deprecated and generates warnings, must be changed to key_buffer_size
    files.sed('/etc/mysql/my.cnf', r'key_buffer\s+', 'key_buffer_size ')
    run('service mysql restart')

    env.host_string = '%s@%s' % (USER, CONFIG['HOST'],)

    global MYSQL_USER_PASSWORD
    MYSQL_USER_PASSWORD = getSysvar(CONFIG['DB_PASS_VAR'])

    if MYSQL_USER_PASSWORD is None:  # User probably doesn't exist
        MYSQL_USER_PASSWORD = generateString(32)
        setSysvar(CONFIG['DB_PASS_VAR'], MYSQL_USER_PASSWORD)

        runQuery('CREATE DATABASE %s;' % MYSQL_DATABASE)
        runQuery('CREATE USER "%s"@"%s" IDENTIFIED BY "%s";' % (MYSQL_USER, MYSQL_HOST, MYSQL_USER_PASSWORD,))
        runQuery('GRANT ALL PRIVILEGES ON %s.* TO "%s"@"%s";' % (MYSQL_DATABASE, MYSQL_USER, MYSQL_HOST,))
        runQuery('FLUSH PRIVILEGES;')


def nginx():
    nginxDir = '/etc/nginx'
    sslDir = '%s/ssl' % nginxDir
    availableFile = '%s/sites-available/%s' % (nginxDir, CONFIG['HOST'],)
    enabledDir = '%s/sites-enabled/' % nginxDir

    # Don't send Nginx version number in error pages and server header
    files.uncomment('%s/nginx.conf' % nginxDir, 'server_tokens off;')

    if CONFIG['SSL']:
        if not files.exists(sslDir):
            run('mkdir -p %s' % sslDir)
        if not files.exists('%s/lunchbreak.key' % sslDir)\
            or not files.exists('%s/lunchbreak.pem' % sslDir):
            warn('Not all of the SSL files (certificates and private key) are present in the directory. Please add them to "%s" and restart nginx.' % sslDir)
        if not files.exists('%s/dhparam.pem' % sslDir):
            run('openssl dhparam -out %s/dhparam.pem 2048' % sslDir)

    # Remove the default site configuration
    defaultConfig = '%s/sites-available/default' % nginxDir
    if files.exists(defaultConfig):
        run('rm %s' % defaultConfig)
    # Copy Lunchbreak's default site configuration
    protocol = 'https' if CONFIG['SSL'] else 'http'
    run('cp %s/default/nginx-%s %s' % (PATH, protocol, availableFile,))

    aVariables = {
        'upstream': BRANCH,
        'port': CONFIG['PORT'],
        'domain': CONFIG['HOST'],
        'path': PATH,
        'static_url': CONFIG['STATIC_URL'],
        'static_relative': CONFIG['STATIC_RELATIVE'],
        'ssl_path': sslDir
    }
    sedFile(availableFile, aVariables)

    # Link the available site configuration with the enabled one
    if not files.exists('%s%s' % (enabledDir, CONFIG['HOST'],)):
        run('ln -s %s %s' % (availableFile, enabledDir,))

    run('%s restart' % NGINX)


def uwsgi():
    apps = '/etc/uwsgi/apps'
    log = '/var/log/uwsgi'

    if not files.exists(log):
        run('mkdir -p %s' % log)
        run('chown -R www-data:www-data %s' % log)
    if not files.exists(apps):
        run('mkdir -p %s' % apps)
        run('chown -R www-data:www-data %s' % apps)
    log += '/emperor.log'

    iniFile = 'lunchbreak.ini'
    run('cp %s/default/%s %s/%s' % (PATH, iniFile, PATH, iniFile,))
    iniFile = '%s/%s' % (PATH, iniFile,)

    virtualenv = '%s/.virtualenvs/%s' % (HOME, BRANCH,)

    iniVariables = {
        'host': CONFIG['HOST'],
        'path': PATH,
        'virtualenv': virtualenv,
        'branch': BRANCH,
        'password_var': CONFIG['DB_PASS_VAR'],
        'password': MYSQL_USER_PASSWORD,
        'business_apns_certificate': BUSINESS_APNS_CERTIFICATE,
        'customers_apns_certificate': CUSTOMERS_APNS_CERTIFICATE
    }
    sedFile(iniFile, iniVariables)

    run('mv %s %s/%s.ini' % (iniFile, apps, CONFIG['HOST'],))

    configFile = 'uwsgi.conf'
    initFolder = '/etc/init/'
    configPath = '%s%s' % (initFolder, configFile,)
    run('cp %s/default/%s %s' % (PATH, configFile, configPath,))

    configVariables = {
        'apps': apps,
        'log': log
    }
    sedFile(configPath, configVariables)

    run('service uwsgi restart')


def deploy():
    prerequisites()

    # Generate public/private key if it doesn't exist
    key = '/root/.ssh/id_rsa'
    if not files.exists(key):
        with hide('stdout', 'stderr'):
            run('ssh-keygen -b 2048 -t rsa -f %s -q -N ""' % key)
            abort('The public key needs to be added to Github: %s' % getPublicKey('/root'))

    installations()
    firewall()

    # Create the user
    with settings(warn_only=True):
        run('useradd %s --create-home --home %s' % (USER, HOME,))
    run('cp -r /root/.ssh %s/.ssh' % HOME)
    # Add Github to known hosts
    run('ssh-keyscan -H github.com > %s/.ssh/known_hosts' % HOME)
    run('chown -R %s:%s %s/.ssh' % (USER, USER, HOME,))

    global MYSQL_ROOT_PASSWORD
    MYSQL_ROOT_PASSWORD = getSysvar(MYSQL_ROOT_PASSWORD_VAR)

    # Use that account via SSH now
    env.host_string = '%s@%s' % (USER, CONFIG['HOST'],)

    python()
    updateProject()

    # We need root privileges
    env.host_string = '%s@%s' % ('root', CONFIG['HOST'],)

    uwsgi()
    nginx()

    if CONFIG['OPBEAT_RELEASE']:
        opbeatRelease()


def opbeatRelease():
    local("""
        curl https://opbeat.com/api/v1/organizations/308fe549a8c042429061395a87bb662a/apps/a475a69ed8/releases/ \
            -H "Authorization: Bearer e2e3be25fe41c9323f8f4384549d7c22f8c2422e" \
            -d rev=`git log -n 1 --pretty=format:%H` \
            -d branch=`git rev-parse --abbrev-ref HEAD` \
            -d status=completed
    """)
