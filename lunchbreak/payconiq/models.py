import uuid
from decimal import Decimal

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _
from Lunchbreak.exceptions import LunchbreakException
from Lunchbreak.models import StatusSignalModel
from payconiq import Transaction as PayconiqTransaction
from payconiq import get_webhook_domain

from .fields import StatusSignalCharField
from .signals import (transaction_canceled, transaction_failed,
                      transaction_succeeded, transaction_timedout)
from .utils import generate_web_signature


class Merchant(models.Model):

    class Meta:
        verbose_name = _('handelaar')
        verbose_name_plural = _('handelaars')

    def __str__(self):
        return self.name

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        unique=True,
        max_length=191,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )
    remote_id = models.CharField(
        unique=True,
        max_length=24,
        verbose_name=_('payconiq merchant id'),
        help_text=_('Merchant ID in Payconiq systeem.')
    )
    access_token = models.TextField(
        verbose_name=_('toegangstoken'),
        help_text=_(
            'Geheime toegangstoken voor backend transactions, ook wel access '
            'token of auth token genoemd'
        )
    )
    widget_token = models.UUIDField(
        verbose_name=_('widget token'),
        help_text=_(
            'Widget token voor web widget gebruik, ook wel online key of '
            'secret key genoemd.'
        )
    )

    def generate_web_signature(self, webhook_id, currency, amount):
        return generate_web_signature(
            merchant_id=self.remote_id,
            webhook_id=webhook_id,
            currency=currency,
            amount=amount,
            widget_token=self.widget_token
        )


class Transaction(StatusSignalModel):

    class Meta:
        verbose_name = _('transactie')
        verbose_name_plural = _('transacties')

    def __str__(self):
        return '{amount} {currency}{status}'.format(
            amount=(
                Decimal(self.amount) / Decimal(100)
            ).quantize(
                Decimal('0.01')
            ),
            currency=self.currency,
            status=' ' + self.get_status_display()
            if self.status is not None else ''
        )

    EUR = 'EUR'
    CURRENCIES = (
        (EUR, EUR),
    )

    UNKNOWN = 'UNKNOWN'
    TIMEDOUT = 'TIMEDOUT'
    CANCELED = 'CANCELED'
    FAILED = 'FAILED'
    SUCCEEDED = 'SUCCEEDED'
    STATUSES = (
        (UNKNOWN, _('Onbekend'), None),
        (TIMEDOUT, _('Verlopen'), transaction_timedout),
        (CANCELED, _('Geannuleerd'), transaction_canceled),
        (FAILED, _('Gefaald'), transaction_failed),
        (SUCCEEDED, _('Succesvol'), transaction_succeeded),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    remote_id = models.CharField(
        unique=True,
        blank=False,
        max_length=24,
        verbose_name=_('payconiq id'),
        help_text=_('ID in Payconiq systeem.')
    )
    amount = models.PositiveIntegerField(
        verbose_name=_('bedrag'),
        help_text=_('Bedrag in centen.')
    )
    currency = models.CharField(
        max_length=3,
        default=EUR,
        choices=CURRENCIES,
        verbose_name=_('valuta'),
        help_text=_('Valuta.')
    )
    status = StatusSignalCharField(
        max_length=9,
        default=UNKNOWN,
        choices=STATUSES,
        verbose_name=_('status'),
        help_text=_('Status.')
    )
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        verbose_name=_('handelaar'),
        help_text=_('Handelaar.')
    )

    @property
    def webhook_url(self):
        return '{protocol}://{domain}{path}'.format(
            protocol='https' if settings.SSL else 'http',
            domain=get_webhook_domain(),
            path=reverse('payconiq:webhook')
        )

    @property
    def waiting(self):
        return self.status is None

    @property
    def unknown(self):
        return self.status == self.UNKNOWN

    @property
    def timedout(self):
        return self.status == self.TIMEDOUT

    @property
    def canceled(self):
        return self.status == self.CANCELED

    @property
    def failed(self):
        return self.status == self.FAILED

    @property
    def succeeded(self):
        return self.status == self.SUCCEEDED

    @classmethod
    def start(cls, amount, merchant, currency=EUR):
        transaction = cls(
            amount=amount,
            currency=currency,
            merchant=merchant
        )
        remote_id = PayconiqTransaction.start(
            amount=amount,
            merchant_token=merchant.access_token,
            currency=currency,
            webhook_url=transaction.webhook_url
        )
        if not remote_id:
            raise LunchbreakException(
                'Could not create Payconiq transaction.'
            )
        transaction.remote_id = remote_id
        transaction.save()
        return transaction

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
