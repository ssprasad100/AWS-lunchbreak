from dirtyfields import DirtyFieldsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..exceptions import LinkingError


class IngredientRelation(models.Model, DirtyFieldsMixin):

    class Meta:
        unique_together = ('food', 'ingredient',)

    def __str__(self):
        return str(self.ingredient)

    food = models.ForeignKey(
        'Food',
        on_delete=models.CASCADE,
        related_name='ingredientrelations',
        verbose_name=_('etenswaar'),
        help_text=_('Etenswaar.')
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        related_name='ingredientrelations',
        verbose_name=_('ingrediënt'),
        help_text=_('Ingrediënt.')
    )
    selected = models.BooleanField(
        default=False,
        verbose_name=_('geselecteerd'),
        help_text=_('Of het ingrediënt standaard geselecteerd is.')
    )
    typical = models.BooleanField(
        default=False,
        verbose_name=_('typisch'),
        help_text=_('Of het een typisch ingrediënt is voor het gelinkte etenswaar.')
    )

    def save(self, *args, **kwargs):
        if self.food.store.id != self.ingredient.store.id:
            raise LinkingError()

        dirty_fields = self.get_dirty_fields(check_relationship=True)
        if 'ingredient' in dirty_fields:
            self.food.update_typical()

        super(IngredientRelation, self).save(*args, **kwargs)
