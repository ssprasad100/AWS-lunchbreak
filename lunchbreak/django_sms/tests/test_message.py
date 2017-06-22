from twilio.base.exceptions import TwilioRestException

from ..models import Message, Phone
from ..tasks import send_message
from .testcase import DjangoSmsTestCase


class MessageTestCase(DjangoSmsTestCase):

    def setUp(self):
        super().setUp()
        self.phone = Phone.objects.create(
            phone=self.PHONE
        )

    def test_last_confirmed_message(self):
        last_message = Message.objects.create(
            phone=self.phone,
            gateway=Message.TWILIO,
            status=Message.FAILED
        )
        self.phone.last_confirmed_message = last_message
        self.phone.save()

        send_message(
            phone=self.phone,
            body='body'
        )

        self.assertEqual(
            self.mock_plivo.call_count,
            0
        )
        self.assertEqual(
            self.mock_twilio.call_count,
            1
        )
        self.assertEqual(
            Message.objects.all().count(),
            2
        )

        last_message.gateway = Message.PLIVO
        last_message.save()
        self.phone.refresh_from_db()

        self.mock_plivo.reset_mock()
        self.mock_twilio.reset_mock()

        send_message(
            phone=self.phone,
            body='body'
        )

        self.assertEqual(
            self.mock_plivo.call_count,
            1
        )
        self.assertEqual(
            self.mock_twilio.call_count,
            0
        )
        self.assertEqual(
            Message.objects.all().count(),
            3
        )

    def test_failed_twilio(self):
        last_message = Message.objects.create(
            phone=self.phone,
            gateway=Message.TWILIO,
            status=Message.FAILED
        )

        self.plivo_message.status_code = 500
        self.plivo_message.json_data = {
            'some': 'error'
        }

        send_message(
            phone=self.phone,
            body='body'
        )

        self.assertEqual(
            self.mock_plivo.call_count,
            1
        )
        self.assertEqual(
            self.mock_twilio.call_count,
            1
        )
        self.assertEqual(
            Message.objects.all().count(),
            3
        )

        plivo_message = Message.objects.exclude(
            pk=last_message.id
        ).get(
            gateway=Message.PLIVO
        )
        self.assertIn(
            str(self.plivo_message.status_code),
            plivo_message.error
        )
        self.assertIn(
            'some',
            plivo_message.error
        )
        self.assertIn(
            'error',
            plivo_message.error
        )

    def test_failed_plivo(self):
        last_message = Message.objects.create(
            phone=self.phone,
            gateway=Message.PLIVO,
            status=Message.FAILED
        )

        exception = TwilioRestException(
            status=500,
            uri='uri',
            msg='msg',
            code='code',
            method='GET'
        )
        self.mock_twilio.side_effect = exception

        send_message(
            phone=self.phone,
            body='body'
        )

        self.assertEqual(
            self.mock_plivo.call_count,
            1
        )
        self.assertEqual(
            self.mock_twilio.call_count,
            1
        )
        self.assertEqual(
            Message.objects.all().count(),
            3
        )

        twilio_message = Message.objects.exclude(
            pk=last_message.id
        ).get(
            gateway=Message.TWILIO
        )
        self.assertEqual(
            twilio_message.status,
            Message.FAILED
        )

        self.assertIn(
            str(exception.status),
            twilio_message.error
        )
        self.assertIn(
            exception.uri,
            twilio_message.error
        )
        self.assertIn(
            exception.msg,
            twilio_message.error
        )
        self.assertIn(
            exception.code,
            twilio_message.error
        )
        self.assertIn(
            exception.method,
            twilio_message.error
        )
