from datetime import time, timedelta

import mock
import pendulum
from Lunchbreak.tests.testcase import LunchbreakTestCase
from pendulum import Pendulum

from ..config import WEEKDAYS
from ..models import OpeningPeriod, Period


class PeriodTestCase(LunchbreakTestCase):

    @mock.patch('pendulum.now')
    def test_time_as_datetime(self, mock_now):
        set_time = time(12, 00)
        # This is a monday
        now = Pendulum(
            year=2016,
            month=9,
            day=19,
            hour=set_time.hour,
            minute=set_time.minute,
            tzinfo=None
        )

        for current_day in range(7):
            now = now.add(days=1)
            mock_now.return_value = now

            for weekday_config in WEEKDAYS:
                day_in_week = weekday_config[0]

                period = Period(
                    day=day_in_week,
                    time=set_time,
                    duration=time(1, 00),
                    store=self.store
                )

                as_datetime = period.weekday_as_datetime(
                    weekday=period.day,
                    time=period.time,
                    store=period.store
                )
                if day_in_week == now.isoweekday():
                    self.assertEqual(
                        as_datetime,
                        now
                    )
                else:
                    self.assertGreater(
                        as_datetime,
                        now
                    )

    def test_between(self):
        times = [
            time(12, 00),
            time(23, 00)
        ]

        timedeltas = [
            timedelta(hours=1),
            timedelta(days=1),
            timedelta(days=2),
            timedelta(days=3),
            timedelta(days=6),
        ]

        for t in times:
            for weekday in WEEKDAYS:
                day = weekday[0]

                for delta in timedeltas:
                    openingperiod = OpeningPeriod.objects.create(
                        store=self.store,
                        day=day,
                        time=t,
                        duration=delta
                    )
                    period = openingperiod.period(
                        OpeningPeriod.weekday_as_datetime(
                            weekday=day,
                            time=t,
                            store=self.store
                        )
                    )
                    period_before = pendulum.Period(
                        start=period.start - timedelta(seconds=2),
                        end=period.start - timedelta(seconds=1),
                    )
                    period_over_start = pendulum.Period(
                        start=period_before.start,
                        end=period.start + timedelta(seconds=1)
                    )
                    period_in = pendulum.Period(
                        start=period.start + timedelta(seconds=1),
                        end=period.end - timedelta(seconds=1),
                    )
                    period_over_end = pendulum.Period(
                        start=period.end - timedelta(seconds=1),
                        end=period.end + timedelta(seconds=1),
                    )
                    period_after = pendulum.Period(
                        start=period.end + timedelta(seconds=1),
                        end=period.end + timedelta(seconds=2),
                    )
                    period_over = pendulum.Period(
                        start=period.start - timedelta(seconds=1),
                        end=period.end + timedelta(seconds=1),
                    )

                    for p in [period_before, period_after]:
                        periods = OpeningPeriod.objects.between(
                            period=p
                        )
                        self.assertEqual(
                            len(periods),
                            0
                        )

                    for p in [period_over_start, period_in, period_over_end, period_over]:
                        periods = OpeningPeriod.objects.between(
                            period=p
                        )
                        self.assertEqual(
                            len(periods),
                            1
                        )

                    openingperiod.delete()
