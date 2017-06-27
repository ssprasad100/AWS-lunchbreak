from django.db import models
from django.utils.translation import ugettext as _


class Heart(models.Model):

    class Meta:
        unique_together = ('user', 'store',)
        verbose_name = _('hart')
        verbose_name_plural = _('hartjes')

    def __str__(self):
        return '{user}, {store}'.format(
            user=self.user,
            store=self.store
        )

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
    added = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('toegevoegd'),
        help_text=_('Datum waarop deze persoon deze winkel "geheart" heeft.')
    )
