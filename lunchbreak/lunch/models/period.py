from datetime import datetime

import pendulum
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..config import WEEKDAYS
from ..managers import PeriodQuerySet


class Period(models.Model):
    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        verbose_name=_('winkel'),
        help_text=_('Winkel.')
    )

    day = models.PositiveSmallIntegerField(
        choices=WEEKDAYS,
        verbose_name=_('weekdag'),
        help_text=_('Dag van de week.')
    )
    time = models.TimeField(
        verbose_name=_('openingstijd'),
        help_text=_('Tijdstip waarop de winkel opengaat.')
    )
    duration = models.DurationField(
        verbose_name=_('openingsduur'),
        help_text=_('Hoelang de winkel open is vanaf de openingstijd.')
    )

    objects = PeriodQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.store.save()
        super(Period, self).save(*args, **kwargs)

    @property
    def weekdays(self):
        now = pendulum.now().with_time(
            hour=self.time.hour,
            minute=self.time.minute,
            second=self.time.second,
            microsecond=self.time.microsecond
        )
        start = now.subtract(
            days=now.isoweekday()
        ).add(
            days=self.day
        )
        period = pendulum.Period(
            start=start,
            end=start + self.duration
        )

        result = set()
        for day in period.xrange('days'):
            weekday = day.isoweekday()
            if weekday in result:
                break
            result.add(weekday)
        return result

    def start(self, day):
        if isinstance(day, datetime):
            day = pendulum.instance(day)
        if day.isoweekday() != self.day:
            day = day.subtract(
                days=day.isoweekday() + (7 if day.isoweekday() < self.day else 0)
            ).add(
                days=self.day
            )

        return day.with_time(
            hour=self.time.hour,
            minute=self.time.minute,
            second=self.time.second,
            microsecond=self.time.microsecond
        ).timezone_(
            self.store.timezone
        )

    def end(self, day):
        return self.start(day) + self.duration

    def period(self, day):
        return pendulum.Period(
            start=self.start(day),
            end=self.end(day)
        )

    @classmethod
    def weekday_as_datetime(cls, weekday, time, store):
        if weekday is None or time is None or store is None:
            return None

        now = pendulum.now(store.timezone)
        start = now.subtract(
            days=now.isoweekday()
        ).add(
            days=weekday
        )
        result = start.with_time(
            hour=time.hour,
            minute=time.minute,
            second=time.second,
            microsecond=time.microsecond
        )
        if result.date() < pendulum.now(store.timezone).date():
            result = result.add(
                days=7
            )
        return result

    def __str__(self):
        return '{day} {time} - {duration}'.format(
            day=self.get_day_display(),
            time=self.time,
            duration=self.duration
        )
