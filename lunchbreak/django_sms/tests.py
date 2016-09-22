from datetime import datetime, timedelta

import mock
from django.test.utils import override_settings
from django.utils import timezone
from Lunchbreak.test import LunchbreakTestCase

from .exceptions import PinExpired, PinIncorrect, PinTimeout, PinTriesExceeded
from .models import Phone

settings = {
    'phone': '1234',
    'text_template': '{pin} is je Lunchbreak authenticatie code, welkom!',
    'max_tries': 3,
    'expiry_time': timedelta(minutes=15),
    'timeout': timedelta(minutes=1, seconds=30),
    'plivo': {
        'auth_id': 'something',
        'auth_token': 'something'
    }
}


@override_settings(SMS=settings)
class SmsTestCase(LunchbreakTestCase):

    PHONE = '+32472907605'
    PIN = '123456'
    INVALID_PIN = '654321'

    @mock.patch('django.utils.timezone.now')
    @mock.patch('plivo.RestAPI.send_message')
    def test_register(self, mock_message, mock_now):
        mock_message.return_value = (
            202,
            'Success'
        )
        mock_now.return_value = datetime.now()
        phone, created = Phone.register(
            phone=self.PHONE
        )

        self.assertTrue(created)
        self.assertEqual(
            phone.tries,
            0
        )
        self.assertIsNone(phone.confirmed_at)
        self.assertIsNotNone(phone.expires_at)
        self.assertIsNotNone(phone.created_at)
        self.assertNotEqual(
            phone.pin,
            ''
        )

        mock_now.return_value = datetime.now().replace(tzinfo=timezone.utc) + settings['timeout']
        phone2, created = Phone.register(
            phone=self.PHONE
        )

        self.assertFalse(created)
        self.assertEqual(
            phone.pk,
            phone2.pk
        )
        self.assertNotEqual(
            phone.pin,
            phone2.pin
        )
        self.assertEqual(
            phone2.tries,
            0
        )
        self.assertIsNone(phone2.confirmed_at)
        self.assertIsNotNone(phone2.created_at)
        self.assertNotEqual(
            phone.expires_at,
            phone2.expires_at
        )

    def test_valid_pin(self):
        expires_at = timezone.now() + settings['expiry_time']

        invalid_pins = [None, '']

        # Test all invalid pins
        for invalid_pin in invalid_pins:
            phone = Phone.objects.create(
                phone=self.PHONE,
                pin=self.PIN,
                expires_at=expires_at
            )

            self.assertRaises(
                PinIncorrect,
                phone.is_valid,
                invalid_pin
            )
            self.assertEqual(
                phone.tries,
                1
            )
            phone.delete()

            if invalid_pin is not None:
                phone = Phone.objects.create(
                    phone=self.PHONE,
                    pin=invalid_pin,
                    expires_at=expires_at
                )

                self.assertRaises(
                    PinIncorrect,
                    phone.is_valid,
                    self.INVALID_PIN
                )
                self.assertEqual(
                    phone.tries,
                    1
                )
                phone.delete()

        phone = Phone.objects.create(
            phone=self.PHONE,
            pin=self.PIN,
            expires_at=expires_at
        )

        self.assertRaises(
            PinIncorrect,
            phone.is_valid,
            self.INVALID_PIN
        )
        self.assertEqual(
            phone.tries,
            1
        )
        phone.delete()

        # Test valid pin
        phone = Phone.objects.create(
            phone=self.PHONE,
            pin=self.PIN,
            expires_at=expires_at
        )
        self.assertTrue(
            phone.is_valid(pin=self.PIN)
        )
        phone.delete()

    def test_expiry_time(self):
        expired_datetime = timezone.now() - settings['expiry_time'] - timedelta(seconds=1)
        phone = Phone.objects.create(
            phone=self.PHONE,
            pin=self.PIN,
            expires_at=expired_datetime
        )
        self.assertRaises(
            PinExpired,
            phone.is_valid,
            self.PIN
        )

    def test_max_tries(self):
        expires_at = timezone.now() + settings['expiry_time']

        phone = Phone.objects.create(
            phone=self.PHONE,
            pin=self.PIN,
            expires_at=expires_at,
            tries=settings['max_tries']
        )
        self.assertRaises(
            PinTriesExceeded,
            phone.is_valid,
            self.PIN
        )

    @mock.patch('plivo.RestAPI.send_message')
    def test_timeout(self, mock_message):
        mock_message.return_value = (
            202,
            'Success'
        )
        Phone.register(
            phone=self.PHONE,
        )
        self.assertRaises(
            PinTimeout,
            Phone.register,
            phone=self.PHONE
        )
