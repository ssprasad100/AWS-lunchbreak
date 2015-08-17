import os

HOST = HOST if 'HOST' in globals() else '%s.lunchbreakapp.be' % BRANCH

if 'ALLOWED_HOSTS' not in globals():
    ALLOWED_HOSTS = []

if HOST not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(HOST)

DB_NAME = DB_NAME if 'DB_NAME' in globals() else 'LB_%s' % BRANCH
DB_USER = DB_USER if 'DB_USER' in globals() else DB_NAME

if 'DB_PASS' not in globals():
    DB_PASS_VAR = 'LB_%s_password' % BRANCH
    DB_PASS = os.environ.get(DB_PASS_VAR)
DB_PASS = DB_PASS if DB_PASS is not None else DB_NAME

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': 'localhost',
        'PORT': '3306'
    }
}
