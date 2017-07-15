from dirtyfields import DirtyFieldsMixin
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from Lunchbreak.fields import CostField
from safedelete import HARD_DELETE, SOFT_DELETE
from safedelete.models import SafeDeleteModel

from ..exceptions import LinkingError


class Ingredient(SafeDeleteModel, DirtyFieldsMixin):

    class Meta:
        verbose_name = _('ingrediënt')
        verbose_name_plural = _('ingrediënten')

    def __str__(self):
        return '{name} ({group}) #{id}'.format(
            name=self.name,
            group=self.group,
            id=self.id
        )

    name = models.CharField(
        max_length=191,
        verbose_name=_('naam'),
        help_text=('Naam.')
    )
    cost = CostField(
        default=0,
        verbose_name=_('basisprijs'),
        help_text=(
            'Basisprijs die in rekening wordt gebracht afhankelijk van de '
            'prijsberekening ingesteld op de ingrediëntengroep.'
        )
    )

    group = models.ForeignKey(
        'IngredientGroup',
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name=_('ingrediëntengroep'),
        help_text=('Ingrediëntengroep.')
    )

    last_modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('laatst aangepast'),
        help_text=('Laatst aangepast.')
    )

    @cached_property
    def store(self):
        return self.group.store

    @cached_property
    def _safedelete_policy(self):
        """Ingredients can be deleted if no active OrderedFood use them.

        Returns:
            SOFT_DELETE if still used, HARD_DELETE otherwise.
        """
        from customers.models import OrderedFood

        active_order = OrderedFood.objects.active_with(
            ingredient=self
        ).exists()
        if active_order:
            return SOFT_DELETE
        return HARD_DELETE

    def save(self, *args, **kwargs):
        if self.store != self.group.store:
            raise LinkingError()

        if self.pk is not None:
            dirty_fields = self.get_dirty_fields(check_relationship=True)
            if 'group' in dirty_fields:
                for food in self.food_set.all():
                    food.update_typical()

        super(Ingredient, self).save(*args, **kwargs)
