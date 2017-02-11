from datetime import time, timedelta

import mock
from customers.exceptions import (PastOrderDenied, PreorderTimeExceeded,
                                  StoreClosed)
from Lunchbreak.test import LunchbreakTestCase

from ..models import HolidayPeriod, OpeningPeriod, Store


class StoreTestCase(LunchbreakTestCase):

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_nearby(self, mock_geocode, mock_timezone):
        """ Test whether LunchbreakManager.nearby returns the right stores. """
        self.mock_timezone_result(mock_timezone)
        Store.objects.all().delete()

        self.mock_geocode_results(
            mock_geocode,
            lat=51.0111595,
            lng=3.9075993
        )
        store_center = Store.objects.create(
            name='center',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        self.mock_geocode_results(
            mock_geocode,
            lat=51.0076504,
            lng=3.8892806
        )
        store_under2 = Store.objects.create(
            name='1,34km',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Wegvoeringstraat',
            number=47
        )

        self.mock_geocode_results(
            mock_geocode,
            lat=51.0089506,
            lng=3.8392584
        )
        store_under5 = Store.objects.create(
            name='4,79km',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Wetterensteenweg',
            number=1
        )

        self.mock_geocode_results(
            mock_geocode,
            lat=51.0267939,
            lng=3.7968594
        )
        store_under8 = Store.objects.create(
            name='7,95km',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Melle',
            postcode='9090',
            street='Wellingstraat',
            number=1
        )

        lat = store_center.latitude
        lng = store_center.longitude

        self.assertInCount(
            Store.objects.nearby(lat, lng, 1),
            [store_center]
        )
        self.assertInCount(
            Store.objects.nearby(lat, lng, 2),
            [store_center, store_under2]
        )
        self.assertInCount(
            Store.objects.nearby(lat, lng, 5),
            [store_center, store_under2, store_under5]
        )
        self.assertInCount(
            Store.objects.nearby(lat, lng, 8),
            [store_center, store_under2, store_under5, store_under8]
        )

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_last_modified(self, mock_geocode, mock_timezone):
        """Test whether updating OpeningPeriod and HolidayPeriod objects updates the Store."""
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

        last_modified_first = store.last_modified
        self.mock_now.return_value = self.midday.add(minutes=1)._datetime

        OpeningPeriod.objects.create(
            store=store,
            day=0,
            time=time(00, 00),
            duration=timedelta(hours=1)
        )

        last_modified_second = store.last_modified

        self.assertGreater(last_modified_second, last_modified_first)

        self.mock_now.return_value = self.midday.add(minutes=2)._datetime

        tomorrow = self.midday.add(days=1)
        HolidayPeriod.objects.create(
            store=store,
            description='description',
            start=self.midday._datetime,
            end=tomorrow._datetime
        )

        self.assertGreater(store.last_modified, last_modified_second)

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('django.utils.timezone.now')
    @mock.patch('googlemaps.Client.geocode')
    def test_check_open(self, mock_geocode, mock_now, mock_timezone):
        self.mock_timezone_result(mock_timezone)
        today = self.midday.with_time(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        # Mock also used for Store.last_modified
        mock_now.return_value = today.add(hours=1)._datetime

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

        # PastOrderDenied
        self.assertRaises(PastOrderDenied, store.is_open, today)

        # PreorderTimeExceeded
        wait = timedelta(minutes=15)
        opening_wait = wait * 2
        hours_closing = 10
        store.wait = wait

        for extra_week in range(3):
            opening = today.add_timedelta(
                opening_wait
            ).add(days=7 * extra_week)
            closing = opening.add(hours=hours_closing)
            day = opening.isoweekday()
            OpeningPeriod.objects.create(
                store=store,
                day=day,
                time=opening,
                duration=timedelta(hours=hours_closing)
            )
            mock_now.return_value = opening._datetime
            self.assertRaises(
                PreorderTimeExceeded,
                store.is_open,
                opening.add_timedelta(wait).subtract(minutes=1)
            )

            # Before and after opening hours
            before = opening.subtract(minutes=1)
            between = opening.add(hours=hours_closing / 2)
            after = closing.add(hours=1)
            end = after.add(hours=1)

            mock_now.return_value = today._datetime
            self.assertRaises(StoreClosed, store.is_open, before._datetime)
            self.assertTrue(store.is_open(between))
            self.assertRaises(StoreClosed, store.is_open, after._datetime)

            hp = HolidayPeriod.objects.create(
                store=store,
                start=today._datetime,
                end=end._datetime,
                closed=True
            )
            self.assertRaises(StoreClosed, store.is_open, before._datetime)

            self.assertRaises(StoreClosed, store.is_open, between._datetime)
            self.assertRaises(StoreClosed, store.is_open, after._datetime)

            hp.closed = False
            hp.save()
            self.assertTrue(store.is_open(before._datetime))
            self.assertTrue(store.is_open(between._datetime))
            self.assertTrue(store.is_open(after._datetime))

            hp.closed = True
            hp.end = between._datetime
            hp.save()
            self.assertRaises(StoreClosed, store.is_open, before._datetime)
            self.assertRaises(StoreClosed, store.is_open, between._datetime)
            self.assertTrue(store.is_open(between.add(minutes=1)._datetime))
