from datetime import timedelta

from django.conf import settings as django_settings

settings = getattr(django_settings, 'SMS', {})
EXPIRY_TIME = settings.get(
    'expiry_time',
    timedelta(minutes=15)
)
TIMEOUT = settings.get(
    'timeout',
    timedelta(seconds=30)
)
RETRY_TIMEOUT = settings.get(
    'retry_timeout',
    timedelta(hours=2)
)
MAX_TRIES = settings.get(
    'max_tries',
    3
)
# 'Hi, here is your code: {code}.'
TEXT_TEMPLATE = settings['text_template']
DOMAIN = settings['domain']

PLIVO_SETTINGS = settings['plivo']
PLIVO_PHONE = PLIVO_SETTINGS['phone']
PLIVO_AUTH_ID = PLIVO_SETTINGS['auth_id']
PLIVO_AUTH_TOKEN = PLIVO_SETTINGS['auth_token']
PLIVO_WEBHOOK_URL = PLIVO_SETTINGS['webhook_url']

TWILIO_SETTINGS = settings['twilio']
TWILIO_PHONE = TWILIO_SETTINGS['phone']
TWILIO_ACCOUNT_SID = TWILIO_SETTINGS['account_sid']
TWILIO_AUTH_TOKEN = TWILIO_SETTINGS['auth_token']
TWILIO_WEBHOOK_URL = TWILIO_SETTINGS['webhook_url']
