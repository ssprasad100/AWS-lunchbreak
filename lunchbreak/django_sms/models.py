
from random import randint

import plivo
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from phonenumber_field.modelfields import PhoneNumberField

from .conf import (DOMAIN, EXPIRY_TIME, GATEWAY_TWILIO, GATEWAYS, MAX_TRIES,
                   MESSAGE_STATUS_QUEUED, MESSAGE_STATUSES, PLIVO_AUTH_ID,
                   PLIVO_AUTH_TOKEN, PLIVO_PHONE, STATUS_DELIVERED,
                   STATUS_FAILED, STATUS_REJECTED, STATUS_UNDELIVERED,
                   TEXT_TEMPLATE, TIMEOUT)
from .exceptions import (PinExpired, PinIncorrect, PinTimeout,
                         PinTriesExceeded, SmsException)
from .tasks import send_pin


class Phone(models.Model):

    class Meta:
        verbose_name = _('telefoon')
        verbose_name_plural = _('telefoons')

    def __str__(self):
        return str(self.phone)

    phone = PhoneNumberField(
        unique=True,
        verbose_name=_('telefoonnummer'),
        help_text=_('Telefoonnummer.')
    )
    pin = models.CharField(
        max_length=6,
        blank=True,
        verbose_name=_('PIN code'),
        help_text=_('PIN code.')
    )
    tries = models.PositiveIntegerField(
        default=0,
        verbose_name=_('pogingen'),
        help_text=_('Aantal keer PIN code geprobeerd.')
    )

    last_message = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('laatst verstuurd bericht'),
        help_text=_('Moment waarop het laatste bericht werd verstuurd.')
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('bevestigd op'),
        help_text=_('Moment waarop er voor het eerste een correcte PIN code werd ingegeven.')
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('PIN code vervalt op'),
        help_text=_('Moment waarop PIN code vervalt.')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('aangemaakt op'),
        help_text=_('Moment waarop dit telefoonnummer werd toegevoegd.')
    )

    @property
    def confirmed(self):
        return self.confirmed_at is not None

    @cached_property
    def last_messsage(self):
        try:
            return Message.objects.filter(
                phone_id=self.id
            ).order_by(
                '-sent_at'
            ).first()
        except IndexError:
            return None

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

    def can_retry(self, gateway):
        return self.messages.filter(
            gateway=gateway,

        )

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
            'src': PLIVO_PHONE,
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


class Message(models.Model):

    class Meta:
        verbose_name = _('bericht')
        verbose_name_plural = _('berichten')

    def __str__(self):
        return str(self.uuid)

    id = models.UUIDField(
        primary_key=True,
        editable=False
    )
    phone = models.ForeignKey(
        Phone,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    gateway = models.CharField(
        choices=GATEWAYS
    )
    status = models.CharField(
        default=MESSAGE_STATUS_QUEUED,
        choices=MESSAGE_STATUSES
    )
    sent_at = models.DateTimeField(
        # This allows for overriding it on creation
        # auto_now_add does not allow overriding.
        default=timezone.now,
        blank=True
    )
    error_code = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    @property
    def success(self):
        return self.status == STATUS_DELIVERED

    @property
    def failure(self):
        return self.status in (
            STATUS_FAILED,
            STATUS_UNDELIVERED,
            STATUS_REJECTED,
        )

    @property
    def sid(self):
        assert self.status == GATEWAY_TWILIO, \
            'Only messages sent via Twilio have an sid.'
        return 'MM' + str(self.id)

    def handle_status(self, status):
        self.status = status

        if self.failure:
            self.retry()

        self.save()

    def retry(self):
        assert self.failure, \
            'Only failed messages can be retried.'

        if self.phone.can_retry(self.gateway):
            send_pin.delay(
                phone_pk=self.phone_id
            )

    @staticmethod
    def get_webhook_uri(gateway):
        if gateway == GATEWAY_TWILIO:
            path = reverse('django_sms:twilio')
        else:
            path = reverse('django_sms:plivo')

        return '{protocol}://{domain}{path}'.format(
            protocol='https' if settings.SSL else 'http',
            domain=DOMAIN,
            path=path
        )
