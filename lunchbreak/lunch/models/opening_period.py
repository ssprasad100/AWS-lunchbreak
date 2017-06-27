from django.utils.translation import ugettext_lazy as _

from .period import Period


class OpeningPeriod(Period):

    class Meta:
        verbose_name = _('openingstijd')
        verbose_name_plural = _('openingstijden')
