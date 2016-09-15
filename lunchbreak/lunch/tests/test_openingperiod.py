from datetime import datetime, time, timedelta

import mock
from Lunchbreak.test import LunchbreakTestCase

from ..config import MONDAY, SUNDAY
from ..models import OpeningPeriod


class OpeningPeriodTestCase(LunchbreakTestCase):

    @mock.patch('googlemaps.Client.geocode')
    def test_openingperiod(self, mock_geocode):
        self.mock_geocode_results(mock_geocode)

        # Weekday 0 - 1
        sun_mon = OpeningPeriod.objects.create(
            store=self.store,
            day=SUNDAY,
            time=time(00, 00),
            duration=timedelta(days=1)
        )

        sunday = datetime(
            year=2016,
            month=4,
            day=3
        )

        between_sun_mon = sunday + timedelta(
            hours=12
        )
        between_mon_tue = between_sun_mon + timedelta(
            days=1
        )

        self.assertTrue(sun_mon.contains(between_sun_mon))
        self.assertFalse(sun_mon.contains(between_mon_tue))

        # Weekday 0 - 1 @ 11:59
        sun_mon_mid = OpeningPeriod.objects.create(
            store=self.store,
            day=SUNDAY,
            time=time(11, 59),
            duration=timedelta(days=1)
        )

        sun_12 = sunday + timedelta(
            hours=12
        )
        tue_00 = sunday + timedelta(
            days=1
        )
        tue_12 = tue_00 + timedelta(
            hours=12
        )

        self.assertTrue(sun_mon_mid.contains(sun_12))
        self.assertTrue(sun_mon_mid.contains(tue_00))
        self.assertFalse(sun_mon_mid.contains(tue_12))

        mon_sun_mid = OpeningPeriod.objects.create(
            store=self.store,
            day=MONDAY,
            time=time(11, 59),
            duration=timedelta(days=6)
        )

        self.assertFalse(mon_sun_mid.contains(sun_12))
        self.assertFalse(mon_sun_mid.contains(tue_00))
        self.assertTrue(mon_sun_mid.contains(tue_12))

        # Same day, hour test
        time_12_14 = OpeningPeriod.objects.create(
            store=self.store,
            day=SUNDAY,
            time=time(12, 00),
            duration=timedelta(hours=2)
        )
        hour_11 = sunday + timedelta(
            hours=11
        )
        hour_12 = sunday + timedelta(
            hours=12
        )
        hour_13 = sunday + timedelta(
            hours=13
        )
        hour_14 = sunday + timedelta(
            hours=14
        )
        hour_15 = sunday + timedelta(
            hours=15
        )

        self.assertFalse(time_12_14.contains(hour_11))
        self.assertTrue(time_12_14.contains(hour_12))
        self.assertTrue(time_12_14.contains(hour_13))
        self.assertTrue(time_12_14.contains(hour_14))
        self.assertFalse(time_12_14.contains(hour_15))
