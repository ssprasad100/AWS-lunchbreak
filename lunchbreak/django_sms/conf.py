from datetime import timedelta

from django.conf import settings as django_settings

settings = getattr(django_settings, 'SMS', {})
EXPIRY_TIME = settings.get(
    'expiry_time',
    timedelta(minutes=15)
)
TIMEOUT = settings.get(
    'timeout',
    timedelta(minutes=1, seconds=30)
)
MAX_TRIES = settings.get(
    'max_tries',
    3
)
# '+32123456789'
PHONE = settings['phone']
# 'Hi, here is your code: {code}.'
TEXT_TEMPLATE = settings['text_template']

PLIVO_SETTINGS = settings['plivo']
PLIVO_AUTH_ID = PLIVO_SETTINGS['auth_id']
PLIVO_AUTH_TOKEN = PLIVO_SETTINGS['auth_token']
