from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from lunch.models import BaseToken


class StaffToken(BaseToken):
    staff = models.ForeignKey(
        'Staff',
        on_delete=models.CASCADE,
        related_name='tokens',
        verbose_name=_('personeel'),
        help_text=_('Personeel.')
    )

    APNS_CERTIFICATE = settings.BUSINESS_APNS_CERTIFICATE

    class Meta:
        verbose_name = _('personeelstoken')
        verbose_name_plural = _('personeelstokens')
