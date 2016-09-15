from datetime import time, timedelta

import pendulum
from Lunchbreak.test import LunchbreakTestCase

from ..config import WEEKDAYS
from ..models import OpeningPeriod


class PeriodTestCase(LunchbreakTestCase):

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
            timedelta(days=7),
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
                    period = openingperiod.period
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
                        self.assertEqual(
                            len(
                                OpeningPeriod.objects.between(
                                    period=p
                                )
                            ),
                            0
                        )

                    for p in [period_over_start, period_in, period_over_end, period_over]:
                        self.assertEqual(
                            len(
                                OpeningPeriod.objects.between(
                                    period=p
                                )
                            ),
                            1
                        )

                    openingperiod.delete()
