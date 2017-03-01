from django.core.urlresolvers import reverse
from rest_framework import status

from ..models import StaffToken
from ..views import StaffDetailView, StaffView
from .testcase import BusinessTestCase


class StaffTestCase(BusinessTestCase):

    def test_unicode_login(self):
        password = 'password'
        self.staff.set_password(password)
        self.staff.save()

        url = reverse('business:staff-list')
        request = self.factory.post(url, {
            'device': 'App’s NM iPad',  # Contains UTF-8 special quote
            'service': 1,
            'password': password,
            'staff': self.staff.pk
        })
        response = self.as_view(
            view=StaffView,
            request=request
        )
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
        self.assertEqual(
            staff_token.device,
            'Apps NM iPad'
        )
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
