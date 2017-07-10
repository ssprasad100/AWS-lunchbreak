from decimal import Decimal

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from Lunchbreak.fields import StatusSignalField
from Lunchbreak.models import StatusSignalModel
from pendulum import Pendulum

from ..config import GROUP_ORDER_STATUSES, ORDER_STATUS_PLACED
from ..tasks import send_group_order_email
from .group import Group


class GroupOrder(StatusSignalModel):

    class Meta:
        unique_together = ('group', 'date',)
        verbose_name = _('groepsbestelling')
        verbose_name_plural = _('groepsbestellingen')

    def __str__(self):
        return _('%(group_name)s %(date)s') % {
            'group_name': self.group.name,
            'date': self.date
        }

    group = models.ForeignKey(
        'Group',
        related_name='group_orders',
        verbose_name=_('groep'),
        help_text=_('Groep.')
    )
    date = models.DateField(
        verbose_name=_('datum'),
        help_text=_('Datum van groepsbestelling.')
    )
    status = StatusSignalField(
        choices=GROUP_ORDER_STATUSES,
        default=ORDER_STATUS_PLACED,
        verbose_name=_('status'),
        help_text=_('Status.')
    )

    @cached_property
    def orders(self):
        return Group.objects.filter(
            id=self.group_id
        ).orders_for(
            timestamp=self.date
        )

    @property
    def total(self):
        if not hasattr(self, '_total'):
            self._calculate_totals()
        return self._total

    @property
    def paid_total(self):
        if not hasattr(self, '_paid_total'):
            self._calculate_totals()
        return self._paid_total

    @property
    def total_no_discount(self):
        """Total without discount"""
        if not hasattr(self, '_total_no_discount'):
            self._calculate_totals()
        return self._total_no_discount

    @property
    def discounted_amount(self):
        """Shortcut for self.total_no_discount - self.total"""
        if not hasattr(self, '_discounted_amount'):
            self._calculate_totals()
        return self._discounted_amount

    @property
    def receipt(self):
        return Pendulum(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=self.group.deadline.hour,
            minute=self.group.deadline.minute,
            second=self.group.deadline.second,
            tzinfo=self.group.store.timezone
        ).add_timedelta(
            self.group.delay
        )

    def _calculate_totals(self):
        self._total = Decimal(0)
        self._paid_total = Decimal(0)
        self._total_no_discount = Decimal(0)
        self._discounted_amount = Decimal(0)
        for order in self.orders.all():
            self._total += order.total
            self._total_no_discount += order.total_no_discount
            self._discounted_amount += order.discounted_amount
            if order.payment_gocardless or order.payment_payconiq:
                self._paid_total += order.total

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.orders.update(
            status=self.status
        )

    @classmethod
    def created(cls, sender, group_order, **kwargs):
        send_group_order_email.apply_async(
            kwargs={
                'group_order_id': group_order.id,
            },
            eta=Pendulum.create(
                year=group_order.date.year,
                month=group_order.date.month,
                day=group_order.date.day,
                tz=group_order.group.store.timezone
            ).at(
                hour=group_order.group.deadline.hour,
                minute=group_order.group.deadline.minute,
                second=group_order.group.deadline.second
            )._datetime
        )
