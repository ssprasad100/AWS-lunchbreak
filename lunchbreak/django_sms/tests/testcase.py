import uuid
from datetime import timedelta

import mock
from django.test.utils import override_settings
from Lunchbreak.tests.testcase import LunchbreakTestCase
from pendulum import Pendulum

from .. import conf
from ..models import Message
from ..tasks import send_pin

settings = {
    'text_template': 'Pin: {pin} test template.',
    'max_tries': 3,
    'expiry_time': timedelta(minutes=15),
    'timeout': timedelta(minutes=1, seconds=30),
    'domain': 'http://lunchbreak.does.not.exist',
    'plivo': {
        'phone': '1234',
        'auth_id': 'something',
        'auth_token': 'something',
    },
    'twilio': {
        'phone': '1234',
        'account_sid': 'something',
        'auth_token': 'something',
    },
}


@override_settings(SMS=settings)
class DjangoSmsTestCase(LunchbreakTestCase):

    PHONE = '+32472907605'
    PIN = '123456'
    INVALID_PIN = '654321'

    def setUp(self):
        super().setUp()

        conf.EXPIRY_TIME = settings.get(
            'expiry_time',
            timedelta(minutes=15)
        )
        conf.TIMEOUT = settings.get(
            'timeout',
            timedelta(seconds=30)
        )
        conf.RETRY_TIMEOUT = settings.get(
            'retry_timeout',
            timedelta(hours=2)
        )
        conf.MAX_TRIES = settings.get(
            'max_tries',
            3
        )
        # 'Hi, here is your code: {code}.'
        conf.TEXT_TEMPLATE = settings['text_template']
        conf.DOMAIN = settings['domain']

        conf.PLIVO_SETTINGS = settings['plivo']
        conf.PLIVO_PHONE = conf.PLIVO_SETTINGS['phone']
        conf.PLIVO_AUTH_ID = conf.PLIVO_SETTINGS['auth_id']
        conf.PLIVO_AUTH_TOKEN = conf.PLIVO_SETTINGS['auth_token']

        conf.TWILIO_SETTINGS = settings['twilio']
        conf.TWILIO_PHONE = conf.TWILIO_SETTINGS['phone']
        conf.TWILIO_ACCOUNT_SID = conf.TWILIO_SETTINGS['account_sid']
        conf.TWILIO_AUTH_TOKEN = conf.TWILIO_SETTINGS['auth_token']

        # Patch requests
        patcher_send_pin = mock.patch('django_sms.models.send_pin.delay')
        patcher_plivo = mock.patch('plivo.Message.send')
        patcher_twilio = mock.patch(
            'twilio.rest.Client.messages',
            new_callable=mock.PropertyMock
        )

        self.addCleanup(patcher_send_pin.stop)
        self.addCleanup(patcher_plivo.stop)
        self.addCleanup(patcher_twilio.stop)

        self.mock_send_pin = patcher_send_pin.start()
        self.mock_plivo = patcher_plivo.start()
        self.mock_twilio = patcher_twilio.start()

        self.twilio_message = mock.MagicMock()

        def create(*args, **kwargs):
            return {
                'sid': 'aa' + str(uuid.uuid4()),
                'status': Message.QUEUED,
                'date_sent': Pendulum.now().isoformat(),
            }
        self.twilio_message.create = create
        self.mock_twilio.return_value = self.twilio_message

        self.plivo_message = mock.MagicMock()
        self.plivo_message.status_code = 202
        self.plivo_message.json_data = {
            'message_uid': [
                uuid.uuid4(),
            ],
        }
        self.mock_plivo.return_value = self.plivo_message
        self.mock_send_pin.side_effect = send_pin
