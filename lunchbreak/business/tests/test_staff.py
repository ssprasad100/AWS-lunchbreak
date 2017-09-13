from unittest.mock import patch

from django.core.urlresolvers import reverse
from rest_framework import status

from ..authentication import StaffAuthentication
from ..models import Staff, StaffToken
from ..serializers import StaffPasswordSerializer
from ..views import (PasswordResetView, ResetRequestView, StaffDetailView,
                     StaffView)
from .testcase import BusinessTestCase


class StaffTestCase(BusinessTestCase):

    def login(self, email=None):
        url = reverse('business:staff-list')
        request = self.factory.post(url, {
            'device': 'Ä',  # Contains UTF-8 special character
            'service': 1,
            'password': self.PASSWORD,
            'email': self.staff.email if email is None else self.staff.email
        })
        return self.as_view(
            view=StaffView,
            request=request
        )

    def test_unicode_login(self):
        response = self.login()
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        staff_token = StaffToken.objects.get(id=response.data['id'])
        equal_fields = ['registration_id', 'service', 'active', 'id']
        for field in equal_fields:
            self.assertEqual(
                getattr(staff_token, field),
                response.data[field]
            )
        self.assertEqual(
            staff_token.staff_id,
            response.data['staff']
        )
        # UTF-8 characters should be stripped
        self.assertTrue(len(staff_token.device) > 0)
        self.assertTrue(
            staff_token.check_identifier(response.data['identifier'])
        )

        kwargs = {
            'pk': self.staff.pk
        }
        url = reverse(
            'business:staff-detail',
            kwargs=kwargs
        )
        request = self.factory.get(url)
        response = self.authenticate_request(
            request,
            StaffDetailView,
            user=self.staff,
            token=staff_token,
            **kwargs
        )
        self.staff.refresh_from_db()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            self.staff.id,
            response.data['id']
        )
        self.assertEqual(
            self.staff.store_id,
            response.data['store']['id']
        )

    @patch('business.models.Staff.clean_email')
    def test_lowercase_login(self, mock_clean):
        uppercase_email = 'UPPERCASE@domain.com'
        self.staff.email = uppercase_email
        self.staff.save()

        self.assertEqual(
            self.staff.email,
            uppercase_email
        )

        response = self.login(email=uppercase_email)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        response = self.login(email=uppercase_email.lower())
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_lowercase_clean(self):
        uppercase_email = 'UPPERCASE@domain.com'
        self.staff.email = uppercase_email
        self.staff.save()

        self.assertEqual(
            self.staff.email,
            uppercase_email.lower()
        )

    def request_password_reset(self, email=None):
        url = reverse('business:staff-password-reset-request')
        request = self.factory.post(url, {
            'email': self.staff.email if email is None else self.staff.email
        })
        return self.as_view(
            view=ResetRequestView,
            request=request,
            authentication=StaffAuthentication
        )

    @patch('django.core.mail.EmailMultiAlternatives.send')
    @patch('business.models.Staff.clean_email')
    def test_lowercase_request_password_reset(self, mock_clean, mock_send):
        uppercase_email = 'UPPERCASE@domain.com'
        self.staff.email = uppercase_email
        self.staff.save()

        self.assertEqual(
            self.staff.email,
            uppercase_email
        )

        response = self.request_password_reset(email=uppercase_email)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            mock_send.call_count,
            1
        )

        response = self.request_password_reset(email=uppercase_email.lower())
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            mock_send.call_count,
            2
        )

    def password_reset(self, **kwargs):
        url = reverse('business:staff-password-reset')
        request = self.factory.post(url, kwargs)
        return self.as_view(
            view=PasswordResetView,
            request=request,
            model=Staff,
            token_model=StaffToken,
            serializer_class=StaffPasswordSerializer
        )

    @patch('business.models.Staff.clean_email')
    def test_lowercase_password_reset(self, mock_clean):
        uppercase_email = 'UPPERCASE@domain.com'
        self.staff.email = uppercase_email
        password_reset = 'reset'
        self.staff.password_reset = password_reset
        self.staff.save()
        other_password = self.PASSWORD + '2'

        self.assertEqual(
            self.staff.email,
            uppercase_email
        )

        response = self.password_reset(
            email=uppercase_email,
            password=other_password,
            password_reset=password_reset
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.staff.refresh_from_db()
        self.assertEqual(
            self.staff.password_reset,
            ''
        )
        self.assertTrue(
            self.staff.check_password(other_password)
        )

        self.staff.password_reset = password_reset
        self.staff.save()

        response = self.password_reset(
            email=uppercase_email,
            password=self.PASSWORD,
            password_reset=password_reset
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.staff.refresh_from_db()
        self.assertEqual(
            self.staff.password_reset,
            ''
        )
        self.assertTrue(
            self.staff.check_password(self.PASSWORD)
        )
