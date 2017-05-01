import mock
from django.core.urlresolvers import reverse
from django.http import Http404
from rest_framework import status

from ..utils import is_signature_valid
from ..views import WebhookView
from .testcase import PayconiqTestCase


class SignatureTestCase(PayconiqTestCase):

    VALID_SIGNATURE = 'oUO1L7qj3sf9wNRL1cMViqyJ1w1G7Qb+np9pN4seExtIl3Gu9Vnd0nHnAfn3VzBZtVuE08+H92qKgEBPzJyfzItJXK3+IfyNEV87xQLj2kDRX5LJKEuJOlrpYF05ybdjvyk0zN4F7iHR6k5tbrPnDohXf/USYc5F1gBs0xAdBlU7w/CYthifN1cztSHa3HmkyIuoX77HsYjj9DvKKIscOTssHnCFf5+bjNbFpUuVKp5RuL0Ijop3fIMbcEHL2G126ov7usDjLXRJFkIu6gxN/lUQSdDxHwVXL1/9k5Lbl7Mwf49PN410mUmpbGJXlAa+P2NrbI2//7jW6lI0y8Rn/Q=='
    INVALID_SIGNATURE = 'something'
    MERCHANT_ID = '58e39d60100178000b3babb3'
    TIMESTAMP = '2017-04-10T15:03:36.257Z'
    ALGORITHM = 'SHA256WithRSA'
    BODY = '{"_id":"58eb9ead15f970006d509589","status":"SUCCEEDED"}'

    def setUp(self):
        super().setUp()
        merchant = mock.MagicMock()
        merchant.remote_id = self.MERCHANT_ID
        self.transaction = mock.MagicMock()
        self.transaction.merchant = merchant

    def test_valid(self):
        self.assertTrue(
            is_signature_valid(
                signature=self.VALID_SIGNATURE,
                merchant_id=self.MERCHANT_ID,
                timestamp=self.TIMESTAMP,
                algorithm=self.ALGORITHM,
                body=self.BODY
            )
        )

    def test_invalid(self):
        self.assertFalse(
            is_signature_valid(
                signature=self.INVALID_SIGNATURE,
                merchant_id=self.MERCHANT_ID,
                timestamp=self.TIMESTAMP,
                algorithm=self.ALGORITHM,
                body=self.BODY
            )
        )

    @mock.patch('payconiq.views.get_object_or_404')
    @mock.patch('payconiq.models.Transaction.save')
    def test_valid_webhook(self, mock_save, mock_get):
        mock_get.return_value = self.transaction
        request = self.factory.post(
            reverse('payconiq:webhook'),
            data=self.BODY,
            content_type='application/json',
            HTTP_X_SECURITY_SIGNATURE=self.VALID_SIGNATURE,
            HTTP_X_SECURITY_TIMESTAMP=self.TIMESTAMP,
            HTTP_X_SECURITY_KEY='currently ignored',
            HTTP_X_SECURITY_ALGORITHM=self.ALGORITHM
        )
        response = self.as_view(request, WebhookView)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    @mock.patch('payconiq.views.get_object_or_404')
    @mock.patch('payconiq.models.Transaction.save')
    def test_invalid_webhook(self, mock_save, mock_get):
        mock_get.return_value = self.transaction
        request = self.factory.post(
            reverse('payconiq:webhook'),
            data=self.BODY,
            content_type='application/json',
            HTTP_X_SECURITY_SIGNATURE=self.INVALID_SIGNATURE,
            HTTP_X_SECURITY_TIMESTAMP=self.TIMESTAMP,
            HTTP_X_SECURITY_KEY='currently ignored',
            HTTP_X_SECURITY_ALGORITHM=self.ALGORITHM
        )
        self.assertRaises(
            Http404,
            self.as_view,
            request,
            WebhookView
        )

    @mock.patch('payconiq.views.get_object_or_404')
    @mock.patch('payconiq.models.Transaction.save')
    def test_malformed_webhook(self, mock_save, mock_get):
        mock_get.return_value = self.transaction
        request = self.factory.post(
            reverse('payconiq:webhook'),
            data=self.BODY,
            content_type='application/json'
        )
        self.assertRaises(
            Http404,
            self.as_view,
            request,
            WebhookView
        )
