from decimal import Decimal

from business.models import Staff
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django_gocardless.config import CURRENCY_EUR, PAYMENT_STATUS_PAID_OUT
from django_gocardless.exceptions import (DjangoGoCardlessException,
                                          MerchantAccessError)
from django_gocardless.models import Payment
from lunch.exceptions import LinkingError, NoDeliveryToAddress
from lunch.utils import timezone_for_store
from Lunchbreak.exceptions import LunchbreakException
from Lunchbreak.fields import (MoneyField, RoundingDecimalField,
                               StatusSignalField)
from Lunchbreak.models import StatusSignalModel
from pendulum import Pendulum

from ..config import (ORDER_STATUS_COMPLETED, ORDER_STATUS_DENIED,
                      ORDER_STATUS_PLACED, ORDER_STATUS_STARTED,
                      ORDER_STATUS_WAITING, ORDER_STATUSES,
                      PAYMENT_METHOD_CASH, PAYMENT_METHOD_GOCARDLESS,
                      PAYMENT_METHOD_PAYCONIQ, PAYMENT_METHODS)
from ..exceptions import (CashDisabled, NoPaymentLink, OnlinePaymentRequired,
                          PaymentLinkNotConfirmed, PreorderTimeExceeded)
from .abstract_order import AbstractOrder
from .group_order import GroupOrder
from .payment_link import PaymentLink


class Order(StatusSignalModel, AbstractOrder):

    class Meta:
        verbose_name = _('bestelling')
        verbose_name_plural = _('bestellingen')

    def __str__(self):
        return _('%(user)s, %(store)s op %(receipt)s') % {
            'user': self.user.name,
            'store': self.store,
            'receipt': self.receipt
        }

    placed = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('tijd van plaatsing'),
        help_text=_('Tijdstip waarop de bestelling werd geplaatst.')
    )
    receipt = models.DateTimeField(
        verbose_name=_('tijd afgave'),
        help_text=_('Tijd van afhalen of levering.')
    )
    status = StatusSignalField(
        choices=ORDER_STATUSES,
        default=ORDER_STATUS_PLACED,
        verbose_name=_('status'),
        help_text=_('Status.')
    )
    total = MoneyField(
        default=0,
        verbose_name=_('totale prijs'),
        help_text=_('Totale prijs inclusief korting.')
    )
    total_confirmed = MoneyField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('totale gecorrigeerde prijs'),
        help_text=_(
            'Totale prijs na correctie van de winkel indien een afgewogen '
            'hoeveelheid licht afwijkt van de bestelde hoeveelheid. Dit is '
            'al inclusief het kortingspercentage.'
        )
    )
    discount = RoundingDecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        verbose_name=_('korting'),
        help_text=_('Korting gegeven op deze bestelling.')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('opmerking bij de bestelling'),
        help_text=_('Bv: extra extra mayonaise graag!')
    )
    payment = models.OneToOneField(
        'django_gocardless.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('betaling'),
        help_text=_('Betaling.')
    )
    payment_method = models.IntegerField(
        choices=PAYMENT_METHODS,
        default=PAYMENT_METHOD_CASH,
        verbose_name=_('betalingswijze'),
        help_text=_('Betalingswijze.')
    )
    delivery_address = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('leveringsadres'),
        help_text=_('Leveringsadres.')
    )
    orderedfood = GenericRelation(
        'OrderedFood',
        related_query_name='placed_order',
        verbose_name=_('bestelde etenswaren'),
        help_text=_('Bestelde etenswaren.')
    )
    group_order = models.ForeignKey(
        'GroupOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('groepsbestelling'),
        help_text=_('Groepsbestelling waartoe bestelling behoort.')
    )
    transaction = models.OneToOneField(
        'payconiq.Transaction',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    @cached_property
    def get_placed_display(self):
        return Pendulum.instance(
            self.placed
        ).in_timezone(
            self.store.timezone
        )

    @cached_property
    def get_receipt_display(self):
        return Pendulum.instance(
            self.receipt
        ).in_timezone(
            self.store.timezone
        )

    @cached_property
    def group(self):
        return self.group_order.group \
            if self.group_order is not None else None

    @cached_property
    def total_no_discount(self):
        """Total without discount"""
        if self.discount == Decimal(100):
            total = 0
            orderedfood = self.orderedfood.all()
            for f in orderedfood:
                total += f.total
            return total
        return int(self.total * Decimal(100) / (Decimal(100) - self.discount))

    @cached_property
    def discounted_amount(self):
        """Shortcut for self.total_no_discount - self.total"""
        return self.total_no_discount - self.total

    @property
    def confirmed(self):
        return not self.payment_payconiq \
            or (self.transaction is not None
                and self.transaction.succeeded)

    @property
    def paid(self):
        if self.payment_cash:
            return self.status == ORDER_STATUS_COMPLETED
        elif self.payment_gocardless:
            return self.payment is not None and \
                self.payment.status == PAYMENT_STATUS_PAID_OUT
        else:
            return self.transaction is not None and \
                self.transaction.succeeded

    @property
    def payment_cash(self):
        return self.payment_method == PAYMENT_METHOD_CASH

    @property
    def payment_gocardless(self):
        return self.payment_method == PAYMENT_METHOD_GOCARDLESS

    @property
    def payment_payconiq(self):
        return self.payment_method == PAYMENT_METHOD_PAYCONIQ

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Order, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(Order, self).delete(*args, **kwargs)
        self.update_hard_delete()

    def update_hard_delete(self):
        """Update whether the orderedfood can be deletedself.

        Calls all of the linked OrderedFood's update_hard_delete methods.
        """
        orderedfood_list = self.orderedfood.select_related(
            'original',
        ).prefetch_related(
            'ingredients',
            'order',
        ).all()

        for orderedfood in orderedfood_list:
            orderedfood.update_hard_delete()

    def clean_placed(self):
        if self.placed is None:
            self.placed = timezone.now()
        if self.group is not None \
                and self.placed.date() == self.receipt.date() \
                and self.group.deadline <= self.placed.time():
            raise PreorderTimeExceeded(
                '{} == {} and {} <= {}'.format(
                    self.placed.date(),
                    self.receipt.date(),
                    self.group.deadline,
                    self.placed.time()
                )
            )

    def clean_status(self):
        if self.group_order is not None \
                and self.group_order.status in [ORDER_STATUS_WAITING, ORDER_STATUS_COMPLETED] \
                and self.group_order.status != self.status:
            # This will also change the status on all of the orders
            self.group_order.status = ORDER_STATUS_STARTED
            self.group_order.save()

    def clean_total(self):
        self.total = 0
        orderedfood = self.orderedfood.all()
        for f in orderedfood:
            self.total += f.total

        if self.group is not None:
            self.discount = self.group.discount

        self.total *= (Decimal(100) - self.discount) / Decimal(100)
        self.total = int(self.total)

    def clean_delivery_address(self):
        if self.delivery_address is not None:
            if self.group is not None:
                raise LunchbreakException(
                    _(
                        'Er kan geen leveringsadres gegeven worden als een '
                        'bestelling op een groep is geplaatst.'
                    )
                )

            is_user_address = self.user.address_set.filter(
                id=self.delivery_address.id
            ).exists()

            if not is_user_address:
                raise LinkingError()

            if not self.store.delivers_to(self.delivery_address):
                raise NoDeliveryToAddress()

    def clean_receipt(self):
        if self.status == ORDER_STATUS_PLACED:
            if self.group is not None:
                self.receipt = Pendulum.instance(
                    self.receipt
                ).with_time(
                    hour=self.group_order.receipt.hour,
                    minute=self.group_order.receipt.minute,
                    second=self.group_order.receipt.second
                )
                self.store.is_open(
                    self.receipt,
                    now=self.placed,
                    ignore_wait=True
                )
            elif self.delivery_address is None:
                if self.receipt is None:
                    raise LunchbreakException(
                        _('Er moet een tijdstip voor het ophalen opgegeven worden.')
                    )
                if self.pk is None or 'receipt' in self.get_dirty_fields():
                    self.receipt = timezone_for_store(
                        value=self.receipt,
                        store=self.store
                    )
                self.store.is_open(
                    self.receipt,
                    now=self.placed
                )

            if isinstance(self.receipt, Pendulum):
                self.receipt = self.receipt._datetime

    def clean_payment_method(self):
        if self.payment_gocardless:
            try:
                paymentlink = PaymentLink.objects.get(
                    user=self.user,
                    store=self.store
                )
                if not paymentlink.redirectflow.is_completed:
                    raise PaymentLinkNotConfirmed()
            except PaymentLink.DoesNotExist:
                if self.pk is None:
                    raise NoPaymentLink()
                self.payment_method = PAYMENT_METHOD_CASH
                self.user.notify(
                    _(
                        'Er liep iets fout bij de online betaling. Gelieve '
                        'contant te betalen bij het ophalen.'
                    )
                )
        elif self.payment_cash:
            if not self.store.cash_enabled:
                raise CashDisabled()

            if self.pk is None \
                    and self.group is not None \
                    and self.group.payment_online_only \
                    and (
                        self.store.staff.gocardless_ready
                        or self.store.staff.payconiq_ready
                    ):
                raise OnlinePaymentRequired()

    def clean_group_order(self):
        if self.group is not None:
            if self.group.store != self.store:
                raise LinkingError(
                    _('De winkel van de groep moet dezelde zijn als die van de bestelling.')
                )
            if not self.group.members.filter(id=self.user_id).exists():
                raise LinkingError(
                    _('Je kan enkel bestellen bij groepen waartoe je behoort.')
                )

    def create_payment(self):
        if self.payment_gocardless:
            try:
                paymentlink = self.user.paymentlink_set.select_related(
                    'redirectflow__mandate'
                ).get(
                    store=self.store
                )

                if paymentlink.redirectflow.is_completed:
                    mandate = paymentlink.redirectflow.mandate
                    self.payment = Payment.create(
                        given={
                            'amount': self.total,
                            'currency': CURRENCY_EUR,
                            'links': {
                                'mandate': mandate
                            },
                            'description': _(
                                'Lunchbreak bestelling #%(order_id)s bij %(store)s.'
                            ) % {
                                'order_id': self.id,
                                'store': self.store.name
                            }
                        }
                    )
                    self.save()
                    return
            except MerchantAccessError as e:
                merchant = self.store.staff.gocardless
                if merchant is not None:
                    merchant.delete()
                    self.store.staff.notify(
                        _('GoCardless account ontkoppelt wegens fout.')
                    )
            except (PaymentLink.DoesNotExist, DjangoGoCardlessException):
                pass
            # Could not create payment
            if paymentlink is not None:
                paymentlink.delete()
            self.payment_method = PAYMENT_METHOD_CASH
            self.user.notify(
                _(
                    'Er liep iets fout bij de online betaling. Gelieve '
                    'contant te betalen bij het ophalen.'
                )
            )
            self.save()

    @classmethod
    def created(cls, sender, order, **kwargs):
        Staff.objects.filter(
            store_id=order.store_id
        ).notify(
            _('Er is een nieuwe bestelling binnengekomen!')
        )

        if order.group is not None:
            group_order, created = GroupOrder.objects.get_or_create(
                group=order.group,
                date=order.receipt.date()
            )

    @classmethod
    def waiting(cls, sender, order, **kwargs):
        order.user.notify(
            'Je bestelling bij {store} ligt klaar!'.format(
                store=order.store.name
            )
        )

    @classmethod
    def completed(cls, sender, order, **kwargs):
        order.create_payment()
        order.update_hard_delete()

    @classmethod
    def denied(cls, sender, order, **kwargs):
        if order.confirmed:
            order.user.notify(
                _('Je bestelling werd spijtig genoeg geweigerd!')
            )
        order.update_hard_delete()

    @classmethod
    def not_collected(cls, sender, order, **kwargs):
        order.create_payment()
        order.update_hard_delete()

    @classmethod
    def deny_order(cls, transaction):
        """Deny the order with the given transaction."""
        order = Order.objects.get(
            transaction=transaction
        )
        order.status = ORDER_STATUS_DENIED
        order.save()

    @classmethod
    def transaction_timedout(cls, sender, transaction, **kwargs):
        cls.deny_order(transaction=transaction)

    @classmethod
    def transaction_canceled(cls, sender, transaction, **kwargs):
        cls.deny_order(transaction=transaction)

    @classmethod
    def transaction_failed(cls, sender, transaction, **kwargs):
        cls.deny_order(transaction=transaction)

    @classmethod
    def transaction_succeeded(cls, sender, transaction, **kwargs):
        from .temporary_order import TemporaryOrder

        order = Order.objects.get(
            transaction=transaction
        )
        TemporaryOrder.objects.filter(
            user=order.user
        ).delete()
