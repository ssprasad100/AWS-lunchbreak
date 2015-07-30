import datetime

from lunch.exceptions import AddressNotFound
from lunch.models import HolidayPeriod, OpeningHours, Store
from rest_framework.test import APITestCase


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
        except:
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
        except:
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
