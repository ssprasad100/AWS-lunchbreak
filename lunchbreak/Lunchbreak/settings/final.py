import os

from django_jinja.builtins import DEFAULT_EXTENSIONS

ALLOWED_HOSTS = globals().get(
    'ALLOWED_HOSTS',
    os.environ.get(
        'ALLOWED_HOSTS',
        []
    )
)

if HOST not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(HOST)

DB_NAME = globals().get(
    'DB_NAME',
    os.environ.get(
        'DB_NAME',
        'LB_%s' % BRANCH
    )
)
DB_USER = globals().get(
    'DB_USER',
    os.environ.get(
        'DB_USER',
        DB_NAME
    )
)
DB_PASS = globals().get(
    'DB_PASS',
    os.environ.get(
        'DB_PASS',
        DB_NAME
    )
)
DB_HOST = globals().get(
    'DB_HOST',
    os.environ.get(
        'DB_HOST',
        '127.0.0.1'
    )
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': DB_HOST,
        'PORT': '3306'
    }
}

GOOGLE_CLOUD_SECRET = globals().get(
    'GOOGLE_CLOUD_SECRET',
    os.environ.get(
        'GOOGLE_CLOUD_SECRET'
    )
)

GOOGLE_WEB_CREDENTIALS = globals().get(
    'GOOGLE_WEB_CREDENTIALS',
    os.environ.get(
        'GOOGLE_WEB_CREDENTIALS'
    )
)

BUSINESS_APNS_CERTIFICATE = globals().get(
    'BUSINESS_APNS_CERTIFICATE',
    os.environ.get(
        'BUSINESS_APNS_CERTIFICATE'
    )
)

CUSTOMERS_APNS_CERTIFICATE = globals().get(
    'CUSTOMERS_APNS_CERTIFICATE',
    os.environ.get(
        'CUSTOMERS_APNS_CERTIFICATE'
    )
)

PUSH_NOTIFICATIONS_SETTINGS = {
    'GCM_API_KEY': GOOGLE_CLOUD_SECRET,
    'APNS_CERTIFICATE': CUSTOMERS_APNS_CERTIFICATE,
}


# GoCardless settings
GOCARDLESS = {
    'access_token': globals().get(
        'GOCARDLESS_ACCESS_TOKEN',
        os.environ.get(
            'GOCARDLESS_ACCESS_TOKEN'
        )
    ),
    'environment': globals().get(
        'GOCARDLESS_ENVIRONMENT',
        os.environ.get(
            'GOCARDLESS_ENVIRONMENT'
        )
    ),
    'webhook': {
        'secret': globals().get(
            'GOCARDLESS_WEBHOOK_SECRET',
            os.environ.get(
                'GOCARDLESS_WEBHOOK_SECRET'
            )
        ),
    },
    'app': {
        'merchant': {
            'exchange_domain': globals().get(
                'GOCARDLESS_APP_EXCHANGE_DOMAIN',
                os.environ.get(
                    'GOCARDLESS_APP_EXCHANGE_DOMAIN'
                )
            ),
        },
        'client_id': globals().get(
            'GOCARDLESS_APP_CLIENT_ID',
            os.environ.get(
                'GOCARDLESS_APP_CLIENT_ID'
            )
        ),
        'client_secret': globals().get(
            'GOCARDLESS_APP_CLIENT_SECRET',
            os.environ.get(
                'GOCARDLESS_APP_CLIENT_SECRET'
            )
        ),
        'oauth_baseurl': {
            'live': 'https://connect.gocardless.com',
            'sandbox': 'https://connect-sandbox.gocardless.com'
        },
        'webhook': {
            'secret': globals().get(
                'GOCARDLESS_APP_WEBHOOK_SECRET',
                os.environ.get(
                    'GOCARDLESS_APP_WEBHOOK_SECRET'
                )
            )
        },
        'redirect': {
            'success': 'lunchbreakstore://gocardless/redirect/success',
            'error': 'lunchbreakstore://gocardless/redirect/error'
        }
    }
}


SMS = {
    'phone': '+32466900406',
    'text_template': '{pin} is je Lunchbreak authenticatie code, welkom!',
    'plivo': {
        'auth_id': globals().get(
            'PLIVO_AUTH_ID',
            os.environ.get(
                'PLIVO_AUTH_ID'
            )
        ),
        'auth_token': globals().get(
            'PLIVO_AUTH_TOKEN',
            os.environ.get(
                'PLIVO_AUTH_TOKEN'
            )
        )
    }
}

OPBEAT = {
    'ORGANIZATION_ID': '5d9db7394a424d27b704ace52cf4f9ef',
    'APP_ID': globals().get(
        'OPBEAT_APP_ID',
        os.environ.get(
            'OPBEAT_APP_ID'
        )
    ),
    'SECRET_TOKEN': globals().get(
        'OPBEAT_SECRET_TOKEN',
        os.environ.get(
            'OPBEAT_SECRET_TOKEN'
        )
    ),
}

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'APP_DIRS': True,
        'DIRS': [],
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
            'constants': {
                'GOOGLE_WEB_CREDENTIALS': GOOGLE_WEB_CREDENTIALS
            },
            'globals': {
                'url_query': 'frontend.templatetags.globals.url_query'
            },
            'extensions': DEFAULT_EXTENSIONS + [
                'sass_processor.jinja2.ext.SassSrc',
                'compressor.contrib.jinja2ext.CompressorExtension',
            ],
            'filters': {
                'list_periods': 'frontend.templatetags.filters.list_periods',
                'humanize_weekday': 'frontend.templatetags.filters.humanize_weekday',
                'json_weekday_periods': 'frontend.templatetags.filters.json_weekday_periods',
            },
            'match_extension': '.html',
            'app_dirname': 'jinja2',
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
