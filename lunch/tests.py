from datetime import datetime, time, timedelta

from customers.exceptions import MinTimeExceeded, PastOrderDenied, StoreClosed
from django.core.exceptions import ValidationError
from django.test.utils import override_settings
from lunch.exceptions import AddressNotFound
from lunch.models import (Food, FoodCategory, FoodType, HolidayPeriod,
                          IngredientGroup, OpeningHours, Quantity, Store)
from Lunchbreak.test import LunchbreakTestCase

from .config import INPUT_AMOUNT, INPUT_SI_SET, INPUT_SI_VARIABLE


@override_settings(TESTING=True)
class LunchbreakTests(LunchbreakTestCase):

    def testAddressNotFound(self):
        ''' Test for the AddressNotFound exception. '''
        try:
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

    def testNearbyStores(self):
        ''' Test whether LunchbreakManager.nearby returns the right stores. '''
        Store.objects.all().delete()

        centerStore = Store.objects.create(
            name='center',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
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
        underFiveKmStore = Store.objects.create(
            name='4,79km',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Wetterensteenweg',
            number=1
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
        lon = centerStore.longitude

        self.assertInCount(Store.objects.nearby(lat, lon, 1), [centerStore])

        self.assertInCount(Store.objects.nearby(lat, lon, 2), [centerStore, underTwoKmStore])

        self.assertInCount(Store.objects.nearby(lat, lon, 5), [centerStore, underTwoKmStore, underFiveKmStore])

        self.assertInCount(Store.objects.nearby(lat, lon, 8), [centerStore, underTwoKmStore, underFiveKmStore, underEightKmStore])

    def assertInCount(self, haystack, needles):
        self.assertEqual(len(haystack), len(needles))

        for needle in needles:
            self.assertIn(needle, haystack)

    def testOpeningHours(self):
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

    def testHolidayPeriod(self):
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

    def testStoreLastModified(self):
        '''Test whether updating OpeningHours and HolidayPeriod objects updates the Store.'''
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

    def testIngredientGroup(self):
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

        def testQuantity(self):
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

            try:
                quantity = Quantity.objects.create(
                    foodType=foodType,
                    store=store,
                    amountMin=1,
                    amountMax=0
                )
            except ValidationError:
                try:
                    quantity.amountMin = 0
                    quantity.amountMax = 1
                    quantity.save()
                except Exception as e:
                    self.fail(e)
            else:
                self.fail()

        def testFoodType(self):
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
                amountMin=0,
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
                except ValidationError as ve:
                    if it['float']:
                        self.fail(ve)
                    elif it['integer']:
                        quantity.amountMin = 1
                        quantity.amountMax = 9

                        try:
                            quantity.save()
                        except Exception as e:
                            self.fail(e)

    def testStoreCheckOpen(self):
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
        self.assertRaises(PastOrderDenied, Store.checkOpen, store, today, today + timedelta(hours=1))

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
        self.assertRaises(MinTimeExceeded, Store.checkOpen, store, opening + minTime - timedelta(minutes=1), opening)

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

    def testFoodCanOrder(self):
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

        pickupTime = datetime.now()
        pickupTime = pickupTime.replace(hour=12, minute=0)

        for i in range(2):
            # Ordering without minDays should always return true
            now -= timedelta(hours=1)
            self.assertTrue(food.canOrder(pickupTime, now=now))

            now += timedelta(hours=2)
            self.assertTrue(food.canOrder(pickupTime, now=now))

            # Ordering before the orderTime should add 1 minDay in the background
            # and should therefore return false if wanting to pick up the next day.

            # with minDays == 1, same day order is impossible
            food.minDays = 1
            food.save()
            now -= timedelta(hours=2)
            self.assertFalse(food.canOrder(pickupTime, now=now))

            now += timedelta(hours=2)
            self.assertFalse(food.canOrder(pickupTime, now=now))

            # with minDays == 1:
            #   * ordering before orderTime should allow for next day ordering.
            #   * ordering after orderTime should not allow for next day ordering.
            pickupTime += timedelta(days=1)
            now -= timedelta(hours=2)
            self.assertTrue(food.canOrder(pickupTime, now=now))

            now += timedelta(hours=2)
            self.assertFalse(food.canOrder(pickupTime, now=now))

            # If it's ordered for within 2 days, before/after orderTime doesn't matter
            pickupTime += timedelta(days=1)
            now -= timedelta(hours=2)
            self.assertTrue(food.canOrder(pickupTime, now=now))

            now += timedelta(hours=2)
            self.assertTrue(food.canOrder(pickupTime, now=now))

            # with minDays == 2:
            #   * ordering before orderTime should allow for 2 day ordering.
            #   * ordering after orderTime should not allow for 2 day ordering.
            food.minDays = 2
            food.save()
            now -= timedelta(hours=2)
            self.assertTrue(food.canOrder(pickupTime, now=now))

            now += timedelta(hours=2)
            self.assertFalse(food.canOrder(pickupTime, now=now))

            # If it's ordered for within 3 days, before/after orderTime doesn't matter
            pickupTime += timedelta(days=1)
            now -= timedelta(hours=2)
            self.assertTrue(food.canOrder(pickupTime, now=now))

            now += timedelta(hours=2)
            self.assertTrue(food.canOrder(pickupTime, now=now))

            food.minDays = 0
            food.save()
            now = datetime.now()
            now = now.replace(hour=12, minute=0)
            pickupTime = datetime.now()
            pickupTime = pickupTime.replace(hour=14, minute=0)
