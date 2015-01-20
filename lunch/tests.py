from rest_framework.test import APITestCase

from lunch.models import Store
from lunch.exceptions import AddressNotFound


class LunchbreakTests(APITestCase):

    def setUp(self):
        super(LunchbreakTests, self).setUp()

    def testAddressNotFound(self):
        ''' Test for the AddressNotFound exception. '''
        invalidStore = Store(name='test', country='nonexisting', province='nonexisting', city='nonexisting', code='nonexisting', street='nonexisting', number=5)
        validStore = Store(name='valid', country='Belgie', province='Oost-Vlaanderen', city='Wetteren', code='9230', street='Dendermondesteenweg', number=10)
        try:
            invalidStore.save()
        except AddressNotFound:
            try:
                validStore.save()
            except AddressNotFound:
                self.fail()
        else:
            self.fail()
