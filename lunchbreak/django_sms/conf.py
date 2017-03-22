from datetime import timedelta

from django.conf import settings as django_settings
from django.utils.translation import ugettext as _

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

TWILIO_SETTINGS = settings['twilio']
TWILIO_PHONE = TWILIO_SETTINGS['phone']
TWILIO_ACCOUNT_SID = TWILIO_SETTINGS['account_sid']
TWILIO_AUTH_TOKEN = TWILIO_SETTINGS['auth_token']

STATUS_QUEUED = 'queued'
STATUS_SENDING = 'sending'
STATUS_SENT = 'sent'
STATUS_FAILED = 'failed'
STATUS_DELIVERED = 'delivered'
STATUS_UNDELIVERED = 'undelivered'
STATUS_REJECTED = 'rejected'
STATUSES = (
    (STATUS_QUEUED, _('In de wachtrij')),
    (STATUS_SENDING, _('Wordt verzonden')),
    (STATUS_SENT, _('Verzonden')),
    (STATUS_FAILED, _('Gefaald')),
    (STATUS_DELIVERED, _('Afgeleverd')),
    (STATUS_UNDELIVERED, _('Niet afgeleverd')),
    (STATUS_REJECTED, _('Afgewezen')),
)

GATEWAY_PLIVO = 'plivo'
GATEWAY_TWILIO = 'twilio'
GATEWAYS = (
    (GATEWAY_PLIVO, 'Plivo'),
    (GATEWAY_TWILIO, 'Twilio'),
)
