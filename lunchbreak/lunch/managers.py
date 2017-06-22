import copy

import pendulum
from django.core.exceptions import MultipleObjectsReturned
from django.db import models
from django.db.models.expressions import RawSQL
from push_notifications.models import DeviceManager

from .config import random_token
from decimal import Decimal


class StoreManager(models.Manager):

    def nearby(self, latitude, longitude, proximity):
        # TODO Use Pointfields instead of 2 decimalfields.
        # Haversine formule is het beste om te gebruiken bij korte afstanden.
        # d = 2 * r * asin(
        #   sqrt(
        #       sin^2(
        #           ( lat2-lat1 ) / 2
        #       ) + cos(lat1)*cos(lat2)*sin^2(
        #           (lon2-lon1) / 2
        #       )
        #   )
        # )
        haversine = '''
        CAST(
            (2*6371)
            * ASIN(
                SQRT(
                    POW(
                        SIN( (RADIANS(%s) - RADIANS(latitude)) / 2 )
                    , 2)
                    + (
                        COS(RADIANS(latitude))
                        * COS(RADIANS(%s))
                        * POW(
                            SIN(
                                (RADIANS(%s) - RADIANS(longitude)) / 2
                            )
                        , 2
                        )
                    )
                )
            )  as DECIMAL(10,7)
        )
        '''
        return self.get_queryset().filter(
            enabled=True
        ).exclude(
            models.Q(
                latitude=None
            ) | models.Q(
                longitude=None
            )
        ).annotate(
            distance=RawSQL(
                haversine,
                (
                    latitude,
                    latitude,
                    longitude,
                ),
            )
        ).filter(
            distance__lt=Decimal(proximity)
        ).order_by(
            'distance'
        )


class PeriodQuerySet(models.QuerySet):

    def periods(self, period):
        queryset = self.select_related(
            'store',
        )
        models = {model for model in queryset}
        days = period.range('days')
        for model in models:
            for day in days:
                if day.isoweekday() in model.weekdays:
                    yield model.period(day)

    def merged_periods(self, *args, **kwargs):
        return pendulum.Period.merge_periods(
            *list(self.periods(*args, **kwargs))
        )

    def between(self, period):
        periods = self.all().merged_periods(period)
        result = []

        for p in periods:
            if (p.start in period or p.end in period) \
                    or (p.start <= period.start and period.end <= p.end):
                result.append(p)

        return result


class HolidayPeriodQuerySet(PeriodQuerySet):

    def periods(self):
        return [model.period for model in self]

    def between(self, period):
        return self.filter(
            models.Q(
                start__range=(
                    period.start,
                    period.end
                )
            ) | models.Q(
                end__range=(
                    period.start,
                    period.end
                )
            )
        )


class BaseTokenManager(DeviceManager):

    def create_token(self, arguments, defaults, clone=False):
        identifier_raw = random_token()
        defaults['identifier'] = identifier_raw

        try:
            token, created = self.update_or_create(
                defaults=defaults,
                **arguments
            )
        except MultipleObjectsReturned:
            self.filter(**arguments).delete()
            token, created = self.update_or_create(
                defaults=defaults,
                **arguments
            )

        if clone:
            token_copy = copy.copy(token)
            token_copy.identifier = identifier_raw
            return (token_copy, created,)
        return (token, created,)
