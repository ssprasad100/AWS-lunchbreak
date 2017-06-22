import uuid
from random import randint

from django.conf import settings as django_settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from phonenumber_field.modelfields import PhoneNumberField

from .conf import settings
from .exceptions import PinExpired, PinIncorrect, PinTimeout, PinTriesExceeded
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

    last_confirmed_message = models.OneToOneField(
        'Message',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='confirmed_phone',
        verbose_name=_('laatst bevestigd bericht'),
        help_text=_('Bericht dat laatst bevestigd werd.')
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

    @cached_property
    def last_message(self):
        try:
            return self.messages.order_by(
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

    def can_send_pin(self):
        if self.last_message is None or self.last_message.failure:
            return True

        timeout = self.last_message.sent_at.replace(
            tzinfo=timezone.utc
        ) + settings.TIMEOUT
        return not (timezone.now() < timeout)

    def send_pin(self):
        if not self.can_send_pin():
            raise PinTimeout()

        send_pin.delay(
            phone_pk=self.pk
        )

    def reset_pin(self, save=True):
        self.pin = self.random_pin()
        self.tries = 0
        self.expires_at = timezone.now() + settings.EXPIRY_TIME

        if save:
            self.save()

    def confirm(self, save=True):
        self.last_confirmed_message = self.last_message
        self.confirmed_at = timezone.now()
        if save:
            self.save()

    def reset(self, save=True):
        self.pin = ''
        self.expires_at = None
        if save:
            self.save()

    def is_valid(self, pin, raise_exception=True):
        if self.tries >= settings.MAX_TRIES:
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
        return str(self.id)

    PLIVO = 'plivo'
    TWILIO = 'twilio'
    GATEWAYS = (
        (PLIVO, 'Plivo'),
        (TWILIO, 'Twilio'),
    )

    QUEUED = 'queued'
    SENDING = 'sending'
    SENT = 'sent'
    FAILED = 'failed'
    DELIVERED = 'delivered'
    UNDELIVERED = 'undelivered'
    REJECTED = 'rejected'
    STATUSES = (
        (QUEUED, _('In de wachtrij')),
        (SENDING, _('Wordt verzonden')),
        (SENT, _('Verzonden')),
        (FAILED, _('Gefaald')),
        (DELIVERED, _('Afgeleverd')),
        (UNDELIVERED, _('Niet afgeleverd')),
        (REJECTED, _('Afgewezen')),
    )

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid.uuid4,
        verbose_name=_('UUID'),
        help_text=_('UUID.')
    )
    remote_uuid = models.UUIDField(
        null=True,
        verbose_name=_('gateway UUID'),
        help_text=_('UUID bij gateway.')
    )
    phone = models.ForeignKey(
        Phone,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('telefoon'),
        help_text=_('Telefoon.')
    )
    gateway = models.CharField(
        max_length=6,
        choices=GATEWAYS,
        verbose_name=_('gateway'),
        help_text=_('SMS gateway.')
    )
    status = models.CharField(
        max_length=11,
        default=QUEUED,
        choices=STATUSES,
        verbose_name=_('status'),
        help_text=_('Status.')
    )
    sent_at = models.DateTimeField(
        # This allows for overriding it on creation
        # auto_now_add does not allow overriding.
        default=timezone.now,
        blank=True,
        verbose_name=_('verzonden om'),
        help_text=_('Verzonden om.')
    )
    error = models.TextField(
        blank=True,
        verbose_name=_('fout'),
        help_text=_('Fout informatie.')
    )

    @property
    def success(self):
        return self.status == self.DELIVERED

    @property
    def failure(self):
        return self.status in {
            self.FAILED,
            self.UNDELIVERED,
            self.REJECTED,
        }

    @property
    def sid(self):
        assert self.status == self.TWILIO, \
            'Only messages sent via Twilio have an sid.'
        return 'MM' + str(self.remote_uuid)

    def handle_status(self, status):
        self.status = status

        if self.failure:
            self.retry()

        self.save()

    def retry(self):
        assert self.failure, \
            'Only failed messages can be retried.'

        if self.phone.can_send_pin():
            send_pin.delay(
                phone_pk=self.phone_id
            )

    @classmethod
    def get_webhook_uri(cls, gateway):
        if gateway == cls.TWILIO:
            path = reverse('django_sms:twilio')
        else:
            path = reverse('django_sms:plivo')

        return '{protocol}://{domain}{path}'.format(
            protocol='https' if django_settings.SSL else 'http',
            domain=settings.DOMAIN,
            path=path
        )
