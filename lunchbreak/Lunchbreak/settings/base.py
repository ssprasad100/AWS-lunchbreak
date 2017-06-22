import os

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MEDIA_ROOT = os.environ.get(
    'MEDIA_ROOT',
    os.path.normpath(os.path.join(BASE_DIR, 'media'))
)
MEDIA_URL = '/media/'
PRIVATE_MEDIA_ROOT = os.environ.get(
    'PRIVATE_MEDIA_ROOT',
    os.path.normpath(os.path.join(BASE_DIR, 'media-private'))
)
PRIVATE_MEDIA_URL = '/internal/'
PRIVATE_MEDIA_SERVER = 'private_media.servers.NginxXAccelRedirectServer'
PRIVATE_MEDIA_PERMISSIONS = 'lunch.authentication.PrivateMediaAuthentication'
IMAGEKIT_DEFAULT_FILE_STORAGE = 'private_media.storages.PrivateMediaStorage'
SENDFILE_ROOT = PRIVATE_MEDIA_ROOT
SENDFILE_URL = PRIVATE_MEDIA_URL

SECRET_KEY = 'e2a86@j!uc5@z^yu=%n9)6^%w+-(pk8a6@^i!vnvxe^-w%!q8('

DEBUG = False
SSL = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'push_notifications',
    'rest_framework',
    'private_media',
    'compressor',
    'sass_processor',
    'subdomains',
    'raven.contrib.django.raven_compat',
    'django_jinja',
    'sendfile',

    'imagekit',
    'polaroid',

    'django_sms',
    'payconiq',
    'django_gocardless',
    'business',
    'customers',
    'lunch',
    'frontend',
    'versioning_prime',
]

MIDDLEWARE_CLASSES = (
    'Lunchbreak.middleware.RedirectHostMiddleware',
    'Lunchbreak.middleware.SubdomainHostMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

HOST = 'lunchbreak.eu'
ROOT_URLCONF = 'Lunchbreak.urls.frontend'
SUBDOMAIN_URLCONFS = {
    None: 'Lunchbreak.urls.frontend',
    'www': 'Lunchbreak.urls.frontend',
    'api': 'Lunchbreak.urls.api',
}
SUBDOMAIN_DEFAULT = 'www'

JINJA2_MUTE_URLRESOLVE_EXCEPTIONS = True

WSGI_APPLICATION = 'Lunchbreak.wsgi.application'

AUTH_USER_MODEL = 'customers.User'
AUTHENTICATION_BACKENDS = [
    'customers.authentication.CustomerBackend',
    'django.contrib.auth.backends.ModelBackend'
]
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
)

LANGUAGE_CODE = 'nl-BE'
LANGUAGES = [
    ('nl-BE', _('Belgium Dutch')),
]
TIME_ZONE = 'Europe/Brussels'
USE_I18N = True  # Translate localisation
USE_L10N = True  # Format localisation
USE_TZ = True

LOGIN_REDIRECT_URL = reverse_lazy('frontend:index')
LOGIN_URL = reverse_lazy('frontend:login')

FIXTURE_DIRS = [
    os.path.normpath(os.path.join(BASE_DIR, 'fixtures'))
]

STATIC_ROOT = os.environ.get(
    'STATIC_ROOT',
    os.path.normpath(os.path.join(BASE_DIR, 'static'))
)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'frontend/img'),
    os.path.join(BASE_DIR, 'frontend/js'),
    os.path.join(BASE_DIR, 'frontend/jinja2/nunjucks'),
    os.path.join(BASE_DIR, 'frontend/scss'),
    os.path.join(BASE_DIR, 'frontend/mdl/src'),
    os.path.join(BASE_DIR, 'frontend/intl-tel-input/build/js'),
    os.path.join(BASE_DIR, 'frontend/intl-tel-input/build/img'),
]

COMPRESS_ENABLED = True
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    'sass_processor.finders.CssFinder',
]
SASS_PROCESSOR_ENABLED = True
SASS_PROCESSOR_INCLUDE_DIRS = (
    os.path.join(BASE_DIR, 'frontend/mdl/src'),
    os.path.join(BASE_DIR, 'frontend/scss'),
    os.path.join(BASE_DIR, 'frontend/intl-tel-input/src/css'),
)

APPEND_SLASH = False

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [],

    'DEFAULT_PAGINATION_CLASS': 'lunch.pagination.SimplePagination',
    'PAGE_SIZE': 25,
    'MAX_PAGINATE_BY': 25,

    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M:%S%z',
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',

    'DATE_INPUT_FORMATS': [
        'iso-8601'
    ],
    'TIME_INPUT_FORMATS': [
        'iso-8601'
    ],
    'DATETIME_INPUT_FORMATS': [
        'iso-8601'
    ],

    'COERCE_DECIMAL_TO_STRING': False,

    'EXCEPTION_HANDLER': 'Lunchbreak.exceptions.lunchbreak_exception_handler',

    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],

    'DEFAULT_VERSIONING_CLASS': 'lunch.versioning.HeaderVersioning'
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'qinspect': {
            'handlers': [
                'console'
            ],
            'level': 'DEBUG',
            'propagate': True,
        },
        'lunchbreak': {
            'level': 'DEBUG',
            'handlers': [
                'console',
                'sentry'
            ],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_FROM = 'Lunchbreak <hi@lunchbreakapp.be>'
