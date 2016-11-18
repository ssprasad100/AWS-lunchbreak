import copy

import mock
from gocardless_pro import resources

from . import GCTestCase
from .. import models


class CustomerTestCase(GCTestCase):

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
