from django.db import models
from django.utils.translation import ugettext_lazy as _


class StoreCategory(models.Model):
    name = models.CharField(
        max_length=191,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )

    class Meta:
        verbose_name = _('winkelcategorie')
        verbose_name_plural = _('winkelcategorieën')

    def __str__(self):
        return self.name
