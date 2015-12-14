import mock
from django.db import models as django_models
from django.test import TestCase
from gocardless_pro import resources

from . import models
from .config import SCHEMES
from .utils import model_from_links


class DjangoGoCardlessTestCase(TestCase):

    def setUp(self):
        pass

    def assertModelEqual(self, model, expected):
        fields = model.__class__._meta.get_fields()

        for field in fields:
            value = getattr(model, field.name)

            if 'links' in expected and field.name in expected['links']:
                expected_value = model_from_links(
                    expected['links'],
                    field.name
                )
            else:
                if field.name in expected:
                    expected_value = expected[field.name]
                else:
                    if issubclass(field.__class__, django_models.CharField):
                        expected_value = ''
                    else:
                        expected_value = None

            self.assertEqual(value, expected_value)

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

        customer = models.Customer.objects.create(
            id=mocked_info['id'],
        )

        customer.fetch()
        self.assertModelEqual(customer, mocked_info)

        # Deleting the company name should set it to '' in the database
        del mocked_info['company_name']
        mocked_info['given_name'] = 'Given name'
        mocked_info['family_name'] = 'Family name'

        mock_get.return_value = resources.Customer(mocked_info, None)

        customer.fetch()
        self.assertModelEqual(customer, mocked_info)

    @mock.patch('gocardless_pro.services.CustomerBankAccountsService.get')
    def test_fetch_customer_bank_account(self, mock_get):
        customer_id = 'CU123'

        mocked_info = {
            'id': 'BA123',
            'account_holder_name': 'Jar Jar Binks, Sith Lord',
            'account_number_ending': '12',
            'bank_name': 'Monopoly',
            'country_code': 'US',
            'created_at': '2015-12-30T23:59:59.999Z',
            'currency': 'EUR',
            'enabled': True,
            'links': {
                'customer': customer_id,
            }
        }

        mock_get.return_value = resources.CustomerBankAccount(mocked_info, None)

        customer_bank_account = models.CustomerBankAccount.objects.create(
            id=mocked_info['id'],
        )

        customer_bank_account.fetch()
        self.assertModelEqual(customer_bank_account, mocked_info)
        customer = models.Customer.objects.get(id=customer_id)

        # Deleting the link should delete the link locally too
        del mocked_info['links']

        mock_get.return_value = resources.CustomerBankAccount(mocked_info, None)

        customer_bank_account.fetch()
        self.assertModelEqual(customer_bank_account, mocked_info)

        # Deleting the customer link should recreate it after a fetch
        mocked_info['links'] = {
            'customer': customer.id,
        }
        mock_get.return_value = resources.CustomerBankAccount(mocked_info, None)

        customer_bank_account.fetch()
        self.assertModelEqual(customer_bank_account, mocked_info)

        # Deleting the customer should delete the customer's bank account
        customer.delete()

        self.assertRaises(
            models.CustomerBankAccount.DoesNotExist,
            models.CustomerBankAccount.objects.get,
            id=mocked_info['id']
        )

    @mock.patch('gocardless_pro.services.MandatesService.get')
    def test_fetch_mandate(self, mock_get):
        customer_bank_account_id = 'BA123'

        mocked_info = {
            'id': 'MD123',
            'created_at': '2015-12-30T23:59:59.999Z',
            'next_possible_charge_date': '2016-01-10',
            'reference': 'reference',
            'scheme': SCHEMES[0][0],
            'links': {
                'customer_bank_account': customer_bank_account_id,
            }
        }

        mock_get.return_value = resources.Mandate(mocked_info, None)

        mandate = models.Mandate.objects.create(
            id=mocked_info['id'],
        )

        mandate.fetch()
        self.assertModelEqual(mandate, mocked_info)
        customer_bank_account = models.CustomerBankAccount.objects.get(
            id=customer_bank_account_id
        )

        # Deleting the link should delete the link locally too
        del mocked_info['links']

        mock_get.return_value = resources.Mandate(mocked_info, None)

        mandate.fetch()
        self.assertModelEqual(mandate, mocked_info)

        # Deleting the customer bank account link should recreate it after a fetch
        mocked_info['links'] = {
            'customer_bank_account': customer_bank_account.id,
        }
        mock_get.return_value = resources.Mandate(mocked_info, None)

        mandate.fetch()
        self.assertModelEqual(mandate, mocked_info)

        # Deleting the custom bank account should delete the mandate
        customer_bank_account.delete()

        self.assertRaises(
            models.Mandate.DoesNotExist,
            models.Mandate.objects.get,
            id=mocked_info['id']
        )
