from ..utils import generate_web_signature
from .testcase import PayconiqTestCase


class WebSignatureTestCase(PayconiqTestCase):

    VALID_SIGNATURE = 'L0L9cCuCnqmiozZzsoUZ/xcG3roHTZIBffpkqpxuYtE='
    MERCHANT_ID = '58daaee3166e662eb1aa0de9'
    WEBHOOK_ID = 'something'
    CURRENCY = 'EUR'
    AMOUNT = 100
    WIDGET_TOKEN = '1c4ce050-89f0-48ed-a0c4-b684c6462866'

    def test_valid(self):
        self.assertEqual(
            generate_web_signature(
                merchant_id=self.MERCHANT_ID,
                webhook_id=self.WEBHOOK_ID,
                currency=self.CURRENCY,
                amount=self.AMOUNT,
                widget_token=self.WIDGET_TOKEN
            ),
            'L0L9cCuCnqmiozZzsoUZ/xcG3roHTZIBffpkqpxuYtE='
        )
