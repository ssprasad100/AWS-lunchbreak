from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..mixins import NotifyModelMixin
from .abstract_password import AbstractPassword


class Employee(AbstractPassword, NotifyModelMixin):
    name = models.CharField(
        max_length=191,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )
    staff = models.ForeignKey(
        'Staff',
        on_delete=models.CASCADE,
        verbose_name=_('personeel'),
        help_text=_('Personeel.')
    )
    owner = models.BooleanField(
        default=False,
        verbose_name=_('eigenaar'),
        help_text=_('Of deze werknemer een eigenaar is.')
    )

    class Meta:
        verbose_name = _('werknemer')
        verbose_name_plural = _('werknemers')

    def __str__(self):
        return self.name
