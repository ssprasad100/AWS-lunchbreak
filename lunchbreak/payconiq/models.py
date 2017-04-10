import uuid

import payconiq
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _
from payconiq import Transaction as PayconiqTransaction
from decimal import Decimal


class Merchant(models.Model):

    class Meta:
        verbose_name = _('merchant')
        verbose_name_plural = _('merchants')

    def __str__(self):
        return str(self.remote_id)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    remote_id = models.CharField(
        unique=True,
        max_length=24
    )
    access_token = models.TextField()


class Transaction(models.Model):

    class Meta:
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')

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

    TIMEDOUT = 'TIMEDOUT'
    CANCELED = 'CANCELED'
    FAILED = 'FAILED'
    SUCCEEDED = 'SUCCEEDED'
    STATUSES = (
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
        max_length=24
    )
    amount = models.PositiveIntegerField()
    currency = models.CharField(
        max_length=3,
        default=EUR,
        choices=CURRENCIES
    )
    status = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        choices=STATUSES
    )
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE
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
        remote_id = PayconiqTransaction.start(
            amount=amount,
            merchant_token=merchant.access_token,
            currency=currency,
            webhook_url=transaction.webhook_url
        )
        transaction.remote_id = remote_id
        transaction.save()
        return transaction
