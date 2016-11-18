import copy

import mock
from gocardless_pro import resources

from . import GCTestCase
from .. import models


class CustomerBankAccountTestCase(GCTestCase):

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
