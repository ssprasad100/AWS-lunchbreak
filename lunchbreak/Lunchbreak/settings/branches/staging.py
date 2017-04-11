GOCARDLESS_ENVIRONMENT = 'sandbox'
GOCARDLESS_APP_DOMAIN = 'api.staging.lunchbreakapp.be'

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

APNS_HOST = 'gateway.sandbox.push.apple.com'
APNS_FEEDBACK_HOST = 'feedback.sandbox.push.apple.com'

RAVEN_ENVIRONMENT = 'staging'
