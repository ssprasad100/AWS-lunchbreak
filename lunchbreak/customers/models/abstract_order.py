from django.db import models
from django.utils.translation import ugettext as _
from Lunchbreak.exceptions import LunchbreakException
from Lunchbreak.mixins import CleanModelMixin

from ..managers import OrderManager
from .ordered_food import OrderedFood


class AbstractOrder(CleanModelMixin, models.Model):

    class Meta:
        abstract = True

    def __str__(self):
        return _('%(user)s, %(store)s (onbevestigd)') % {
            'user': self.user.name,
            'store': self.store
        }

    objects = OrderManager()

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        verbose_name=_('gebruiker'),
        help_text=_('Gebruiker.')
    )
    store = models.ForeignKey(
        'lunch.Store',
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )

    @classmethod
    def is_valid(cls, orderedfood, **kwargs):
        if orderedfood is None or len(orderedfood) == 0:
            raise LunchbreakException(
                'Een bestelling moet etenswaren hebben.'
            )

        try:
            for f in orderedfood:
                if not isinstance(f, dict) and not isinstance(f, OrderedFood):
                    raise ValueError(
                        'Order creation requires a list of dicts or OrderedFoods.'
                    )
        except TypeError:
            raise LunchbreakException(
                'Een bestelling moet etenswaren hebben.'
            )
