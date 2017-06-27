from django.db import models
from django.utils.translation import ugettext_lazy as _
from Lunchbreak.fields import RoundingDecimalField
from Lunchbreak.mixins import CleanModelMixin
from safedelete import HARD_DELETE_NOCASCADE
from safedelete.models import SafeDeleteMixin

from ..exceptions import InvalidFoodTypeAmount


class Quantity(CleanModelMixin, SafeDeleteMixin):

    _safedelete_policy = HARD_DELETE_NOCASCADE

    class Meta:
        unique_together = ('foodtype', 'store',)
        verbose_name = _('hoeveelheid')
        verbose_name_plural = _('hoeveelheden')

    def __str__(self):
        return '{minimum}-{maximum}'.format(
            minimum=self.minimum,
            maximum=self.maximum
        )

    foodtype = models.ForeignKey(
        'FoodType',
        on_delete=models.CASCADE,
        verbose_name=_('type etenswaar'),
        help_text=('Type etenswaar.')
    )
    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=('Winkel.')
    )

    minimum = RoundingDecimalField(
        decimal_places=3,
        max_digits=7,
        default=1,
        verbose_name=_('minimum'),
        help_text=('Minimum hoeveelheid.')
    )
    maximum = RoundingDecimalField(
        decimal_places=3,
        max_digits=7,
        default=10,
        verbose_name=_('maximum'),
        help_text=('Maximum hoeveelheid.')
    )

    last_modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('laatst aangepast'),
        help_text=('Laatst aangepast.')
    )

    def clean_minimum(self):
        self.foodtype.is_valid_amount(self.minimum)
        if self.minimum > self.maximum:
            raise InvalidFoodTypeAmount(
                'Het minimum kan niet groter zijn dan het maximum.'
            )

    def clean_maximum(self):
        self.foodtype.is_valid_amount(self.maximum)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Quantity, self).save(*args, **kwargs)
