import os

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django_jinja.builtins import DEFAULT_EXTENSIONS

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
PRIVATE_MEDIA_URL = '/private/'
PRIVATE_MEDIA_SERVER = 'private_media.servers.NginxXAccelRedirectServer'
PRIVATE_MEDIA_PERMISSIONS = 'lunch.authentication.PrivateMediaAuthentication'
IMAGEKIT_DEFAULT_FILE_STORAGE = 'private_media.storages.PrivateMediaStorage'

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
    'django_jinja',

    'imagekit',
    'polaroid',

    'django_gocardless',
    'business',
    'customers',
    'lunch',
    'frontend',
]

MIDDLEWARE_CLASSES = (
    'Lunchbreak.middleware.SubdomainHostMiddleWare',
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
TIME_ZONE = 'UTC'
USE_I18N = True  # Translate localisation
USE_L10N = True  # Format localisation
USE_TZ = True

LOGIN_REDIRECT_URL = reverse_lazy('frontend-index')
LOGIN_URL = reverse_lazy('frontend-login')

STATIC_ROOT = os.environ.get(
    'STATIC_ROOT',
    os.path.normpath(os.path.join(BASE_DIR, 'static'))
)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'frontend/img'),
    os.path.join(BASE_DIR, 'frontend/js'),
    os.path.join(BASE_DIR, 'frontend/templates/nunjucks'),
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

GOOGLE_WEB_CREDENTIALS = 'AIzaSyBb7Bd6r-jTG10gEXH3Tmrasd-qJ4oFHlo'
TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'match_extension': None,
            'match_regex': r'^(?!admin/).*',
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'constants': {
                'GOOGLE_WEB_CREDENTIALS': GOOGLE_WEB_CREDENTIALS
            },
            'extensions': DEFAULT_EXTENSIONS + [
                'sass_processor.jinja2.ext.SassSrc',
                'compressor.contrib.jinja2ext.CompressorExtension',
                'jinja2.ext.loopcontrols'
            ],
            'filters': {
                'list_periods': 'frontend.templatetags.filters.list_periods',
                'humanize_weekday': 'frontend.templatetags.filters.humanize_weekday',
                'json_weekday_periods': 'frontend.templatetags.filters.json_weekday_periods',
            }
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]

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

    'DATE_FORMAT': 'iso-8601',
    'TIME_FORMAT': 'iso-8601',
    'DATETIME_FORMAT': 'iso-8601',

    'DATE_INPUT_FORMATS': ['iso-8601'],
    'TIME_INPUT_FORMATS': ['iso-8601'],
    'DATETIME_INPUT_FORMATS': ['iso-8601'],

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
    },
}

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_FROM = 'noreply@lunchbreakapp.be'
