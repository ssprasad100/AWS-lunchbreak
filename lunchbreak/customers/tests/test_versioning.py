from datetime import time

from django.core.urlresolvers import reverse

from . import CustomersTestCase
from ..views import StoreViewSet


class VersioningTestCase(CustomersTestCase):

    def test_hide_cash_disabled_stores(self):
        """Hide stores that do not accept cash payments in versions prior to 2.2.1."""

        self.store.cash_enabled = False
        self.store.save()

        response = self.request_stores(HTTP_X_VERSION='2.2.0')
        cash_enabled_stores = len(response.data)
        self.assertEqual(
            cash_enabled_stores,
            2
        )

        response = self.request_stores(HTTP_X_VERSION='2.2.1')
        all_stores = len(response.data)
        self.assertEqual(
            all_stores,
            3
        )

    def request_stores(self, **kwargs):
        url = reverse('customers:store-list')
        request = self.factory.get(url, **kwargs)
        response = self.authenticate_request(
            request,
            StoreViewSet,
            view_actions={
                'get': 'list'
            }
        )
        response.render()
        return response

    def request_store(self, **kwargs):
        url_kwargs = {
            'pk': self.store.pk
        }
        url = reverse(
            'customers:store-detail',
            kwargs=url_kwargs,
        )
        request = self.factory.get(
            url,
            **kwargs
        )
        response = self.authenticate_request(
            request,
            StoreViewSet,
            view_actions={
                'get': 'retrieve'
            },
            **url_kwargs
        )
        response.render()
        return response

    def test_preorder_store(self):
        response = self.request_store(HTTP_X_VERSION='2.2.1')

        self.assertEqual(
            response.data['preorder_time'],
            time(hour=0, minute=0, second=1),
        )

        response = self.request_store(HTTP_X_VERSION='2.2.2')

        self.assertNotIn(
            'preorder_time',
            response.data
        )

    def test_preorder_stores(self):
        response = self.request_stores(HTTP_X_VERSION='2.2.1')

        self.assertNotEqual(
            len(response.data),
            0
        )

        for store in response.data:
            self.assertEqual(
                store['preorder_time'],
                time(hour=0, minute=0, second=1),
            )

        response = self.request_store(HTTP_X_VERSION='2.2.2')

        self.assertNotEqual(
            len(response.data),
            0
        )
        for store in response.data:
            self.assertNotIn(
                'preorder_time',
                response.data
            )
