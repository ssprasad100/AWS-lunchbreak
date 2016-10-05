from datetime import datetime, timedelta

import mock
from Lunchbreak.exceptions import LunchbreakException
from Lunchbreak.test import LunchbreakTestCase

from ..models import HolidayPeriod, Store


class HolidayPeriodTestCase(LunchbreakTestCase):

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_holidayperiod(self, mock_geocode, mock_timezone):
        self.mock_timezone_result(mock_timezone)
        self.mock_geocode_results(mock_geocode)
        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        now = datetime.now()

        hp = HolidayPeriod(
            store=store,
            description='description',
            start=now,
            end=now
        )

        try:
            hp.save()
        except LunchbreakException:
            try:
                tomorrow = now + timedelta(days=1)
                hp.end = tomorrow
                hp.save()
            except Exception as e:
                self.fail(e)
        else:
            self.fail()
