import copy

import mock
from gocardless_pro import resources

from . import GCTestCase
from .. import models


class SubscriptionTestCase(GCTestCase):

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
