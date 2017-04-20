import uuid
from decimal import Decimal

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _
from payconiq import Transaction as PayconiqTransaction


class Merchant(models.Model):

    class Meta:
        verbose_name = _('handelaar')
        verbose_name_plural = _('handelaars')

    def __str__(self):
        return str(self.remote_id)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    remote_id = models.CharField(
        unique=True,
        max_length=24,
        verbose_name=_('payconiq id'),
        help_text=_('ID in Payconiq systeem.')
    )
    access_token = models.TextField(
        verbose_name=_('toegangstoken'),
        help_text=_('Toegangstoken.')
    )


class Transaction(models.Model):

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
        (UNKNOWN, _('Onbekend')),
        (TIMEDOUT, _('Verlopen')),
        (CANCELED, _('Geannuleerd')),
        (FAILED, _('Gefaald')),
        (SUCCEEDED, _('Succesvol')),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    remote_id = models.CharField(
        unique=True,
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
    status = models.CharField(
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
            domain='api.andreas.cloock.be',
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
        transaction = cls.objects.create(
            amount=amount,
            currency=currency,
            merchant=merchant
        )
        try:
            remote_id = PayconiqTransaction.start(
                amount=amount,
                merchant_token=merchant.access_token,
                currency=currency,
                webhook_url=transaction.webhook_url
            )
            transaction.remote_id = remote_id
            transaction.save()
            return transaction
        except Exception:
            transaction.delete()
            raise
