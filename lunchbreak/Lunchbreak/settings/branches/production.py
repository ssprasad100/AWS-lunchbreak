DB_HOST = 'db'

GOCARDLESS_ENVIRONMENT = 'live'
GOCARDLESS_APP_DOMAIN = 'api.lunchbreakapp.be'
MIDDLEWARE_CLASSES += (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
)

ALLOWED_HOSTS = [
    'lunchbreakapp.be',
    'www.lunchbreakapp.be',
    'api.lunchbreakapp.be',

    'lunchbreak.eu',
    'www.lunchbreak.eu',
    'api.lunchbreak.eu',

    'lunchbreak.fr',
    'www.lunchbreak.fr',
    'api.lunchbreak.fr',
]
