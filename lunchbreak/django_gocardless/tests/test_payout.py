import mock
from gocardless_pro import resources

from . import GCTestCase
from .. import models
from ..config import CURRENCIES, PAYOUT_STATUSES


class PayoutTestCase(GCTestCase):

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
