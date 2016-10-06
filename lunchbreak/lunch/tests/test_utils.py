from datetime import datetime

from Lunchbreak.test import LunchbreakTestCase
from pendulum import Pendulum

from ..models import Store
from ..utils import timezone_for_store


class UtilsTestCase(LunchbreakTestCase):

    def test_timezone_for_store(self):
        brussels = 'Europe/Brussels'
        london = 'Europe/London'

        store = Store(
            timezone=brussels
        )

        # The hour should stay the same when both timezones are the same
        value = Pendulum(2016, 1, 1, 12, 00, tzinfo=brussels)
        self.assertTrue(
            isinstance(timezone_for_store(value, store), datetime)
        )
        self.assertEqual(
            timezone_for_store(value, store).hour,
            value.hour
        )

        # The hour should never change, regardless of timezone
        value = Pendulum(2016, 1, 1, 12, 00, tzinfo=london)
        self.assertEqual(
            timezone_for_store(value, store).hour,
            value.hour
        )
        self.assertEqual(
            Pendulum.instance(
                timezone_for_store(value, store)
            ).timezone_name,
            value.timezone_name
        )
