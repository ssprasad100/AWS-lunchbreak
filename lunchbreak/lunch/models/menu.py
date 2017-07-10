from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from safedelete import HARD_DELETE, SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel


class Menu(SafeDeleteModel):

    class Meta:
        unique_together = ('name', 'store',)
        verbose_name = _('menu')
        verbose_name_plural = _('menu\'s')

    def __str__(self):
        return self.name

    name = models.CharField(
        max_length=191,
        verbose_name=_('naam'),
        help_text=('Naam.')
    )
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name=_('prioriteit'),
        help_text=('Prioriteit.')
    )
    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        related_name='menus',
        verbose_name=_('winkel'),
        help_text=('Winkel.')
    )

    @cached_property
    def _safedelete_policy(self):
        """Menu can be deleted if no active OrderedFood use them.

        Otherwise soft delete it and the food it's related to.

        Returns:
            SOFT_DELETE_CASCADE if still used, HARD_DELETE otherwise.
        """
        from customers.models import OrderedFood

        active_order = OrderedFood.objects.active_with(
            menu=self
        ).exists()
        if active_order:
            return SOFT_DELETE_CASCADE
        return HARD_DELETE
