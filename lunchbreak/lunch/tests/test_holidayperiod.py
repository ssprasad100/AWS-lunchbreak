from datetime import datetime, timedelta

import mock
from django.core.exceptions import ValidationError
from Lunchbreak.test import LunchbreakTestCase

from ..models import HolidayPeriod, Store


class HolidayPeriodTestCase(LunchbreakTestCase):

    @mock.patch('googlemaps.Client.geocode')
    def test_holidayperiod(self, mock_geocode):
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
        except ValidationError:
            try:
                tomorrow = now + timedelta(days=1)
                hp.end = tomorrow
                hp.save()
            except Exception as e:
                self.fail(e)
        else:
            self.fail()
