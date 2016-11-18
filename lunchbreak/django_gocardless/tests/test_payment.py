import copy

import mock
from gocardless_pro import resources

from . import GCTestCase
from .. import models


class PaymentTestCase(GCTestCase):

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
