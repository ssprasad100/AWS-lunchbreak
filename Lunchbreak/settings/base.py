import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MEDIA_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'media'))
MEDIA_URL = '/media/'
PRIVATE_MEDIA_ROOT = '/var/media/lunchbreak'
PRIVATE_MEDIA_URL = '/private/'
PRIVATE_MEDIA_SERVER = 'private_media.servers.NginxXAccelRedirectServer'
PRIVATE_MEDIA_PERMISSIONS = 'lunch.authentication.PrivateMediaAuthentication'
IMAGEKIT_DEFAULT_FILE_STORAGE = 'private_media.storages.PrivateMediaStorage'


SECRET_KEY = 'e2a86@j!uc5@z^yu=%n9)6^%w+-(pk8a6@^i!vnvxe^-w%!q8('

DEBUG = False
TEMPLATE_DEBUG = True
SSL = True

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'push_notifications',
    'rest_framework',
    'opbeat.contrib.django',
    'private_media',

    'imagekit',
    'polaroid',

    'business',
    'customers',
    'lunch',
)

MIDDLEWARE_CLASSES = (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

)

ROOT_URLCONF = 'Lunchbreak.urls'

WSGI_APPLICATION = 'Lunchbreak.wsgi.application'

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
)

LANGUAGE_CODE = 'nl-be'
TIME_ZONE = 'Europe/Brussels'
USE_I18N = True  # Translate localisation
USE_L10N = True  # Format localisation
USE_TZ = False

DATE_FORMAT = '%Y-%m-%d'
DATE_INPUT_FORMATS = (
    DATE_FORMAT,
)

TIME_FORMAT = '%H:%M:%S'
TIME_INPUT_FORMATS = (
    TIME_FORMAT,
)

DATETIME_FORMAT = '%s %s' % (DATE_FORMAT, TIME_FORMAT,)
DATETIME_INPUT_FORMATS = (
    DATETIME_FORMAT,
)

STATIC_RELATIVE = '/static/'
STATIC_ROOT = BASE_DIR + STATIC_RELATIVE
STATIC_URL = '/static/'
TEMPLATE_DIRS = (
    BASE_DIR + '/business/templates/',
)

APPEND_SLASH = True

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

    'DATE_FORMAT': DATE_FORMAT,
    'TIME_FORMAT': TIME_FORMAT,
    'DATETIME_FORMAT': DATETIME_FORMAT,

    'DATE_INPUT_FORMATS': list(DATE_INPUT_FORMATS),
    'TIME_INPUT_FORMATS': list(TIME_INPUT_FORMATS),
    'DATETIME_INPUT_FORMATS': list(DATETIME_INPUT_FORMATS),

    'COERCE_DECIMAL_TO_STRING': False,

    'EXCEPTION_HANDLER': 'Lunchbreak.exceptions.lunchbreakExceptionHandler',

    'TEST_REQUEST_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],

    'DEFAULT_VERSIONING_CLASS': 'lunch.versioning.HeaderVersioning'
}

OPBEAT = {
    'ORGANIZATION_ID': '308fe549a8c042429061395a87bb662a',
    'APP_ID': 'a475a69ed8',
    'SECRET_TOKEN': 'e2e3be25fe41c9323f8f4384549d7c22f8c2422e',
    'DEBUG': False
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['opbeat'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'opbeat': {
            'level': 'ERROR',
            'class': 'opbeat.contrib.django.handlers.OpbeatHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'opbeat': {
            'level': 'WARN',
            'handlers': ['console'],
            'propagate': False,
        },
        'opbeat.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'M8cDQH8m3WLstEfLuKphqCalsy5eSJyW5xtQIQLd8viPPM9tfyQimqCMiBxF7CN9owMp80STdM7cdepLcPCQhIPmNJeOhE4yTr2pIcUa1mmreywzcRactiNQVAo1gy9b'
EMAIL_HOST_PASSWORD = 'JmxxhBcM45A4Phth3SzMa0Lqfyd2qRgvT7a4aGnrHz8yTROmQL'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_FROM = 'noreply@lunchbreakapp.be'

TESTING = False
