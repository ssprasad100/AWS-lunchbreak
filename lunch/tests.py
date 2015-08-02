import datetime

from django.core.exceptions import ValidationError
from lunch.exceptions import AddressNotFound
from lunch.models import (FoodType, HolidayPeriod, IngredientGroup,
                          OpeningHours, Quantity, Store)
from rest_framework.test import APITestCase

from .config import INPUT_AMOUNT, INPUT_SI_SET, INPUT_SI_VARIABLE


class LunchbreakTests(APITestCase):

    def setUp(self):
        super(LunchbreakTests, self).setUp()

    def testAddressNotFound(self):
        ''' Test for the AddressNotFound exception. '''
        invalidStore = Store(name='test', country='nonexisting', province='nonexisting', city='nonexisting', postcode='nonexisting', street='nonexisting', number=5)
        validStore = Store(name='valid', country='Belgie', province='Oost-Vlaanderen', city='Wetteren', postcode='9230', street='Dendermondesteenweg', number=10)
        try:
            invalidStore.save()
        except AddressNotFound:
            try:
                validStore.save()
            except AddressNotFound:
                self.fail()
        else:
            self.fail()

    def testNearbyStores(self):
        ''' Test whether LunchbreakManager.nearby returns the right stores. '''
        Store.objects.all().delete()

        centerStore = Store(name='center', country='Belgie', province='Oost-Vlaanderen', city='Wetteren', postcode='9230', street='Dendermondesteenweg', number=10)
        underTwoKmStore = Store(name='1,34km', country='Belgie', province='Oost-Vlaanderen', city='Wetteren', postcode='9230', street='Wegvoeringstraat', number=47)
        underFiveKmStore = Store(name='4,79km', country='Belgie', province='Oost-Vlaanderen', city='Wetteren', postcode='9230', street='Wetterensteenweg', number=1)
        underEightKmStore = Store(name='7,95km', country='Belgie', province='Oost-Vlaanderen', city='Melle', postcode='9090', street='Wellingstraat', number=1)

        centerStore.save()
        underTwoKmStore.save()
        underFiveKmStore.save()
        underEightKmStore.save()

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
        store = Store(name='valid', country='Belgie', province='Oost-Vlaanderen', city='Wetteren', postcode='9230', street='Dendermondesteenweg', number=10)
        store.save()

        oh = OpeningHours(store=store, day=0, opening='00:00', closing='00:00')
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
        store = Store(name='valid', country='Belgie', province='Oost-Vlaanderen', city='Wetteren', postcode='9230', street='Dendermondesteenweg', number=10)
        store.save()

        now = datetime.datetime.now()
        hp = HolidayPeriod(store=store, description='description', start=now, end=now)
        try:
            hp.save()
        except ValidationError:
            try:
                tomorrow = now + datetime.timedelta(days=1)
                hp.end = tomorrow
                hp.save()
            except Exception as e:
                self.fail(e)
        else:
            self.fail()

    def testStoreLastModified(self):
        '''Test whether updating OpeningHours and HolidayPeriod objects updates the Store.'''
        store = Store(name='valid', country='Belgie', province='Oost-Vlaanderen', city='Wetteren', postcode='9230', street='Dendermondesteenweg', number=10)
        store.save()

        firstModified = store.lastModified

        oh = OpeningHours(store=store, day=0, opening='00:00', closing='01:00')
        oh.save()

        secondModified = store.lastModified

        self.assertGreater(secondModified, firstModified)

        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        hp = HolidayPeriod(store=store, description='description', start=now, end=tomorrow)
        hp.save()

        self.assertGreater(store.lastModified, secondModified)

    def testIngredientGroup(self):
        store = Store(name='valid', country='Belgie', province='Oost-Vlaanderen', city='Wetteren', postcode='9230', street='Dendermondesteenweg', number=10)
        store.save()

        foodType = FoodType(name='type')
        foodType.save()

        group = IngredientGroup(name='group', foodType=foodType, store=store, maximum=0, minimum=1)

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
            foodType = FoodType(name='type')
            foodType.save()

            store = Store(name='valid', country='Belgie', province='Oost-Vlaanderen', city='Wetteren', postcode='9230', street='Dendermondesteenweg', number=10)
            store.save()

            quantity = Quantity(foodType=foodType, store=store, amountMin=1, amountMax=0)
            try:
                quantity.save()
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
            store = Store(name='valid', country='Belgie', province='Oost-Vlaanderen', city='Wetteren', postcode='9230', street='Dendermondesteenweg', number=10)
            store.save()

            foodType = FoodType(name='type')
            foodType.save()

            quantity = Quantity(foodType=foodType, store=store, amountMin=0, amountMax=10)
            quantity.save()

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


