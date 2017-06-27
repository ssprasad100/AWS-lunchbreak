from django.utils.translation import ugettext as _

from ..managers import ConfirmedOrderManager
from .order import Order


class ConfirmedOrder(Order):

    class Meta:
        proxy = True
        verbose_name = _('bevestigde bestelling')
        verbose_name_plural = _('bevestigde bestellingen')

    objects = ConfirmedOrderManager()
