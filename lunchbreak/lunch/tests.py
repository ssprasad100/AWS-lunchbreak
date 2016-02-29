from datetime import datetime, time, timedelta

import mock
import requests
from customers.exceptions import MinTimeExceeded, PastOrderDenied, StoreClosed
from django.core.exceptions import ValidationError
from Lunchbreak.test import LunchbreakTestCase

from .config import INPUT_AMOUNT, INPUT_SI_SET, INPUT_SI_VARIABLE
from .exceptions import AddressNotFound
from .models import (Food, FoodCategory, FoodType, HolidayPeriod,
                     IngredientGroup, OpeningHours, Quantity, Store)


class LunchTests(LunchbreakTestCase):

    MOCK_ADDRESS = {
        'results': [
            {
                'geometry': {
                    'location': {
                        'lat': 1,
                        'lng': 1
                    }
                }
            }
        ]
    }

    def mockAddressResponse(self, mock_get, mock_json, return_value=None, lat=None, lng=None):
        if return_value is None:
            return_value = self.MOCK_ADDRESS

            if lat is not None and lng is not None:
                return_value['results'][0]['geometry']['location']['lat'] = lat
                return_value['results'][0]['geometry']['location']['lng'] = lng

        mock_get.return_value = requests.Response()
        mock_json.return_value = return_value

    @mock.patch('requests.Response.json')
    @mock.patch('requests.get')
    def testAddressNotFound(self, mock_get, mock_json):
        ''' Test for the AddressNotFound exception. '''
        try:
            mock_fail = {
                'results': []
            }
            self.mockAddressResponse(mock_get, mock_json, mock_fail)
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
                self.mockAddressResponse(mock_get, mock_json)
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

    @mock.patch('requests.Response.json')
    @mock.patch('requests.get')
    def testNearbyStores(self, mock_get, mock_json):
        ''' Test whether LunchbreakManager.nearby returns the right stores. '''
        Store.objects.all().delete()

        self.mockAddressResponse(
            mock_get,
            mock_json,
            lat=51.0111595,
            lng=3.9075993
        )
        centerStore = Store.objects.create(
            name='center',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        self.mockAddressResponse(
            mock_get,
            mock_json,
            lat=51.0076504,
            lng=3.8892806
        )
        underTwoKmStore = Store.objects.create(
            name='1,34km',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Wegvoeringstraat',
            number=47
        )

        self.mockAddressResponse(
            mock_get,
            mock_json,
            lat=51.0089506,
            lng=3.8392584
        )
        underFiveKmStore = Store.objects.create(
            name='4,79km',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Wetterensteenweg',
            number=1
        )

        self.mockAddressResponse(
            mock_get,
            mock_json,
            lat=51.0267939,
            lng=3.7968594
        )
        underEightKmStore = Store.objects.create(
            name='7,95km',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Melle',
            postcode='9090',
            street='Wellingstraat',
            number=1
        )

        lat = centerStore.latitude
        lng = centerStore.longitude

        self.assertInCount(
            Store.objects.nearby(lat, lng, 1),
            [centerStore]
        )
        self.assertInCount(
            Store.objects.nearby(lat, lng, 2),
            [centerStore, underTwoKmStore]
        )
        self.assertInCount(
            Store.objects.nearby(lat, lng, 5),
            [centerStore, underTwoKmStore, underFiveKmStore]
        )
        self.assertInCount(
            Store.objects.nearby(lat, lng, 8),
            [centerStore, underTwoKmStore, underFiveKmStore, underEightKmStore]
        )

    def assertInCount(self, haystack, needles):
        self.assertEqual(len(haystack), len(needles))

        for needle in needles:
            self.assertIn(needle, haystack)

    @mock.patch('requests.Response.json')
    @mock.patch('requests.get')
    def testOpeningHours(self, mock_get, mock_json):
        self.mockAddressResponse(mock_get, mock_json)
        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )
        oh = OpeningHours(
            store=store,
            day=0,
            opening='00:00',
            closing='00:00'
        )

        try:
            oh.save()
        except ValidationError:
            try:
                oh.closing = '00:01'
                oh.save()
            except Exception as e:
                self.fail(e)
        else:
            self.fail()

    @mock.patch('requests.Response.json')
    @mock.patch('requests.get')
    def testHolidayPeriod(self, mock_get, mock_json):
        self.mockAddressResponse(mock_get, mock_json)
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

    @mock.patch('requests.Response.json')
    @mock.patch('requests.get')
    def testStoreLastModified(self, mock_get, mock_json):
        '''Test whether updating OpeningHours and HolidayPeriod objects updates the Store.'''
        self.mockAddressResponse(mock_get, mock_json)
        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        firstModified = store.lastModified

        OpeningHours.objects.create(
            store=store, day=0,
            opening='00:00',
            closing='01:00'
        )

        secondModified = store.lastModified

        self.assertGreater(secondModified, firstModified)

        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        HolidayPeriod.objects.create(
            store=store,
            description='description',
            start=now,
            end=tomorrow
        )

        self.assertGreater(store.lastModified, secondModified)

    @mock.patch('requests.Response.json')
    @mock.patch('requests.get')
    def testIngredientGroup(self, mock_get, mock_json):
        self.mockAddressResponse(mock_get, mock_json)
        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        foodType = FoodType.objects.create(name='type')

        group = IngredientGroup(
            name='group',
            foodType=foodType,
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

    @mock.patch('requests.Response.json')
    @mock.patch('requests.get')
    def testQuantity(self, mock_get, mock_json):
        self.mockAddressResponse(mock_get, mock_json)
        foodType = FoodType.objects.create(name='type')

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
            foodType=foodType,
            store=store,
            amountMin=2,
            amountMax=1
        )

        Quantity.objects.create(
            foodType=foodType,
            store=store,
            amountMin=1,
            amountMax=2
        )

    @mock.patch('requests.Response.json')
    @mock.patch('requests.get')
    def testFoodType(self, mock_get, mock_json):
        self.mockAddressResponse(mock_get, mock_json)
        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        foodType = FoodType.objects.create(name='type')

        quantity = Quantity.objects.create(
            foodType=foodType,
            store=store,
            amountMin=1,
            amountMax=10
        )

        inputTypes = [
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

        for it in inputTypes:
            foodType.inputType = it['type']

            self.assertEqual(foodType.isValidAmount(1), it['integer'])
            self.assertEqual(foodType.isValidAmount(1.5), it['float'])

            quantity.amountMin = 1.5
            quantity.amountMax = 9.5

            try:
                quantity.save()
            except:
                if it['float']:
                    self.fail(
                        'Input type is float, but raises exception.'
                    )
                elif it['integer']:
                    quantity.amountMin = 1
                    quantity.amountMax = 9

                    try:
                        quantity.save()
                    except:
                        self.fail(
                            'Input type is integer, but raises exception.'
                        )

    @mock.patch('requests.Response.json')
    @mock.patch('requests.get')
    def testStoreCheckOpen(self, mock_get, mock_json):
        self.mockAddressResponse(mock_get, mock_json)
        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        today = datetime.now()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)

        # PastOrderDenied
        self.assertRaises(
            PastOrderDenied, Store.checkOpen, store, today, today + timedelta(hours=1))

        # MinTimeExceeded
        minTime = timedelta(minutes=15)
        openingMinTime = minTime * 2
        closingHours = 10
        store.minTime = minTime

        opening = (today + openingMinTime)
        closing = (opening + timedelta(hours=closingHours))
        day = opening.strftime('%w')
        OpeningHours.objects.create(
            store=store,
            day=day,
            opening=opening,
            closing=closing
        )
        self.assertRaises(MinTimeExceeded, Store.checkOpen, store,
                          opening + minTime - timedelta(minutes=1), opening)

        # Before and after opening hours
        before = opening - timedelta(minutes=1)
        between = opening + timedelta(hours=closingHours / 2)
        after = closing + timedelta(hours=1)
        end = after + timedelta(hours=1)

        self.assertRaises(StoreClosed, Store.checkOpen, store, before, today)
        self.assertIsNone(Store.checkOpen(store, between, today))
        self.assertRaises(StoreClosed, Store.checkOpen, store, after, today)

        hp = HolidayPeriod.objects.create(
            store=store,
            start=today,
            end=end,
            closed=True
        )
        self.assertRaises(StoreClosed, Store.checkOpen, store, before, today)

        self.assertRaises(StoreClosed, Store.checkOpen, store, between, today)
        self.assertRaises(StoreClosed, Store.checkOpen, store, after, today)

        hp.closed = False
        hp.save()
        self.assertIsNone(Store.checkOpen(store, before, today))
        self.assertIsNone(Store.checkOpen(store, between, today))
        self.assertIsNone(Store.checkOpen(store, after, today))

        hp.closed = True
        hp.end = between
        hp.save()
        self.assertRaises(StoreClosed, Store.checkOpen, store, before, today)
        self.assertRaises(StoreClosed, Store.checkOpen, store, between, today)
        self.assertIsNone(Store.checkOpen(store, between + timedelta(minutes=1), today))

    @mock.patch('requests.Response.json')
    @mock.patch('requests.get')
    def testFoodCanOrder(self, mock_get, mock_json):
        self.mockAddressResponse(mock_get, mock_json)
        orderTime = time(hour=12)

        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10,
            orderTime=orderTime,
            minTime=timedelta()
        )

        foodType = FoodType.objects.create(
            name='Test foodType'
        )

        foodCategory = FoodCategory.objects.create(
            name='Test foodCategory',
            store=store
        )

        food = Food.objects.create(
            name='Test food',
            cost=1,
            foodType=foodType,
            category=foodCategory,
            store=store,
            minDays=0
        )

        now = datetime.now()
        now = now.replace(hour=12, minute=0)

        pickup = datetime.now()
        pickup = pickup.replace(hour=12, minute=0)

        for i in range(2):
            # Ordering without minDays should always return true
            now -= timedelta(hours=1)
            self.assertTrue(food.canOrder(pickup, now=now))

            now += timedelta(hours=2)
            self.assertTrue(food.canOrder(pickup, now=now))

            # Ordering before the orderTime should add 1 minDay in the background
            # and should therefore return false if wanting to pick up the next day.

            # with minDays == 1, same day order is impossible
            food.minDays = 1
            food.save()
            now -= timedelta(hours=2)
            self.assertFalse(food.canOrder(pickup, now=now))

            now += timedelta(hours=2)
            self.assertFalse(food.canOrder(pickup, now=now))

            # with minDays == 1:
            #   * ordering before orderTime should allow for next day ordering.
            #   * ordering after orderTime should not allow for next day ordering.
            pickup += timedelta(days=1)
            now -= timedelta(hours=2)
            self.assertTrue(food.canOrder(pickup, now=now))

            now += timedelta(hours=2)
            self.assertFalse(food.canOrder(pickup, now=now))

            # If it's ordered for within 2 days, before/after orderTime doesn't matter
            pickup += timedelta(days=1)
            now -= timedelta(hours=2)
            self.assertTrue(food.canOrder(pickup, now=now))

            now += timedelta(hours=2)
            self.assertTrue(food.canOrder(pickup, now=now))

            # with minDays == 2:
            #   * ordering before orderTime should allow for 2 day ordering.
            #   * ordering after orderTime should not allow for 2 day ordering.
            food.minDays = 2
            food.save()
            now -= timedelta(hours=2)
            self.assertTrue(food.canOrder(pickup, now=now))

            now += timedelta(hours=2)
            self.assertFalse(food.canOrder(pickup, now=now))

            # If it's ordered for within 3 days, before/after orderTime doesn't matter
            pickup += timedelta(days=1)
            now -= timedelta(hours=2)
            self.assertTrue(food.canOrder(pickup, now=now))

            now += timedelta(hours=2)
            self.assertTrue(food.canOrder(pickup, now=now))

            food.minDays = 0
            food.save()
            now = datetime.now()
            now = now.replace(hour=12, minute=0)
            pickup = datetime.now()
            pickup = pickup.replace(hour=14, minute=0)
