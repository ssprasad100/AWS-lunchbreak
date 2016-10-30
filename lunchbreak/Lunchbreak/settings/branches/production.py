BRANCH = 'master'

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

DB_HOST = 'db'

OPBEAT_RELEASE = True

# TODO Add production access token
GOCARDLESS_ENVIRONMENT = 'live'
GOCARDLESS_APP_DOMAIN = 'api.lunchbreakapp.be'
MIDDLEWARE_CLASSES += (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
)
