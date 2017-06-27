from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import ugettext as _

from .abstract_order import AbstractOrder
from .order import Order


class TemporaryOrder(AbstractOrder):

    class Meta:
        unique_together = ['user', 'store']
        verbose_name = _('tijdelijke bestelling')
        verbose_name_plural = _('tijdelijke bestellingen')

    orderedfood = GenericRelation(
        'OrderedFood',
        related_query_name='temporary_order',
        verbose_name=_('bestelde etenswaren'),
        help_text=_('Bestelde etenswaren.')
    )

    def place(self, **kwargs):
        save = kwargs.get('save')
        order = Order.objects.create_with_orderedfood(
            orderedfood=self.orderedfood.all(),
            user=self.user,
            store=self.store,
            **kwargs
        )
        if save and not order.payment_payconiq:
            self.delete()
        return order
