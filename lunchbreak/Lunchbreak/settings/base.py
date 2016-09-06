import os

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MEDIA_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'media'))
MEDIA_URL = '/media/'
PRIVATE_MEDIA_ROOT = '/media/lunchbreak/'
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
ROOT_URLCONF = 'Lunchbreak.urls.api'
SUBDOMAIN_URLCONFS = {
    None: 'Lunchbreak.urls.frontend',
    'www': 'Lunchbreak.urls.frontend',
    'api': 'Lunchbreak.urls.api',
}

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

LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('nl-be', _('Belgium Dutch')),
    ('en', _('Europe')),
]
TIME_ZONE = 'UTC'
USE_I18N = True  # Translate localisation
USE_L10N = True  # Format localisation
USE_TZ = True

LOGIN_REDIRECT_URL = reverse_lazy('frontend-index')
LOGIN_URL = reverse_lazy('frontend-login')

STATIC_RELATIVE = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, STATIC_RELATIVE)
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
SASS_PROCESSOR_INCLUDE_DIRS = (
    os.path.join(BASE_DIR, 'frontend/mdl/src'),
    os.path.join(BASE_DIR, 'frontend/scss'),
    os.path.join(BASE_DIR, 'frontend/intl-tel-input/src/css'),
)

TEMPLATES = [
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
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'frontend.jinja2.environment'
        }
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

GOOGLE_WEB_CREDENTIALS = 'AIzaSyBb7Bd6r-jTG10gEXH3Tmrasd-qJ4oFHlo'

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = os.environ.get('SENDGRID_USER')
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_FROM = 'noreply@lunchbreakapp.be'

# What APNS certificate to use (development or production)
CERT_TYPE = 'development'

GOCARDLESS = {
    'access_token': 'fGTKM_yaVZ7t-twTQ9uTJWo6Gy6f8nK70kGgjQTr',
    'environment': 'sandbox',
    'app': {
        'redirect_uri': 'https://isoanufkkl.localtunnel.me/gocardless/redirect',
        'client_id': '2J4hQVvc7nIdFkpYvM9luLD7JCJWf6Iwco3W7Hu5yFOcmBPNSzQq1XwXurg-B17i',
        'client_secret': 'u9p1M_5j25uBmGdxTG04E-i_ZnCPERRHQkYFwqYZ3NCwUMyfraS-NJUg63WlJ18w',
        'oauth_baseurl': {
            'live': 'https://connect.gocardless.com',
            'sandbox': 'https://connect-sandbox.gocardless.com'
        },
        'webhook': {
            'secret': 'DpiVqyjEkvDLNDYC-fNIHGQADLpCS_wZfnzrl9LM',
        },
        'redirect': {
            'success': reverse_lazy(
                'frontend-account', kwargs={
                    'status': 'success'
                }
            ),
            'error': reverse_lazy(
                'frontend-account', kwargs={
                    'status': 'error'
                }
            )
        }
    },
    'app_redirect': {
        'success': 'lunchbreakstore://gocardless/redirectflow/success',
        'error': {
            'default': 'lunchbreakstore://gocardless/redirectflow/error',
            'invalid': 'lunchbreakstore://gocardless/redirectflow/error/invalid',
            'incomplete': 'lunchbreakstore://gocardless/redirectflow/error/incomplete',
            'completed': 'lunchbreakstore://gocardless/redirectflow/error/completed',
        }
    },
    'webhook': {
        'secret': 'UqNOZ-Zplk3ODIke8VldT9jKCM4TIkc0AIAFTWAx',
    }
}
