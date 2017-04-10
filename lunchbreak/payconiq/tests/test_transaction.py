import responses
from payconiq import Transaction

from .testcase import PayconiqTestCase


class TransactionTestCase(PayconiqTestCase):

    REMOTE_ID = '5e14137fe51905040b202c04'

    @responses.activate
    def test_resource_start(self):
        responses.add(
            responses.POST,
            Transaction.get_base_url(),
            json={
                'transactionId': self.REMOTE_ID
            },
            status=200
        )

        remote_id = Transaction.start(
            amount=1,
            webhook_url=''
        )
        self.assertEqual(
            remote_id,
            self.REMOTE_ID
        )
