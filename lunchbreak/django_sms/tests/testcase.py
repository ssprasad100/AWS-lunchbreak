import uuid
from datetime import timedelta

import mock
from django.test.utils import override_settings
from Lunchbreak.tests.testcase import LunchbreakTestCase
from pendulum import Pendulum

from ..models import Message
from ..tasks import send_pin


@override_settings(SMS={
    'text_template': 'Pin: {pin} test template.',
    'max_tries': 3,
    'expiry_time': timedelta(minutes=15),
    'timeout': timedelta(minutes=1, seconds=30),
    'domain': 'http://lunchbreak.does.not.exist',
    'plivo': {
        'phone': '1234',
        'auth_id': 'something',
        'auth_token': 'something',
        'webhook_url': 'something',
    },
    'twilio': {
        'phone': '1234',
        'account_sid': 'something',
        'auth_token': 'something',
        'webhook_url': 'something',
    },
})
class DjangoSmsTestCase(LunchbreakTestCase):

    PHONE = '+32472907605'
    PIN = '123456'
    INVALID_PIN = '654321'

    def setUp(self):
        super().setUp()

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
            message = mock.MagicMock()
            message.sid = 'aa' + str(uuid.uuid4())
            message.status = Message.QUEUED
            message.date_sent = Pendulum.now().isoformat()
            return message

        self.twilio_message.create = create
        self.mock_twilio.return_value = self.twilio_message

        self.plivo_message = mock.MagicMock()
        self.plivo_message.status_code = 202
        self.plivo_message.json_data = {
            'message_uuid': [
                uuid.uuid4(),
            ],
        }
        self.mock_plivo.return_value = self.plivo_message
        self.mock_send_pin.side_effect = send_pin
