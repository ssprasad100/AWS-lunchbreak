import mock
from django.test import TestCase
from gocardless_pro import resources
from django.db import models as django_models

from . import models


class DjangoGoCardlessTestCase(TestCase):

    def setUp(self):
        pass

    def assertModelEqual(self, model, expected):
        fields = model.__class__._meta.get_fields()

        for field in fields:
            expected_value = expected[field.name]\
                if field.name in expected\
                else '' if issubclass(field.__class__, django_models.CharField) else None
            self.assertEqual(getattr(model, field.name), expected_value)

    @mock.patch('gocardless_pro.services.CustomersService.get')
    def test_fetch_customer(self, mock_get):
        mocked_info = {
            'id': 'CU123',
            'address_line1': 'Address line 1',
            'address_line2': 'Address line 2',
            'address_line3': 'Address line 3',
            'city': 'Coruscant',
            'company_name': 'Lucas',
            'country_code': 'US',
            'created_at': '2015-12-30T23:59:59.999Z',
            'email': 'user@example.com',
            'language': 'en',
            'postal_code': '123',
            'region': 'California',
        }

        mock_get.return_value = resources.Customer(mocked_info, None)

        customer = models.Customer(
            id='CU123',
        )

        customer.fetch()

        self.assertModelEqual(customer, mocked_info)

        del mocked_info['company_name']
        mocked_info['given_name'] = 'Given name'
        mocked_info['family_name'] = 'Family name'

        mock_get.return_value = resources.Customer(mocked_info, None)

        customer.fetch()
        self.assertModelEqual(customer, mocked_info)
