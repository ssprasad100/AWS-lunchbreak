from django.utils.translation import ugettext_lazy as _

from .period import Period


class DeliveryPeriod(Period):

    class Meta:
        verbose_name = _('leveringstijd')
        verbose_name_plural = _('leveringstijden')
