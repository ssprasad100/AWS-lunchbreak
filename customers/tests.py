from customers import views
from customers.config import DEMO_DIGITS_ID, DEMO_PHONE
from customers.exceptions import UserNameEmpty
from customers.models import Heart, User, UserToken
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test.utils import override_settings
from lunch.exceptions import BadRequest, DoesNotExist
from lunch.models import Store
from Lunchbreak.test import LunchbreakTestCase
from push_notifications.models import SERVICE_APNS
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate


@override_settings(TESTING=True)
class CustomersTests(LunchbreakTestCase):

    PHONE_USER = '+32472907604'
    NAME_USER = 'Meneer Aardappel'
    FORMAT = 'json'
    VALID_PHONE = '+32472907605'
    INVALID_PHONE = '+123456789'
    PIN = '123456'
    NAME = 'Meneer De Bolle'
    NAME_ALTERNATE = 'Mevrouw De Bolle'
    DEVICE = 'Test device'
    REGISTRATION_ID = '123456789'

    def setUp(self):
        super(CustomersTests, self).setUp()
        self.factory = APIRequestFactory()
        self.user = User.objects.create(
            phone=CustomersTests.PHONE_USER,
            name=CustomersTests.NAME_USER
        )

    def testRegistration(self):
        url = reverse('user-registration')
        content = {
            'phone': CustomersTests.VALID_PHONE
        }

        # As long as the name is not in the database, it should return 201
        for i in range(0, 2):
            response = self.client.post(url, content, format=CustomersTests.FORMAT)
            self.assertEqual(response.content, '')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        User.objects.filter(phone=CustomersTests.VALID_PHONE).delete()

    def testDemoRegistration(self):
        url = reverse('user-registration')
        content = {
            'phone': DEMO_PHONE
        }

        # The demo should always return 200
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqual(response.content, '')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testInvalidRegistration(self):
        url = reverse('user-registration')
        content = {
            'phone': CustomersTests.INVALID_PHONE
        }

        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqualException(response, BadRequest)

        content = {}

        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqualException(response, BadRequest)

    def testLogin(self):
        url = reverse('user-login')
        content = {
            'phone': CustomersTests.VALID_PHONE,
            'pin': CustomersTests.PIN,
            'token': {
                'device': CustomersTests.DEVICE,
                'service': SERVICE_APNS,
                'registration_id': CustomersTests.REGISTRATION_ID
            }
        }

        # You cannot login without registering first
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqualException(response, DoesNotExist)

        user = User.objects.create(phone=CustomersTests.VALID_PHONE)

        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqualException(response, UserNameEmpty)
        self.assertFalse(user.name)
        self.assertFalse(user.confirmedAt)

        content['name'] = CustomersTests.NAME
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user.refresh_from_db()
        tokens = UserToken.objects.filter(user=user)
        self.assertEqual(len(tokens), 1)
        identifier = tokens[0].identifier
        self.assertTrue(user.confirmedAt)
        self.assertEqual(user.name, CustomersTests.NAME)
        confirmedAt = user.confirmedAt

        content['name'] = CustomersTests.NAME_ALTERNATE
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        tokens = UserToken.objects.filter(user=user)
        self.assertEqual(len(tokens), 1)
        self.assertNotEqual(identifier, tokens[0].identifier)
        self.assertEqual(user.name, CustomersTests.NAME_ALTERNATE)
        self.assertEqual(user.confirmedAt, confirmedAt)

        user.delete()

    def testDemoLogin(self):
        url = reverse('user-login')

        content = {
            'phone': DEMO_PHONE,
            'pin': CustomersTests.PIN,
            'token': {
                'device': CustomersTests.DEVICE,
                'service': SERVICE_APNS,
                'registration_id': CustomersTests.REGISTRATION_ID
            }
        }

        # Demo account is only allowed when it's in the database
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqualException(response, BadRequest)

        demoPin = '1337'
        demo = User.objects.create(phone=DEMO_PHONE, requestId=demoPin, digitsId=DEMO_DIGITS_ID)

        # Invalid pin
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqualException(response, BadRequest)

        content['pin'] = demoPin
        response = self.client.post(url, content, format=CustomersTests.FORMAT)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserToken.objects.filter(user=demo).count(), 1)

        demo.delete()

    def authenticateRequest(self, request, view, *args, **kwargs):
        force_authenticate(request, user=self.user)
        return view.as_view()(request, *args, **kwargs)

    def testHearting(self):
        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        heartKwargs = {'option': 'heart', 'pk': store.id}
        heartUrl = reverse('store-heart', kwargs=heartKwargs)
        unheartKwargs = {'option': 'unheart', 'pk': store.id}
        unheartUrl = reverse('store-heart', kwargs=unheartKwargs)

        request = self.factory.patch(heartUrl, {}, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.StoreHeartView, **heartKwargs)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Heart.objects.filter(user=self.user).count(), 1)

        request = self.factory.patch(heartUrl, {}, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.StoreHeartView, **heartKwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Heart.objects.filter(user=self.user).count(), 1)

        request = self.factory.patch(unheartUrl, {}, format=CustomersTests.FORMAT)
        response = self.authenticateRequest(request, views.StoreHeartView, **unheartKwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Heart.objects.filter(user=self.user).count(), 0)

        request = self.factory.patch(unheartUrl, {}, format=CustomersTests.FORMAT)
        self.assertRaises(Http404, self.authenticateRequest, request, views.StoreHeartView, **unheartKwargs)
