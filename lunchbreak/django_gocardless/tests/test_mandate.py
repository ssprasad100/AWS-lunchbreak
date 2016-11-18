import copy

import mock
from gocardless_pro import resources

from . import GCTestCase
from .. import models


class MandateTestCase(GCTestCase):

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
