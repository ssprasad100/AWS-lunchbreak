GOCARDLESS_ENVIRONMENT = 'sandbox'
GOCARDLESS_APP_DOMAIN = 'api.staging.lunchbreakapp.be'

PLIVO_WEBHOOK_URL = 'https://api.staging.lunchbreak.io/sms/plivo'
TWILIO_WEBHOOK_URL = 'https://api.staging.lunchbreak.io/sms/twilio'

ALLOWED_HOSTS = [
    'staging.lunchbreakapp.be',
    'www.staging.lunchbreakapp.be',
    'api.staging.lunchbreakapp.be',

    'staging.lunchbreak.io',
    'www.staging.lunchbreak.io',
    'api.staging.lunchbreak.io',
]

REDIRECTED_HOSTS = {
    'staging.lunchbreakapp.be': 'www.staging.lunchbreak.io',
    'www.staging.lunchbreakapp.be': 'www.staging.lunchbreak.io',
}

RAVEN_ENVIRONMENT = 'staging'

PAYCONIQ_WEBHOOK_DOMAIN = 'api.staging.lunchbreak.io'
