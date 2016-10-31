
from random import randint

import plivo
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from .conf import (EXPIRY_TIME, MAX_TRIES, PHONE, PLIVO_AUTH_ID,
                   PLIVO_AUTH_TOKEN, TEXT_TEMPLATE, TIMEOUT)
from .exceptions import (PinExpired, PinIncorrect, PinTimeout,
                         PinTriesExceeded, SmsException)


class Phone(models.Model):
    phone = PhoneNumberField(
        unique=True
    )
    pin = models.CharField(
        max_length=6,
        blank=True
    )
    tries = models.PositiveIntegerField(
        default=0
    )

    last_message = models.DateTimeField(
        null=True,
        blank=True
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def confirmed(self):
        return self.confirmed_at is not None

    @classmethod
    def register(cls, phone):
        instance, created = cls.objects.get_or_create(
            phone=phone
        )
        instance.send_pin()
        return instance, created

    @staticmethod
    def random_pin():
        pin = ''
        for i in range(6):
            pin += str(randint(0, 9))
        return pin

    def send_pin(self, new_pin=True):
        if self.last_message is not None:
            timeout = self.last_message.replace(
                tzinfo=timezone.utc
            ) + TIMEOUT
            if timezone.now() < timeout:
                raise PinTimeout()

        if new_pin:
            self.new_pin()

        api = plivo.RestAPI(
            PLIVO_AUTH_ID,
            PLIVO_AUTH_TOKEN
        )
        params = {
            'src': PHONE,
            'dst': str(self.phone),
            'text': TEXT_TEMPLATE.format(
                pin=self.pin
            ),
            'method': 'POST'
        }
        status, details = api.send_message(params)
        self.last_message = timezone.now()
        self.save()
        if status != 202:
            raise SmsException(details)

    def new_pin(self, save=True):
        self.pin = self.random_pin()
        self.tries = 0
        self.expires_at = timezone.now() + EXPIRY_TIME

        if save:
            self.save()

    def confirm(self, save=True):
        self.confirmed_at = timezone.now()
        if save:
            self.save()

    def reset(self, save=True):
        self.pin = ''
        self.expires_at = None
        if save:
            self.save()

    def is_valid(self, pin, raise_exception=True):
        if self.tries >= MAX_TRIES:
            if raise_exception:
                raise PinTriesExceeded()
            return False

        # In case the pin is not a string, prepend it with zeros
        try:
            pin = '{:06d}'.format(int(pin))
        except (ValueError, TypeError):
            self.tries += 1
            self.save()
            if raise_exception:
                raise PinIncorrect()
            return False

        if not pin or not self.pin or self.pin != pin:
            self.tries += 1
            self.save()
            if raise_exception:
                raise PinIncorrect()
            return False

        if self.expires_at is None or self.expires_at < timezone.now():
            if raise_exception:
                raise PinExpired()
            return False

        self.confirm(save=False)
        self.reset()

        return True

    def __str__(self):
        return str(self.phone)
