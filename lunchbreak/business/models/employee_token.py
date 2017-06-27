from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from lunch.models import BaseToken


class EmployeeToken(BaseToken):
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name=_('werknemer'),
        help_text=_('Werknemer.')
    )

    APNS_CERTIFICATE = settings.BUSINESS_APNS_CERTIFICATE

    class Meta:
        verbose_name = _('werknemerstoken')
        verbose_name_plural = _('werknemerstokens')
