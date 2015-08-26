from customers.models import User
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from lunch import config
from rest_framework import status
from rest_framework.test import APITestCase


@override_settings(TESTING=True)
class CustomersTests(APITestCase):

    def testRegistration(self):
        url = reverse('user-registration')
        phone = '+32472907605'
        content = {
            'phone': phone
        }

        # As long as the name is not in the database, it should return 201
        for i in range(0, 2):
            response = self.client.post(url, content, format='json')
            self.assertEqual(response.content, '')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        User.objects.filter(phone=phone).delete()

    def testDemoRegistration(self):
        url = reverse('user-registration')
        content = {
            'phone': config.DEMO_PHONE
        }

        # The demo should always return 200
        response = self.client.post(url, content, format='json')
        self.assertEqual(response.content, '')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testInvalidRegistration(self):
        url = reverse('user-registration')
        content = {
            'phone': '+123456789'
        }

        response = self.client.post(url, content, format='json')
        self.assertNotEqual(response.content, '')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        content = {}

        response = self.client.post(url, content, format='json')
        self.assertNotEqual(response.content, '')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
