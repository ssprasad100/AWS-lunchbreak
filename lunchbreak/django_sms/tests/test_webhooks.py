import uuid
from urllib.parse import urlencode

from django.core.urlresolvers import reverse
from django.http import Http404
from mock import patch
from rest_framework import status

from ..models import Message, Phone
from ..utils import validate_plivo_signature
from ..views import PlivoWebhookView
from .testcase import DjangoSmsTestCase


class WebhookTestCase(DjangoSmsTestCase):

    PLIVO_ID = str(uuid.uuid4())
    TWILIO_ID = 'MM' + str(uuid.uuid4())

    PLIVO_WEBHOOK_URL = 'http://api.andreas.cloock.be/payconiq'
    PLIVO_AUTH_TOKEN = 'OlASOlJpJXjn9cPfv8PKfZBJDnbZDkceO6hgtoCU'

    MESSAGE_UUID = '82ab9178-41e2-457c-929f-5d818ee8adbd'
    DELIVERED_PLIVO_SIGNATURE = 'AhvqztmG0A8GSdXfthx46SQcXzA='
    DELIVERED_PLIVO_POST = {
        'PartInfo': '1 of 1',
        'TotalRate': '0.05733',
        'ParentMessageUUID': MESSAGE_UUID,
        'ErrorCode': '',
        'Units': '1',
        'Status': 'delivered',
        'To': '32472907605',
        'From': '32466900406',
        'MNC': '001',
        'MCC': '206',
        'TotalAmount': '0.05733',
        'MessageUUID': MESSAGE_UUID
    }
    REJECTED_PLIVO_SIGNATURE = 'AhvqztmG0A8GSdXfthx46SQcXzA='
    REJECTED_PLIVO_POST = {
        'PartInfo': '1 of 1',
        'TotalRate': '0.05733',
        'ParentMessageUUID': MESSAGE_UUID,
        'ErrorCode': '',
        'Units': '1',
        'Status': 'rejected',
        'To': '32472907605',
        'From': '32466900406',
        'MNC': '001',
        'MCC': '206',
        'TotalAmount': '0.05733',
        'MessageUUID': MESSAGE_UUID
    }

    NOTFOUND_MESSAGE_UID = '12ab9178-41e2-457c-929f-5d818ee8adbd'
    NOTFOUND_PLIVO_POST = {
        'PartInfo': '1 of 1',
        'TotalRate': '0.05733',
        'ParentMessageUUID': NOTFOUND_MESSAGE_UID,
        'ErrorCode': '',
        'Units': '1',
        'Status': 'rejected',
        'To': '32472907605',
        'From': '32466900406',
        'MNC': '001',
        'MCC': '206',
        'TotalAmount': '0.05733',
        'MessageUUID': NOTFOUND_MESSAGE_UID
    }

    def setUp(self):
        super().setUp()
        self.phone = Phone.objects.create(
            phone=self.PHONE
        )
        self.message = Message.objects.create(
            phone=self.phone,
            remote_uuid=self.MESSAGE_UUID,
        )

    def test_plivo_signature_success(self):
        self.assertTrue(
            validate_plivo_signature(
                signature=self.DELIVERED_PLIVO_SIGNATURE,
                post_params=self.DELIVERED_PLIVO_POST,
                webhook_url=self.PLIVO_WEBHOOK_URL,
                auth_token=self.PLIVO_AUTH_TOKEN
            )
        )

    def test_plivo_signature_failure(self):
        self.assertFalse(
            validate_plivo_signature(
                signature=self.DELIVERED_PLIVO_SIGNATURE,
                post_params=self.REJECTED_PLIVO_POST,
                webhook_url=self.PLIVO_WEBHOOK_URL,
                auth_token=self.PLIVO_AUTH_TOKEN
            )
        )

    @patch('django_sms.models.Message.retry')
    @patch('django_sms.views.PlivoWebhookView.is_valid')
    def test_plivo_webhook_delivered(self, mock_valid, mock_retry):
        """Successful webhooks should not try to send the message again."""

        mock_valid.return_value = True

        self.message.gateway = Message.PLIVO
        self.message.save()

        request = self.factory.post(
            reverse('django_sms:plivo'),
            data=urlencode(self.DELIVERED_PLIVO_POST),
            content_type='application/x-www-form-urlencoded'
        )
        response = self.as_view(request, PlivoWebhookView)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertFalse(
            mock_retry.called
        )

    @patch('django_sms.models.Message.retry')
    @patch('django_sms.views.PlivoWebhookView.is_valid')
    def test_plivo_webhook_rejected(self, mock_valid, mock_retry):
        """Failed webhooks should try to send the message again."""

        mock_valid.return_value = True

        self.message.gateway = Message.PLIVO
        self.message.save()

        request = self.factory.post(
            reverse('django_sms:plivo'),
            data=urlencode(self.REJECTED_PLIVO_POST),
            content_type='application/x-www-form-urlencoded'
        )
        response = self.as_view(request, PlivoWebhookView)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertTrue(
            mock_retry.called
        )

    @patch('django_sms.views.PlivoWebhookView.is_valid')
    def test_plivo_webhook_notfound(self, mock_valid):
        """Messages that aren't found, should return a 404."""

        mock_valid.return_value = True

        request = self.factory.post(
            reverse('django_sms:plivo'),
            data=urlencode(self.NOTFOUND_PLIVO_POST),
            content_type='application/x-www-form-urlencoded'
        )
        self.assertRaises(
            Http404,
            self.as_view,
            request,
            PlivoWebhookView
        )

    @patch('django_sms.views.PlivoWebhookView.is_valid')
    def test_plivo_webhook_malformed(self, mock_valid):
        """Messages that aren't found, should return a 404."""

        mock_valid.return_value = True

        request = self.factory.post(
            reverse('django_sms:plivo')
        )
        response = self.as_view(request, PlivoWebhookView)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
