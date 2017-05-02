from datetime import timedelta

from django.utils import timezone
from freezegun import freeze_time

from ..exceptions import PinExpired, PinIncorrect, PinTimeout, PinTriesExceeded
from ..models import Phone
from .testcase import DjangoSmsTestCase, settings


class PhoneTestCase(DjangoSmsTestCase):

    def test_register(self):
        phone, created = Phone.register(
            phone=self.PHONE
        )
        phone.refresh_from_db()

        # This is a new phone
        self.assertTrue(created)
        # The tries should be set to 0 by default.
        self.assertEqual(
            phone.tries,
            0
        )
        # The phone is unconfirmed.
        self.assertIsNone(phone.confirmed_at)
        # A pin expiration should be set.
        self.assertIsNotNone(phone.expires_at)
        # A creation datetime should be set.
        self.assertIsNotNone(phone.created_at)
        # A new pin should be created.
        self.assertNotEqual(
            phone.pin,
            ''
        )

        now = self.midday.add_timedelta(
            settings['timeout']
        )._datetime
        with freeze_time(now):
            phone2, created = Phone.register(
                phone=self.PHONE
            )
            phone2.refresh_from_db()

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

    def test_timeout(self):
        Phone.register(
            phone=self.PHONE,
        )
        self.assertRaises(
            PinTimeout,
            Phone.register,
            phone=self.PHONE
        )
