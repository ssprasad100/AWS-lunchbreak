from django.core.urlresolvers import reverse

from . import CustomersTestCase
from ..views import StoreViewSet


class VersioningTestCase(CustomersTestCase):

    def test_hide_cash_disabled_stores(self):
        """Hide stores that do not accept cash payments in versions prior to 2.2.1."""

        self.store.cash_enabled = False
        self.store.save()

        def get_stores(**kwargs):
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

        response = get_stores(HTTP_X_VERSION='2.2.0')
        cash_enabled_stores = len(response.data)
        self.assertEqual(
            cash_enabled_stores,
            2
        )

        response = get_stores(HTTP_X_VERSION='2.2.1')
        all_stores = len(response.data)
        self.assertEqual(
            all_stores,
            3
        )
