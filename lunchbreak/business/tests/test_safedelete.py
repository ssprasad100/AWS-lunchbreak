from datetime import timedelta

import mock
from customers.config import ORDER_STATUS_COMPLETED
from customers.models import Order
from django.core.urlresolvers import reverse
from django.utils import timezone
from lunch.models import Food, Ingredient, Menu
from rest_framework import status

from .. import views
from .testcase import BusinessTestCase


class SafeDeleteTestCase(BusinessTestCase):

    @mock.patch('lunch.managers.FoodManager.closest')
    def setUp(self, mock_closest):
        super().setUp()

        mock_closest.return_value = self.food
        self.orderedfood = {
            'original': self.food,
            'ingredients': [self.deselected_ingredient],
            'total': self.food.cost,
            'amount': 1
        }

        self.order = Order.objects.create_with_orderedfood(
            user=self.user,
            store=self.store,
            receipt=timezone.now() + timedelta(days=1),
            orderedfood=[self.orderedfood]
        )
        self.orderedfood = self.order.orderedfood.all().first()

    @mock.patch('customers.models.User.notify')
    def test_order_completion(self, mock_notify):
        """Test whether completing an order hard deletes the soft deleted related food.

        Food should be deleted if there are no OrderedFood of it with active
        orders. If that still is the case, then stage it for deletion and it
        should be deleted once the order finished.
        """
        # Trying to delete it while there still is a depending OrderedFood
        # should return 200
        response = self.request_food_deletion(pk=self.food.pk)

        self.assertFalse(Food.objects.filter(pk=self.food.pk).exists())
        self.assertTrue(Food.objects.all_with_deleted().filter(pk=self.food.pk).exists())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Because the food is now marked to be deleted
        # Updating the order status should delete it
        self.order.status = ORDER_STATUS_COMPLETED
        self.order.save()

        response = self.request_food_deletion(pk=self.food.pk)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
        self.assertRaises(
            Food.DoesNotExist,
            Food.objects.get,
            pk=self.food.pk
        )
        self.orderedfood.refresh_from_db()
        self.assertIsNone(self.orderedfood.original)

    @mock.patch('customers.models.User.notify')
    def test_food_order_finished(self, mock_notify):
        """Test whether a food without an active order is hard deleted."""
        self.order.status = ORDER_STATUS_COMPLETED
        self.order.save()

        # If the food is not yet marked as deleted, but has no
        # unfinished orders, a 204 should be returned.
        response = self.request_food_deletion(pk=self.food.pk)

        self.assertFalse(Food.objects.filter(pk=self.food.pk).exists())
        self.assertFalse(Food.objects.all_with_deleted().filter(pk=self.food.pk).exists())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.orderedfood.refresh_from_db()
        self.assertIsNone(self.orderedfood.original)

    @mock.patch('customers.models.User.notify')
    def test_food_no_order(self, mock_notify):
        """Test whether a food without an active order is hard deleted."""
        self.order.delete()

        # If the food is not yet marked as deleted, but has no
        # unfinished orders, a 204 should be returned.
        response = self.request_food_deletion(pk=self.food.pk)

        self.assertFalse(Food.objects.filter(pk=self.food.pk).exists())
        self.assertFalse(Food.objects.all_with_deleted().filter(pk=self.food.pk).exists())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @mock.patch('customers.models.User.notify')
    def test_menu_completion(self, mock_notify):
        # Trying to delete it while there still is a depending OrderedFood
        # should return 200
        response = self.request_menu_deletion(pk=self.menu.pk)

        self.assertFalse(Menu.objects.filter(pk=self.menu.pk).exists())
        self.assertTrue(Menu.objects.all_with_deleted().filter(pk=self.menu.pk).exists())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Because the menu is now marked to be deleted
        # Updating the order status should delete it
        self.order.status = ORDER_STATUS_COMPLETED
        self.order.save()

        response = self.request_menu_deletion(pk=self.menu.pk)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
        self.assertRaises(
            Menu.DoesNotExist,
            Menu.objects.get,
            pk=self.menu.pk
        )
        self.orderedfood.refresh_from_db()
        self.assertIsNone(self.orderedfood.original)

    @mock.patch('customers.models.User.notify')
    def test_menu_order_finished(self, mock_notify):
        """Test whether a food without an active order is hard deleted."""
        self.order.status = ORDER_STATUS_COMPLETED
        self.order.save()

        # If the food is not yet marked as deleted, but has no
        # unfinished orders, a 204 should be returned.
        response = self.request_menu_deletion(pk=self.menu.pk)

        self.assertFalse(Menu.objects.filter(pk=self.menu.pk).exists())
        self.assertFalse(Menu.objects.all_with_deleted().filter(pk=self.menu.pk).exists())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.orderedfood.refresh_from_db()
        self.assertIsNone(self.orderedfood.original)

    @mock.patch('customers.models.User.notify')
    def test_menu_no_order(self, mock_notify):
        """Test whether a food without an active order is hard deleted."""
        self.order.delete()

        # If the food is not yet marked as deleted, but has no
        # unfinished orders, a 204 should be returned.
        response = self.request_menu_deletion(pk=self.menu.pk)

        self.assertFalse(Menu.objects.filter(pk=self.menu.pk).exists())
        self.assertFalse(Menu.objects.all_with_deleted().filter(pk=self.menu.pk).exists())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @mock.patch('customers.models.User.notify')
    def test_ingredient_completion(self, mock_notify):
        # Trying to delete it while there still is a depending OrderedFood
        # should return 200
        response = self.request_ingredient_deletion(pk=self.deselected_ingredient.pk)

        self.assertFalse(
            Ingredient.objects.filter(
                pk=self.deselected_ingredient.pk
            ).exists()
        )
        self.assertTrue(
            Ingredient.objects.all_with_deleted().filter(
                pk=self.deselected_ingredient.pk
            ).exists()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Because the menu is now marked to be deleted
        # Updating the order status should delete it
        self.order.status = ORDER_STATUS_COMPLETED
        self.order.save()

        response = self.request_ingredient_deletion(pk=self.deselected_ingredient.pk)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
        self.assertRaises(
            Ingredient.DoesNotExist,
            Ingredient.objects.get,
            pk=self.deselected_ingredient.pk
        )
        self.orderedfood.refresh_from_db()
        self.assertFalse(self.orderedfood.ingredients.filter(
            pk__in=[self.deselected_ingredient.pk]
        ).exists())

    @mock.patch('customers.models.User.notify')
    def test_ingredient_order_finished(self, mock_notify):
        """Test whether a food without an active order is hard deleted."""
        self.order.status = ORDER_STATUS_COMPLETED
        self.order.save()

        # If the food is not yet marked as deleted, but has no
        # unfinished orders, a 204 should be returned.
        response = self.request_ingredient_deletion(pk=self.deselected_ingredient.pk)

        self.assertFalse(Ingredient.objects.filter(pk=self.deselected_ingredient.pk).exists())
        self.assertFalse(Ingredient.objects.all_with_deleted().filter(
            pk=self.deselected_ingredient.pk).exists())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.orderedfood.refresh_from_db()
        self.assertFalse(self.orderedfood.ingredients.filter(
            pk__in=[self.deselected_ingredient.pk]
        ).exists())

    @mock.patch('customers.models.User.notify')
    def test_ingredient_no_order(self, mock_notify):
        """Test whether a food without an active order is hard deleted."""
        self.order.delete()

        # If the food is not yet marked as deleted, but has no
        # unfinished orders, a 204 should be returned.
        response = self.request_ingredient_deletion(pk=self.deselected_ingredient.pk)

        self.assertFalse(Ingredient.objects.filter(pk=self.deselected_ingredient.pk).exists())
        self.assertFalse(Ingredient.objects.all_with_deleted().filter(
            pk=self.deselected_ingredient.pk).exists())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def request_deletion(self, pk, url_name, viewset, user=None):
        """Request deletion for a specific model and viewset."""
        if user is None:
            user = self.owner

        url_kwargs = {
            'pk': pk
        }
        url = reverse(
            url_name,
            kwargs=url_kwargs
        )
        request = self.factory.delete(url)
        return self.authenticate_request(
            request,
            viewset,
            user=user,
            view_actions={
                'delete': 'destroy'
            },
            **url_kwargs
        )

    def request_food_deletion(self, pk, **kwargs):
        """Make a request for food deletion."""
        return self.request_deletion(
            pk=pk,
            url_name='business:food-detail',
            viewset=views.FoodViewSet,
            **kwargs
        )

    def request_menu_deletion(self, pk, **kwargs):
        """Make a request for menu deletion."""
        return self.request_deletion(
            pk=pk,
            url_name='business:menu-detail',
            viewset=views.MenuViewSet,
            **kwargs
        )

    def request_ingredient_deletion(self, pk, **kwargs):
        """Make a request for ingredient deletion."""
        return self.request_deletion(
            pk=pk,
            url_name='business:ingredient-detail',
            viewset=views.IngredientViewSet,
            **kwargs
        )
