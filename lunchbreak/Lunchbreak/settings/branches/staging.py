DB_HOST = 'db'

GOCARDLESS_ENVIRONMENT = 'sandbox'
GOCARDLESS_APP_DOMAIN = 'api.staging.lunchbreakapp.be'
MIDDLEWARE_CLASSES += (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
)

ALLOWED_HOSTS = [
    'staging.lunchbreakapp.be',
    'www.staging.lunchbreakapp.be',
    'api.staging.lunchbreakapp.be',
]

APNS_HOST = 'gateway.sandbox.push.apple.com'
APNS_FEEDBACK_HOST = 'feedback.sandbox.push.apple.com'
