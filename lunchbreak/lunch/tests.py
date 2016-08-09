from datetime import datetime, time, timedelta

import mock
from customers.exceptions import MinTimeExceeded, PastOrderDenied, StoreClosed
from django.core.exceptions import ValidationError
from Lunchbreak.test import LunchbreakTestCase

from .config import (INPUT_AMOUNT, INPUT_SI_SET, INPUT_SI_VARIABLE, MONDAY,
                     SUNDAY)
from .exceptions import AddressNotFound
from .models import (Food, Menu, FoodType, HolidayPeriod,
                     IngredientGroup, OpeningPeriod, Quantity, Store)


class LunchTests(LunchbreakTestCase):

    @mock.patch('googlemaps.Client.geocode')
    def test_address(self, mock_geocode):
        """ Test for the AddressNotFound exception. """
        try:
            mock_fail = []
            self.mock_geocode_results(mock_geocode, mock_fail)
            Store.objects.create(
                name='test',
                country='nonexisting',
                province='nonexisting',
                city='nonexisting',
                postcode='nonexisting',
                street='nonexisting',
                number=5
            )
        except AddressNotFound:
            try:
                self.mock_geocode_results(mock_geocode)
                Store.objects.create(
                    name='valid',
                    country='Belgie',
                    province='Oost-Vlaanderen',
                    city='Wetteren',
                    postcode='9230',
                    street='Dendermondesteenweg',
                    number=10
                )
            except AddressNotFound:
                self.fail()
        else:
            self.fail()

    @mock.patch('googlemaps.Client.geocode')
    def test_stores_nearby(self, mock_geocode):
        """ Test whether LunchbreakManager.nearby returns the right stores. """
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

    def assertInCount(self, haystack, needles):
        self.assertEqual(len(haystack), len(needles))

        for needle in needles:
            self.assertIn(needle, haystack)

    def time_from_string(self, time_string):
        return datetime.strptime(time_string, '%H:%M').time()

    @mock.patch('googlemaps.Client.geocode')
    def test_store_last_modified(self, mock_geocode):
        """Test whether updating OpeningPeriod and HolidayPeriod objects updates the Store."""
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

        OpeningPeriod.objects.create(
            store=store,
            day=0,
            time=self.time_from_string('00:00'),
            duration=timedelta(hours=1)
        )

        last_modified_second = store.last_modified

        self.assertGreater(last_modified_second, last_modified_first)

        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        HolidayPeriod.objects.create(
            store=store,
            description='description',
            start=now,
            end=tomorrow
        )

        self.assertGreater(store.last_modified, last_modified_second)

    @mock.patch('django.utils.timezone.now')
    @mock.patch('googlemaps.Client.geocode')
    def test_store_store_check_open(self, mock_geocode, mock_now):
        today = datetime.now()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)

        # Mock also used for Store.last_modified
        mock_now.return_value = today + timedelta(hours=1)

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

        # MinTimeExceeded
        wait = timedelta(minutes=15)
        opening_wait = wait * 2
        hours_closing = 10
        store.wait = wait

        opening = (today + opening_wait)
        closing = (opening + timedelta(hours=hours_closing))
        day = opening.isoweekday()
        OpeningPeriod.objects.create(
            store=store,
            day=day,
            time=opening,
            duration=timedelta(hours=hours_closing)
        )
        mock_now.return_value = opening
        self.assertRaises(
            MinTimeExceeded,
            store.is_open,
            opening + wait - timedelta(minutes=1)
        )

        # Before and after opening hours
        before = opening - timedelta(minutes=1)
        between = opening + timedelta(hours=hours_closing / 2)
        after = closing + timedelta(hours=1)
        end = after + timedelta(hours=1)

        mock_now.return_value = today
        self.assertRaises(StoreClosed, store.is_open, before)
        self.assertIsNone(store.is_open(between))
        self.assertRaises(StoreClosed, store.is_open, after)

        hp = HolidayPeriod.objects.create(
            store=store,
            start=today,
            end=end,
            closed=True
        )
        self.assertRaises(StoreClosed, store.is_open, before)

        self.assertRaises(StoreClosed, store.is_open, between)
        self.assertRaises(StoreClosed, store.is_open, after)

        hp.closed = False
        hp.save()
        self.assertIsNone(store.is_open(before))
        self.assertIsNone(store.is_open(between))
        self.assertIsNone(store.is_open(after))

        hp.closed = True
        hp.end = between
        hp.save()
        self.assertRaises(StoreClosed, store.is_open, before)
        self.assertRaises(StoreClosed, store.is_open, between)
        self.assertIsNone(store.is_open(between + timedelta(minutes=1)))

    @mock.patch('googlemaps.Client.geocode')
    def test_openingperiod(self, mock_geocode):
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

        # Weekday 0 - 1
        sun_mon = OpeningPeriod.objects.create(
            store=store,
            day=SUNDAY,
            time=self.time_from_string('00:00'),
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
            store=store,
            day=SUNDAY,
            time=self.time_from_string('11:59'),
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
            store=store,
            day=MONDAY,
            time=self.time_from_string('11:59'),
            duration=timedelta(days=6)
        )

        self.assertFalse(mon_sun_mid.contains(sun_12))
        self.assertFalse(mon_sun_mid.contains(tue_00))
        self.assertTrue(mon_sun_mid.contains(tue_12))

        # Same day, hour test
        time_12_14 = OpeningPeriod.objects.create(
            store=store,
            day=SUNDAY,
            time=self.time_from_string('12:00'),
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

    @mock.patch('googlemaps.Client.geocode')
    def test_ingredientgroup(self, mock_geocode):
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

        foodtype = FoodType.objects.create(name='type')

        group = IngredientGroup(
            name='group',
            foodtype=foodtype,
            store=store,
            maximum=0,
            minimum=1
        )

        try:
            group.save()
        except ValidationError:
            try:
                group.minimum = 0
                group.save()

                group.maximum = 1
                group.save()
            except Exception as e:
                self.fail(e)
        else:
            self.fail()

    @mock.patch('googlemaps.Client.geocode')
    def test_quantity(self, mock_geocode):
        self.mock_geocode_results(mock_geocode)
        foodtype = FoodType.objects.create(name='type')

        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        self.assertRaises(
            ValidationError,
            Quantity.objects.create,
            foodtype=foodtype,
            store=store,
            min=2,
            max=1
        )

        Quantity.objects.create(
            foodtype=foodtype,
            store=store,
            min=1,
            max=2
        )

    @mock.patch('googlemaps.Client.geocode')
    def test_foodtype(self, mock_geocode):
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

        foodtype = FoodType.objects.create(name='type')

        quantity = Quantity.objects.create(
            foodtype=foodtype,
            store=store,
            min=1,
            max=10
        )

        inputtypes = [
            {
                'type': INPUT_AMOUNT,
                'float': False,
                'integer': True
            }, {
                'type': INPUT_SI_SET,
                'float': True,
                'integer': True
            }, {
                'type': INPUT_SI_VARIABLE,
                'float': True,
                'integer': True
            }
        ]

        for it in inputtypes:
            foodtype.inputtype = it['type']

            self.assertEqual(foodtype.is_valid_amount(1), it['integer'])
            self.assertEqual(foodtype.is_valid_amount(1.5), it['float'])

            quantity.min = 1.5
            quantity.max = 9.5

            try:
                quantity.save()
            except:
                if it['float']:
                    self.fail(
                        'Input type is float, but raises exception.'
                    )
                elif it['integer']:
                    quantity.min = 1
                    quantity.max = 9

                    try:
                        quantity.save()
                    except:
                        self.fail(
                            'Input type is integer, but raises exception.'
                        )

    @mock.patch('googlemaps.Client.geocode')
    def test_food_orderable(self, mock_geocode):
        self.mock_geocode_results(mock_geocode)
        preorder_time = time(hour=12)

        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10,
            preorder_time=preorder_time,
            wait=timedelta()
        )

        foodtype = FoodType.objects.create(
            name='Test foodtype'
        )

        menu = Menu.objects.create(
            name='Test menu',
            store=store
        )

        food = Food.objects.create(
            name='Test food',
            cost=1,
            foodtype=foodtype,
            menu=menu,
            store=store,
            preorder_days=0
        )

        now = datetime.now()
        now = now.replace(hour=12, minute=0)

        pickup = datetime.now()
        pickup = pickup.replace(hour=12, minute=0)

        for i in range(2):
            # Ordering without preorder_days should always return true
            now -= timedelta(hours=1)
            self.assertTrue(food.is_orderable(pickup, now=now))

            now += timedelta(hours=2)
            self.assertTrue(food.is_orderable(pickup, now=now))

            # Ordering before the preorder_time should add 1 preorder_day in the background
            # and should therefore return false if wanting to pick up the next day.

            # with preorder_days == 1, same day order is impossible
            food.preorder_days = 1
            food.save()
            now -= timedelta(hours=2)
            self.assertFalse(food.is_orderable(pickup, now=now))

            now += timedelta(hours=2)
            self.assertFalse(food.is_orderable(pickup, now=now))

            # with preorder_days == 1:
            #   * ordering before preorder_time should allow for next day ordering.
            #   * ordering after preorder_time should not allow for next day ordering.
            pickup += timedelta(days=1)
            now -= timedelta(hours=2)
            self.assertTrue(food.is_orderable(pickup, now=now))

            now += timedelta(hours=2)
            self.assertFalse(food.is_orderable(pickup, now=now))

            # If it's ordered for within 2 days, before/after preorder_time doesn't matter
            pickup += timedelta(days=1)
            now -= timedelta(hours=2)
            self.assertTrue(food.is_orderable(pickup, now=now))

            now += timedelta(hours=2)
            self.assertTrue(food.is_orderable(pickup, now=now))

            # with preorder_days == 2:
            #   * ordering before preorder_time should allow for 2 day ordering.
            #   * ordering after preorder_time should not allow for 2 day ordering.
            food.preorder_days = 2
            food.save()
            now -= timedelta(hours=2)
            self.assertTrue(food.is_orderable(pickup, now=now))

            now += timedelta(hours=2)
            self.assertFalse(food.is_orderable(pickup, now=now))

            # If it's ordered for within 3 days, before/after preorder_time doesn't matter
            pickup += timedelta(days=1)
            now -= timedelta(hours=2)
            self.assertTrue(food.is_orderable(pickup, now=now))

            now += timedelta(hours=2)
            self.assertTrue(food.is_orderable(pickup, now=now))

            food.preorder_days = 0
            food.save()
            now = datetime.now()
            now = now.replace(hour=12, minute=0)
            pickup = datetime.now()
            pickup = pickup.replace(hour=14, minute=0)
