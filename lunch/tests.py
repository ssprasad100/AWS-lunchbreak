from rest_framework.test import APITestCase

from lunch.models import Store
from lunch.exceptions import AddressNotFound


class LunchbreakTests(APITestCase):

    def setUp(self):
        super(LunchbreakTests, self).setUp()

    def testAddressNotFound(self):
        ''' Test for the AddressNotFound exception. '''
        store = Store(name='test', country='nonexisting', province='nonexisting', city='nonexisting', code='nonexisting', street='nonexisting', number=5)
        try:
            store.save()
        except AddressNotFound:
            pass
        else:
            self.fail()
