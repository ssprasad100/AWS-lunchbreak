import copy

import mock
from django.db import models as django_models
from django.test import TestCase
from gocardless_pro import resources

from . import models
from .config import CURRENCIES, PAYOUT_STATUSES, SCHEMES
from .handlers import EventHandler
from .utils import field_default, model_from_links


class DjangoGoCardlessTestCase(TestCase):

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

        for field in fields:
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

    def test_event_actions_connected(self):
        for client_property, actions in EventHandler.ACTIONS.items():
            for method_name, signal in actions.items():
                self.assertEqual(1, len(signal.receivers))

    @mock.patch('gocardless_pro.services.CustomersService.get')
    def test_customer_fetch(self, mock_customer):
        mocked_info = copy.deepcopy(self.CUSTOMER_INFO)

        mock_customer.return_value = resources.Customer(
            mocked_info,
            None
        )

        customer = models.Customer.objects.create(
            id=mocked_info['id'],
        )

        models.Customer.fetch(customer)
        self.assertModelEqual(customer, mocked_info)

        # Deleting the company name should set it to '' in the database
        del mocked_info['company_name']
        mocked_info['given_name'] = 'Given name'
        mocked_info['family_name'] = 'Family name'

        mock_customer.return_value = resources.Customer(
            mocked_info,
            None
        )

        models.Customer.fetch(customer)
        self.assertModelEqual(customer, mocked_info)

        customer.delete()

    @mock.patch('gocardless_pro.services.CustomersService.get')
    @mock.patch('gocardless_pro.services.CustomerBankAccountsService.get')
    def test_customer_bank_account_fetch(self, mock_bank, mock_customer):
        mocked_info = copy.deepcopy(self.CUSTOMER_BANK_ACCOUNT_INFO)

        mock_customer.return_value = resources.Customer(self.CUSTOMER_INFO, None)
        mock_bank.return_value = resources.CustomerBankAccount(
            mocked_info,
            None
        )

        customer_bank_account = models.CustomerBankAccount.objects.create(
            id=mocked_info['id'],
        )

        models.CustomerBankAccount.fetch(customer_bank_account)
        self.assertModelEqual(customer_bank_account, mocked_info)
        customer = models.Customer.objects.get(
            id=self.CUSTOMER_INFO['id']
        )

        # Deleting the link should not delete the link locally
        del mocked_info['links']

        mock_bank.return_value = resources.CustomerBankAccount(
            mocked_info,
            None
        )

        models.CustomerBankAccount.fetch(customer_bank_account)
        self.assertModelEqual(customer_bank_account, self.CUSTOMER_BANK_ACCOUNT_INFO)

        # Deleting the customer should delete the customer's bank account
        customer.delete()

        self.assertRaises(
            models.CustomerBankAccount.DoesNotExist,
            models.CustomerBankAccount.objects.get,
            id=mocked_info['id']
        )

    @mock.patch('gocardless_pro.services.CustomerBankAccountsService.get')
    @mock.patch('gocardless_pro.services.CustomersService.get')
    @mock.patch('gocardless_pro.services.MandatesService.get')
    def test_mandate_fetch(self, mock_mandate, mock_customer, mock_bank):
        mocked_info = copy.deepcopy(self.MANDATE_INFO)

        mock_mandate.return_value = resources.Mandate(
            mocked_info,
            None
        )
        mock_customer.return_value = resources.Customer(
            self.CUSTOMER_INFO,
            None
        )
        mock_bank.return_value = resources.CustomerBankAccount(
            self.CUSTOMER_BANK_ACCOUNT_INFO,
            None
        )

        mandate = models.Mandate.objects.create(
            id=mocked_info['id'],
        )

        models.Mandate.fetch(mandate)
        self.assertModelEqual(mandate, mocked_info)
        customer_bank_account = models.CustomerBankAccount.objects.get(
            id=mocked_info['links']['customer_bank_account']
        )

        # Deleting the link should not delete the link locally
        del mocked_info['links']

        mock_mandate.return_value = resources.Mandate(
            mocked_info,
            None
        )

        models.Mandate.fetch(mandate)
        self.assertModelEqual(mandate, self.MANDATE_INFO)

        # Deleting the customer bank account should delete the mandate
        customer_bank_account.delete()

        self.assertRaises(
            models.Mandate.DoesNotExist,
            models.Mandate.objects.get,
            id=mocked_info['id']
        )

    @mock.patch('gocardless_pro.services.CustomerBankAccountsService.get')
    @mock.patch('gocardless_pro.services.CustomersService.get')
    @mock.patch('gocardless_pro.services.MandatesService.get')
    @mock.patch('gocardless_pro.services.RedirectFlowsService.create')
    @mock.patch('gocardless_pro.services.RedirectFlowsService.complete')
    def test_redirectflow_create_complete(self, mock_create, mock_complete,
                                          mock_mandate, mock_customer, mock_bank):
        links = {
            'customer': self.CUSTOMER_INFO['id'],
            'customer_bank_account': self.CUSTOMER_BANK_ACCOUNT_INFO['id'],
            'mandate': self.MANDATE_INFO['id'],
        }

        mocked_info = copy.deepcopy(self.REDIRECTFLOW_INFO)

        mock_mandate.return_value = resources.Mandate(
            self.MANDATE_INFO,
            None
        )
        mock_customer.return_value = resources.Customer(
            self.CUSTOMER_INFO,
            None
        )
        mock_bank.return_value = resources.CustomerBankAccount(
            self.CUSTOMER_BANK_ACCOUNT_INFO,
            None
        )

        # Workaround so side_effect can modify last_mocked_result
        last_mocked_result = [None]

        def side_effect(id=None, params=[]):
            mocked_result = copy.deepcopy(mocked_info)

            same_return_values = [
                'session_token',
                'description',
                'success_redirect_url'
            ]

            for same_return_value in same_return_values:
                if same_return_value in params:
                    mocked_result[same_return_value] = params[same_return_value]

            last_mocked_result[0] = mocked_result
            return resources.RedirectFlow(mocked_result, None)

        mock_create.side_effect = side_effect
        mock_complete.side_effect = side_effect

        for field, identifier in links.items():
            if 'links' in mocked_info:
                del mocked_info['links']

            redirectflow = models.RedirectFlow.create()
            self.assertModelEqual(redirectflow, last_mocked_result[0])

            mocked_info['links'] = links

            redirectflow.complete()
            self.assertModelEqual(redirectflow, last_mocked_result[0])

            # Deleting any of the relations should result in the RedirectFlow being deleted
            rel_model = models.RedirectFlow._meta.get_field(field).rel.to
            rel_instance = rel_model.objects.get(
                id=identifier
            )
            rel_instance.delete()

            self.assertRaises(
                models.RedirectFlow.DoesNotExist,
                models.RedirectFlow.objects.get,
                id=mocked_info['id']
            )

    @mock.patch('gocardless_pro.services.CustomerBankAccountsService.get')
    @mock.patch('gocardless_pro.services.CustomersService.get')
    @mock.patch('gocardless_pro.services.MandatesService.get')
    @mock.patch('gocardless_pro.services.RedirectFlowsService.get')
    def test_redirectflow_fetch(self, mock_redirect, mock_mandate,
                                mock_customer, mock_bank):
        links = {
            'customer': self.CUSTOMER_INFO['id'],
            'customer_bank_account': self.CUSTOMER_BANK_ACCOUNT_INFO['id'],
            'mandate': self.MANDATE_INFO['id'],
        }

        session_token = 'SESS_somerandomtoken'

        mocked_info = copy.deepcopy(self.REDIRECTFLOW_INFO)
        mocked_info.update({
            'session_token': session_token,
            'success_redirect_url': 'https://success.com',
            'links': links,
        })

        mock_redirect.return_value = resources.RedirectFlow(
            mocked_info,
            None
        )
        mock_mandate.return_value = resources.Mandate(
            self.MANDATE_INFO,
            None
        )
        mock_customer.return_value = resources.Customer(
            self.CUSTOMER_INFO,
            None
        )
        mock_bank.return_value = resources.CustomerBankAccount(
            self.CUSTOMER_BANK_ACCOUNT_INFO,
            None
        )

        for field, identifier in links.items():
            if 'links' in mocked_info:
                del mocked_info['links']

            redirectflow = models.RedirectFlow.objects.create(
                id=mocked_info['id'],
                session_token=session_token
            )
            mock_redirect.return_value = resources.RedirectFlow(
                mocked_info,
                None
            )
            models.RedirectFlow.fetch(redirectflow)
            self.assertModelEqual(redirectflow, mocked_info)

            # Deleting any of the links should result in them being None
            mocked_info['links'] = links
            mock_redirect.return_value = resources.RedirectFlow(
                mocked_info,
                None
            )
            models.RedirectFlow.fetch(redirectflow)
            self.assertModelEqual(redirectflow, mocked_info)

            # Deleting any of the relations should result in the RedirectFlow being deleted
            rel_model = models.RedirectFlow._meta.get_field(field).rel.to
            rel_instance = rel_model.objects.get(
                id=identifier
            )
            rel_instance.delete()

            self.assertRaises(
                models.RedirectFlow.DoesNotExist,
                models.RedirectFlow.objects.get,
                id=mocked_info['id']
            )

    @mock.patch('gocardless_pro.services.PayoutsService.get')
    def test_payout_fetch(self, mock_get):
        mocked_info = {
            'id': 'PO123',
            'amount': 13.37,
            'created_at': '2015-12-30T23:59:59.999Z',
            'currency': CURRENCIES[0][0],
            'reference': 'A Star Wars reference?',
            'status': PAYOUT_STATUSES[0][0],
        }

        mock_get.return_value = resources.Payout(
            mocked_info,
            None
        )

        payout = models.Payout.objects.create(
            id=mocked_info['id'],
        )

        models.Payout.fetch(payout)
        self.assertModelEqual(payout, mocked_info)

        # Deleting the reference should set it to '' in the database
        del mocked_info['reference']

        mock_get.return_value = resources.Payout(
            mocked_info,
            None
        )

        models.Payout.fetch(payout)
        self.assertModelEqual(payout, mocked_info)

        payout.delete()

    @mock.patch('gocardless_pro.services.CustomerBankAccountsService.get')
    @mock.patch('gocardless_pro.services.CustomersService.get')
    @mock.patch('gocardless_pro.services.MandatesService.get')
    @mock.patch('gocardless_pro.services.SubscriptionsService.create')
    def test_subscription_create(self, mock_subscription, mock_mandate,
                                 mock_customer, mock_bank):
        mocked_info = copy.deepcopy(self.SUBSCRIPTION_INFO)

        given = copy.deepcopy(mocked_info)
        del given['id']
        del given['created_at']
        del given['status']
        del given['metadata']  # Temporary
        del given['upcoming_payments']

        mock_subscription.return_value = resources.Subscription(
            mocked_info,
            None
        )
        mock_mandate.return_value = resources.Mandate(
            self.MANDATE_INFO,
            None
        )
        mock_customer.return_value = resources.Customer(
            self.CUSTOMER_INFO,
            None
        )
        mock_bank.return_value = resources.CustomerBankAccount(
            self.CUSTOMER_BANK_ACCOUNT_INFO,
            None
        )

        subscription = models.Subscription.create(given)
        self.assertModelEqual(subscription, mocked_info)

        # Deleting the customer should delete the customer's bank account
        models.Mandate.objects.filter(
            id=mocked_info['links']['mandate']
        ).delete()

        self.assertRaises(
            models.Subscription.DoesNotExist,
            models.Subscription.objects.get,
            id=mocked_info['id']
        )

        # Deleting the mandate link should give an error
        del given['links']

        mock_subscription.return_value = resources.Subscription(
            mocked_info,
            None
        )

        self.assertRaises(
            ValueError,
            models.Subscription.create,
            given
        )

        subscription.delete()

    @mock.patch('gocardless_pro.services.CustomerBankAccountsService.get')
    @mock.patch('gocardless_pro.services.CustomersService.get')
    @mock.patch('gocardless_pro.services.MandatesService.get')
    @mock.patch('gocardless_pro.services.SubscriptionsService.get')
    @mock.patch('gocardless_pro.services.PaymentsService.create')
    def test_payment_create(self, mock_payment, mock_subscription, mock_mandate,
                            mock_customer, mock_bank):
        mocked_info = {
            'id': 'PM123',
            'created_at': '2014-05-08T17:01:06.000Z',
            'charge_date': '2014-05-21',
            'amount': 100,
            'description': None,
            'currency': 'GBP',
            'status': 'pending_submission',
            'reference': 'WINEBOX001',
            'metadata': {
                'order_dispatch_date': '2014-05-22',
            },
            'amount_refunded': 0,
            'links': {
                'mandate': self.MANDATE_INFO['id'],
                'subscription': self.SUBSCRIPTION_INFO['id'],
            },
        }

        given = copy.deepcopy(mocked_info)
        del given['id']
        del given['created_at']
        del given['status']
        del given['metadata']
        del given['amount_refunded']

        mock_payment.return_value = resources.Payment(
            mocked_info,
            None
        )
        mock_subscription.return_value = resources.Subscription(
            self.SUBSCRIPTION_INFO,
            None
        )
        mock_mandate.return_value = resources.Mandate(
            self.MANDATE_INFO,
            None
        )
        mock_customer.return_value = resources.Customer(
            self.CUSTOMER_INFO,
            None
        )
        mock_bank.return_value = resources.CustomerBankAccount(
            self.CUSTOMER_BANK_ACCOUNT_INFO,
            None
        )

        payment = models.Payment.create(given)
        self.assertModelEqual(payment, mocked_info)

        # Deleting the subscription should delete the payment
        models.Subscription.objects.filter(
            id=mocked_info['links']['subscription']
        ).delete()

        self.assertRaises(
            models.Payment.DoesNotExist,
            models.Payment.objects.get,
            id=mocked_info['id']
        )

        payment = models.Payment.create(given)
        self.assertModelEqual(payment, mocked_info)

        # Deleting the mandate should delete the payment
        models.Mandate.objects.filter(
            id=mocked_info['links']['mandate']
        ).delete()

        self.assertRaises(
            models.Payment.DoesNotExist,
            models.Payment.objects.get,
            id=mocked_info['id']
        )

        # Deleting the subscription link should set the relation to None
        del mocked_info['links']['subscription']
        del given['links']['subscription']

        mock_payment.return_value = resources.Payment(
            mocked_info,
            None
        )
        payment = models.Payment.create(given)
        self.assertModelEqual(payment, mocked_info)
