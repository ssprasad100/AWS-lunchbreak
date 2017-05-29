GOCARDLESS_ENVIRONMENT = 'live'
GOCARDLESS_APP_DOMAIN = 'api.lunchbreakapp.be'

PLIVO_WEBHOOK_URL = 'https://api.lunchbreak.io/sms/plivo'
TWILIO_WEBHOOK_URL = 'https://api.lunchbreak.io/sms/twilio'

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
PAYCONIQ_ENVIRONMENT = 'production'
