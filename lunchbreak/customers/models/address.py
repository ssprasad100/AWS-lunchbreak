from django.db import models
from django.utils.translation import ugettext as _
from lunch.models import AbstractAddress

from ..config import ORDER_STATUSES_ACTIVE


class Address(AbstractAddress):

    class Meta:
        verbose_name = _('adres')
        verbose_name_plural = _('adressen')

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name=_('gebruiker'),
        help_text=_('Gebruiker.')
    )

    deleted = models.BooleanField(
        default=False,
        verbose_name=_('verwijderd'),
        help_text=_(
            'Duid aan of het item wacht om verwijderd te worden. Het wordt '
            'pas verwijderd wanneer er geen actieve bestellingen meer zijn '
            'met dit adres.'
        )
    )

    def delete(self, *args, **kwargs):
        active_orders = self.order_set.filter(
            status__in=ORDER_STATUSES_ACTIVE
        ).exists()

        if active_orders:
            self.deleted = True
            self.save()
        else:
            super(Address, self).delete(*args, **kwargs)
