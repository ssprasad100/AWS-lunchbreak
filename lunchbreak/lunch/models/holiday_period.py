import pendulum
from dirtyfields import DirtyFieldsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _
from Lunchbreak.exceptions import LunchbreakException
from Lunchbreak.mixins import CleanModelMixin

from ..managers import HolidayPeriodQuerySet
from ..utils import timezone_for_store


class HolidayPeriod(CleanModelMixin, models.Model, DirtyFieldsMixin):
    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )
    description = models.CharField(
        max_length=191,
        blank=True,
        verbose_name=_('beschrijving'),
        help_text=_('Beschrijving met een reden.')
    )

    start = models.DateTimeField(
        verbose_name=_('start'),
        help_text=_('Start van de vakantieperiode.')
    )
    end = models.DateTimeField(
        verbose_name=_('einde'),
        help_text=_('Einde van de vakantieperiode.')
    )

    closed = models.BooleanField(
        default=True,
        verbose_name=_('gesloten'),
        help_text=_('Of de winkel gesloten is tijdens deze vakantieperiode.')
    )

    objects = HolidayPeriodQuerySet.as_manager()

    class Meta:
        verbose_name = _('vakantieperiode')
        verbose_name_plural = _('vakantieperiodes')

    @property
    def period(self):
        period = pendulum.Period(
            start=self.start,
            end=self.end
        )
        period.closed = self.closed
        return period

    def clean_start(self):
        if self.pk is None or 'start' in self.get_dirty_fields():
            self.start = timezone_for_store(
                value=self.start,
                store=self.store
            )

        if self.pk is None or 'start' in self.get_dirty_fields():
            # Put here because both the start and end need to be set to the same timezone
            self.end = timezone_for_store(
                value=self.end,
                store=self.store
            )

        if self.start >= self.end:
            raise LunchbreakException(
                'Het begin moet voor het einde zijn.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        self.store.save()
        super(HolidayPeriod, self).save(*args, **kwargs)

    def __str__(self):
        return '{start}-{end} {state}'.format(
            start=self.start,
            end=self.end,
            state='closed' if self.closed else 'open'
        )
