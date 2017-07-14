from collections import defaultdict
from datetime import timedelta

import pendulum
from customers.exceptions import (PastOrderDenied, PreorderTimeExceeded,
                                  StoreClosed)
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from ..managers import StoreManager
from .abstract_address import AbstractAddress


class Store(AbstractAddress):

    class Meta:
        verbose_name = _('winkel')
        verbose_name_plural = _('winkels')

    def __str__(self):
        return self.name

    objects = StoreManager()

    name = models.CharField(
        max_length=191,
        verbose_name=_('naam'),
        help_text=_('Naam.')
    )

    categories = models.ManyToManyField(
        'StoreCategory',
        verbose_name=_('winkelcategorieën'),
        help_text=_('Winkelcategorieën.')
    )
    wait = models.DurationField(
        default=timedelta(seconds=60),
        verbose_name=_('wachttijd'),
        help_text=_('Minimum tijd dat op voorhand besteld moet worden.')
    )
    hearts = models.ManyToManyField(
        'customers.User',
        through='customers.Heart',
        blank=True,
        verbose_name=_('hartjes'),
        help_text=_('Hartjes van klanten.')
    )
    seats_max = models.PositiveIntegerField(
        default=10,
        validators=[
            MinValueValidator(1)
        ],
        verbose_name=_('maximum plaatsen'),
        help_text=_('Maximum aantal plaatsen voor reservaties.')
    )
    regions = models.ManyToManyField(
        'Region',
        blank=True,
        verbose_name=_('regio\'s'),
        help_text=_('Regio\'s waaraan geleverd wordt.')
    )
    timezone = models.CharField(
        max_length=191,
        default='UTC',
        verbose_name=_('tijdzone'),
        help_text=_('Tijdzone.')
    )

    gocardless_enabled = models.BooleanField(
        default=False,
        verbose_name=_('gocardless betalingen ingeschakeld'),
        help_text=_(
            'Online betalingen ingeschakeld, er moet een GoCardless '
            'merchant gelinkt worden voor online betalingen '
            'aanvaard kunnen worden.'
        )
    )
    payconiq_enabled = models.BooleanField(
        default=False,
        verbose_name=_('payconiq betalingen ingeschakeld'),
        help_text=_(
            'Online betalingen ingeschakeld, er moet een Payconiq '
            'merchant gelinkt worden voor online betalingen '
            'aanvaard kunnen worden.'
        )
    )
    cash_enabled = models.BooleanField(
        default=True,
        verbose_name=_('betalingen in winkel ingeschakeld'),
        help_text=_(
            'Betalingen in winkel ingeschakeld.'
        )
    )
    last_modified = models.DateTimeField(
        auto_now=True,
        verbose_name=_('laatst aangepast'),
        help_text=_('Wanneer deze winkel laatst aangepast werd.')
    )
    enabled = models.BooleanField(
        default=True,
        verbose_name=_('ingeschakeld'),
        help_text=_('Ingeschakeld.')
    )

    @cached_property
    def category(self):
        return self.categories.all()[0]

    @cached_property
    def does_delivery(self):
        return self.regions.all().exists()

    @cached_property
    def hearts_count(self):
        return self.hearts.count()

    def update_location(self):
        super().update_location()

        google_client = self.maps_client()
        result = google_client.timezone(
            location={
                'lat': self.latitude,
                'lng': self.longitude
            },
            language='English'
        )

        self.timezone = result['timeZoneId']

    def open_dates(self, openingperiods=None, **kwargs):
        """Wrapper for openingperiods_for returning the dates.

        Will use given openingperiods instead of using openingperiods_for if not None.
        Else it will use openingperiods_for with given kwargs.

        Args:
            **kwargs (dict): Passed onto openingperiods_for.
            openingperiods (list, optional): List of :obj:`pendulum.Period`s.

        Returns:
            set: Dates of the openingperiods.
        """
        if openingperiods is None:
            openingperiods = self.openingperiods_for(**kwargs)

        weekdays = list()
        for openingperiod in openingperiods:
            if openingperiod.start.date() not in weekdays:
                weekdays.append(openingperiod.start.date())
            if openingperiod.end.date() not in weekdays:
                weekdays.append(openingperiod.end.date())

        return weekdays

    def periods_per_weekday(self, periods=None, **kwargs):
        """Split periods into their starting weekdays.

        Return a dict with as keys the starting weekdays and values a set of
        periods with that starting weekday.

        Args:
            **kwargs (dict): Kwargs passed onto openingperiods_for if periods is None.
            periods (:obj:`list`, optional): List of :obj:`pendulum.Period`s.

        Returns:
            dict: Key: weekday of start, value set of periods
        """
        if periods is None:
            periods = self.openingperiods_for(
                **kwargs
            )

        result = defaultdict(set)

        for period in periods:
            result[period.start.isoweekday()].add(period)

        return result

    @property
    def openingperiods_today(self):
        """Wrapper for openingperiods_for_day where the datetime is the given current day."""
        return self.openingperiods_for_day(
            dt=timezone.now()
        )

    def openingperiods_for_day(self, dt, **kwargs):
        """Wrapper for opening_periods where period is the whole given day."""
        start = pendulum.instance(dt).hour_(0).minute_(0).second_(0)
        end = start.hour_(23).minute_(59).second_(59)
        period = pendulum.Period(
            start=start,
            end=end
        )

        return self.openingperiods_for(
            period=period,
            **kwargs
        )

    def openingperiods_for(self, period=None, start=None, orderedfood=None, **kwargs):
        """Get opening periods for given period.

        Return a list of periods indicating when the store is open for the given period.
        If period is None, it will use start as the start of the period.
        If start is None, it will use the current datetime + Store.wait as the start of the period.
        It will pass **kwargs onto pendulum.Pendulum.add calculate an end to
        the period based on the start.

        Args:
            **kwargs (dict): Passed onto pendulum.Pendulum.add to calculate the
            end of the period based off of the start.
            period (:obj:`pendulum.Period`, optional): Period for which the
            openingperiods are requested.
            start (:obj:`pendulum.Pendulum`, optional): Start of the period.

        Returns:
            list: List of :obj:`pendulum.Period` indicating when the store is open.

        Raises:
            ValueError: A period or start or kwargs must be given.
        """
        if period is None and start is None and not kwargs:
            raise ValueError(
                'A period or start or kwargs must be given.'
            )

        if period is None:
            if start is None:
                now = timezone.now()
                start = pendulum.instance(now)
                wait = timedelta()
                if orderedfood is not None:
                    preorder_time = None
                    preorder_days = None

                    for of in orderedfood:
                        food_wait = of.original.inherited_wait

                        if food_wait > wait:
                            wait = food_wait

                        food_preorder_days, food_preorder_time = of.original.preorder_settings

                        if food_preorder_time is None or food_preorder_days is None:
                            continue

                        if (preorder_time is None and preorder_days is None) \
                            or food_preorder_days > preorder_days \
                            or (
                                food_preorder_time < preorder_time
                                and food_preorder_days == preorder_days
                        ):
                            preorder_time = food_preorder_time
                            preorder_days = food_preorder_days

                    if preorder_time is not None and preorder_days is not None:
                        # Amount of days needed to order in advance
                        # (add 1 if it isn't before the preorder_time)
                        preorder_days = preorder_days + (
                            1 if now.time() > preorder_time else 0
                        )
                        start = start.add(
                            days=preorder_days
                        )
                        if 'days' in kwargs:
                            kwargs['days'] = max(0, kwargs['days'] - preorder_days)

                start += wait
            end = start.add(**kwargs)

            period = pendulum.Period(
                start=start,
                end=end
            )

        from .holiday_period import HolidayPeriod
        from .opening_period import OpeningPeriod

        openingperiods = OpeningPeriod.objects.filter(
            store=self
        ).between(
            period=period
        )
        holidayperiods = HolidayPeriod.objects.filter(
            store=self
        ).between(
            period=period
        ).periods()

        closingperiods = []
        for period in holidayperiods:
            if not period.closed:
                openingperiods.append(period)
            else:
                closingperiods.append(period)

        result = []
        for openingperiod in openingperiods:
            adjusted_openingperiod = openingperiod.exclude(
                *closingperiods
            )
            if adjusted_openingperiod is not None:
                result.extend(adjusted_openingperiod)
        return result

    def delivers_to(self, address):
        return self.regions.filter(
            postcode=address.postcode
        ).exists()

    def is_open(self, dt, raise_exception=True, now=None, ignore_wait=False):
        """Check whether the store is open at the specified time."""

        if isinstance(dt, pendulum.Pendulum):
            dt = dt._datetime

        if now is None:
            now = timezone.now()

        if dt < now:
            if not raise_exception:
                return False
            raise PastOrderDenied()

        if not ignore_wait and dt - now < self.wait:
            if not raise_exception:
                return False
            raise PreorderTimeExceeded()

        from .holiday_period import HolidayPeriod

        holidayperiods = HolidayPeriod.objects.filter(
            store=self,
            start__lte=dt,
            end__gte=dt
        )

        closed = False
        for holidayperiod in holidayperiods:
            if not holidayperiod.closed:
                break
            else:
                closed = True
        else:
            # Open stores are
            if closed:
                if not raise_exception:
                    return False
                raise StoreClosed(
                    'De winkel is exclusief gesloten vanwege een vakantieperiode.'
                )

            periods = self.openingperiods_for_day(
                dt=dt
            )

            for period in periods:
                if dt in period:
                    return True

            if not raise_exception:
                return False
            raise StoreClosed()
        return True
