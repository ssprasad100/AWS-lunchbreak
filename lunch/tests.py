from lunch.exceptions import AddressNotFound
from lunch.models import Store
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
