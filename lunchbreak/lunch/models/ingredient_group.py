from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from Lunchbreak.exceptions import LunchbreakException
from Lunchbreak.fields import CostField
from Lunchbreak.mixins import CleanModelMixin
from safedelete.models import SafeDeleteModel

from ..config import COST_GROUP_BOTH, COST_GROUP_CALCULATIONS


class IngredientGroup(CleanModelMixin, SafeDeleteModel):

    class Meta:
        verbose_name = _('ingrediëntengroep')
        verbose_name_plural = _('ingrediëntengroepen')

    def __str__(self):
        return self.name

    name = models.CharField(
        max_length=191,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )
    foodtype = models.ForeignKey(
        'FoodType',
        on_delete=models.CASCADE,
        verbose_name=_('type etenswaar'),
        help_text=_('Type etenswaar.')
    )
    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )

    minimum = models.PositiveIntegerField(
        default=0,
        verbose_name=_('minimum'),
        help_text=_('Minimum hoeveelheid.')
    )
    maximum = models.PositiveIntegerField(
        default=0,
        verbose_name=_('maximum'),
        help_text=_('Maximum hoeveelheid.')
    )
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name=_('prioriteit'),
        help_text=_('Prioriteit waarop gesorteerd wordt.')
    )
    cost = CostField(
        default=0,
        validators=[
            MinValueValidator(0)
        ],
        verbose_name=_('basisprijs'),
        help_text=_(
            'Basisprijs indien toegevoegd of afgetrokken van het etenswaar.'
        )
    )
    calculation = models.PositiveIntegerField(
        choices=COST_GROUP_CALCULATIONS,
        default=COST_GROUP_BOTH,
        verbose_name=_('prijsberekening'),
        help_text=_(
            'Manier waarop de prijs moet berekened worden indien '
            'ingrediënten aangepast toegevoegd of afgetrokken worden.'
        )
    )

    def clean_minimum(self):
        if self.minimum > self.maximum:
            raise LunchbreakException(
                'Het minimum kan niet groter zijn dan het maximum.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(IngredientGroup, self).save(*args, **kwargs)
