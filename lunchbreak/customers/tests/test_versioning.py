from datetime import time

from django.core.urlresolvers import reverse
from lunch.models import Food

from . import CustomersTestCase
from ..views import FoodViewSet, StoreFoodViewSet, StoreViewSet


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
            time(hour=23, minute=59, second=59),
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
                time(hour=23, minute=59, second=59),
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

    def request_food(self, **kwargs):
        url_kwargs = {
            'pk': self.food.pk
        }
        url = reverse(
            'customers:food-detail',
            kwargs=url_kwargs,
        )
        request = self.factory.get(
            url,
            **kwargs
        )
        response = self.authenticate_request(
            request,
            FoodViewSet,
            view_actions={
                'get': 'retrieve'
            },
            **url_kwargs
        )
        response.render()
        return response

    def request_foods(self, **kwargs):
        url_kwargs = {
            'parent_lookup_pk': self.store.pk
        }
        url = reverse(
            'customers:store-food-list',
            kwargs=url_kwargs,
        )
        request = self.factory.get(
            url,
            **kwargs
        )
        response = self.authenticate_request(
            request,
            StoreFoodViewSet,
            view_actions={
                'get': 'list'
            },
            **url_kwargs
        )
        response.render()
        return response

    def test_preorder_food(self):
        self.food.preorder_days = None
        self.food.save()

        response = self.request_food(HTTP_X_VERSION='2.2.2')

        self.assertEqual(
            response.data['preorder_days'],
            self.food.preorder_days,
        )

        # Food.preorder_days = None
        # Food.foodtype.preorder_days = None
        # Should return preorder_days = 0

        self.food.foodtype.preorder_days = None
        self.food.foodtype.save()

        response = self.request_food(HTTP_X_VERSION='2.2.1')
        self.assertEqual(
            response.data['preorder_days'],
            0,
        )

        # Food.preorder_days = None
        # Food.foodtype.preorder_days = 1
        # Should return preorder_days = Food.foodtype.preorder_days + 1

        self.food.foodtype.preorder_days = 1
        self.food.foodtype.save()

        response = self.request_food(HTTP_X_VERSION='2.2.1')
        self.assertEqual(
            response.data['preorder_days'],
            self.food.foodtype.preorder_days + 1,
        )

        # Food.preorder_days = 1
        # Food.foodtype.preorder_days = 1
        # Should return preorder_days = Food.preorder_days + 1

        self.food.preorder_days = 1
        self.food.save()

        response = self.request_food(HTTP_X_VERSION='2.2.1')
        self.assertEqual(
            response.data['preorder_days'],
            self.food.preorder_days + 1,
        )

        # Food.preorder_days = 1
        # Food.foodtype.preorder_days = None
        # Should return preorder_days = Food.preorder_days + 1

        self.food.foodtype.preorder_days = None
        self.food.foodtype.save()

        response = self.request_food(HTTP_X_VERSION='2.2.1')
        self.assertEqual(
            response.data['preorder_days'],
            self.food.preorder_days + 1,
        )

        # Food.preorder_disabled = True
        # Should return preorder_days = 0

        self.food.preorder_disabled = True
        self.food.save()

        response = self.request_food(HTTP_X_VERSION='2.2.1')
        self.assertEqual(
            response.data['preorder_days'],
            0,
        )

    def test_preorder_foods(self):
        # Only 2 basic tests are done here to test whether the transformation was applied.
        # See test_preorder_food for all tests.

        response = self.request_foods(HTTP_X_VERSION='2.2.1')

        self.assertNotEqual(
            len(response.data),
            0
        )

        for item in response.data:
            food = Food.objects.get(id=item['id'])
            self.assertNotEqual(
                item['preorder_days'],
                food.preorder_days,
            )

        response = self.request_foods(HTTP_X_VERSION='2.2.2')

        self.assertNotEqual(
            len(response.data),
            0
        )

        for item in response.data:
            food = Food.objects.get(id=item['id'])
            self.assertEqual(
                item['preorder_days'],
                food.preorder_days,
            )
