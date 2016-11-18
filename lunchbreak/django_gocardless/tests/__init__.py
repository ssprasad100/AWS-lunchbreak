from django.db import models as django_models
from django.test import TestCase

from ..config import CURRENCIES, SCHEMES
from ..utils import field_default, model_from_links


class GCTestCase(TestCase):

    CUSTOMER_INFO = {
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
    CUSTOMER_BANK_ACCOUNT_INFO = {
        'id': 'BA123',
        'account_holder_name': 'Jar Jar Binks, Sit',
        'account_number_ending': '12',
        'bank_name': 'Monopoly',
        'country_code': 'US',
        'created_at': '2015-12-30T23:59:59.999Z',
        'currency': 'EUR',
        'enabled': True,
        'links': {
            'customer': CUSTOMER_INFO['id'],
        },
    }
    MANDATE_INFO = {
        'id': 'MD123',
        'created_at': '2015-12-30T23:59:59.999Z',
        'next_possible_charge_date': '2016-01-10',
        'reference': 'reference',
        'scheme': SCHEMES[0][0],
        'links': {
            'customer_bank_account': CUSTOMER_BANK_ACCOUNT_INFO['id'],
        },
    }
    REDIRECTFLOW_INFO = {
        'id': 'RE123',
        'description': 'Description',
        'scheme': SCHEMES[0][0],
        'created_at': '2015-12-30T23:59:59.999Z',
        'redirect_url': 'https://example.com',
    }
    SUBSCRIPTION_INFO = {
        'id': 'SU123',
        'created_at': '2014-10-20T17:01:06.000Z',
        'amount': 2500,
        'currency': CURRENCIES[1][0],
        'status': 'active',
        'name': 'Monthly Magazine',
        'start_date': '2014-11-03',
        'end_date': None,
        'interval': 1,
        'interval_unit': 'monthly',
        'day_of_month': 1,
        'month': None,
        'payment_reference': None,
        'upcoming_payments': [
            {
                'charge_date': '2014-11-03',
                'amount': 2500,
            },
            {
                'charge_date': '2014-12-01',
                'amount': 2500,
            },
            {
                'charge_date': '2015-01-02',
                'amount': 2500,
            },
            {
                'charge_date': '2015-02-02',
                'amount': 2500,
            },
            {
                'charge_date': '2015-03-02',
                'amount': 2500,
            },
            {
                'charge_date': '2015-04-01',
                'amount': 2500,
            },
            {
                'charge_date': '2015-05-01',
                'amount': 2500,
            },
            {
                'charge_date': '2015-06-01',
                'amount': 2500,
            },
            {
                'charge_date': '2015-07-01',
                'amount': 2500,
            },
            {
                'charge_date': '2015-08-03',
                'amount': 2500,
            }
        ],
        'metadata': {
            'order_no': 'ABCD1234',
        },
        'links': {
            'mandate': MANDATE_INFO['id'],
        },
    }

    def assertModelEqual(self, model, expected):
        fields = model.__class__._meta.get_fields()
        ignore_fields = getattr(model.__class__, 'ignore_fields', [])

        for field in fields:
            if field.name in ignore_fields:
                continue

            if not issubclass(field.__class__, django_models.fields.Field):
                continue

            value = getattr(model, field.name)

            if 'links' in expected and field.name in expected['links']:
                expected_value = model_from_links(
                    expected['links'],
                    field.name
                )
            else:
                expected_value = expected.get(field.name, None)
                if expected_value is None:
                    expected_value = field_default(field)

            self.assertEqual(value, expected_value)
