"""
Django settings for Lunchbreak project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e2a86@j!uc5@z^yu=%n9)6^%w+-(pk8a6@^i!vnvxe^-w%!q8('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',

	# Plugins
	'rest_framework',
	'opbeat.contrib.django',

	# Lunchbreak
	'lunch',
)

MIDDLEWARE_CLASSES = (
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


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'lunchbreak_development',
		'USER': 'lunchbreak',
		'PASSWORD': 'lunchbreak',
		'HOST': 'localhost',
		'PORT': '3306'
	}
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'nl-be'

TIME_ZONE = 'Europe/Brussels'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = '/home/lunchbreak/public_html/lunchbreak/static/'
STATIC_URL = '/static/'

APPEND_SLASH = False

# Disable the browsable API when it's not in debug mode
REST_FRAMEWORK = {
	'EXCEPTION_HANDLER': 'lunch.exceptions.lunchbreakExceptionHandler'
}

if not DEBUG:
	REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ('rest_framework.renderers.JSONRenderer',)


# Opbeat settings
OPBEAT = {
	'ORGANIZATION_ID': '308fe549a8c042429061395a87bb662a',
	'APP_ID': 'a475a69ed8',
	'SECRET_TOKEN': 'e2e3be25fe41c9323f8f4384549d7c22f8c2422e',
	'DEBUG': True
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
			'formatter': 'verbose'
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
			'level': 'WARNING',
			'handlers': ['opbeat'],
			'propagate': False,
		},
		'opbeat.errors': {
			'level': 'DEBUG',
			'handlers': ['console'],
			'propagate': False,
		},
	},
}
