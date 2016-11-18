import copy

import mock
from gocardless_pro import resources

from . import GCTestCase
from .. import models


class RedirectFlowTestCase(GCTestCase):

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
