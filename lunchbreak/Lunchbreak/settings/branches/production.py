ALLOWED_HOSTS = [
    'lunchbreakapp.be',
    'www.lunchbreakapp.be',
    'api.lunchbreakapp.be',

    'lunchbreak.io',
    'www.lunchbreak.io',
    'api.lunchbreak.io',
]

REDIRECTED_HOSTS = {
    'lunchbreakapp.be': 'www.lunchbreak.io',
    'www.lunchbreakapp.be': 'www.lunchbreak.io',
}

VERSION = '2.0.13'
RAVEN_ENVIRONMENT = 'production'
