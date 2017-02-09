from datetime import timedelta

import mock
from customers.config import ORDER_STATUS_COMPLETED
from customers.models import Order, OrderedFood
from django.core.urlresolvers import reverse
from django.utils import timezone
from lunch.models import Food
from rest_framework import status

from .. import views
from .testcase import BusinessTestCase


class StagedDeleteTestCase(BusinessTestCase):

    @mock.patch('customers.models.User.notify')
    def test_food_delete(self, mock_notify):
        orderedfood = OrderedFood(
            cost=1,
            original=self.food,
            is_original=True
        )

        order = Order.objects.create_with_orderedfood(
            user=self.user,
            store=self.store,
            receipt=timezone.now() + timedelta(days=1),
            orderedfood=[orderedfood]
        )

        url_kwargs = {
            'pk': self.food.pk
        }
        url = reverse(
            'business-food-delete',
            kwargs=url_kwargs
        )

        # Trying to delete it while there still is a depending OrderedFood
        # should return 200
        request = self.factory.delete(url)
        response = self.authenticate_request(
            request,
            views.FoodViewSet,
            user=self.owner,
            view_actions={
                'delete': 'delete'
            },
            **url_kwargs
        )

        self.assertFalse(Food.objects.filter(pk=self.food.pk).exists())
        self.assertTrue(Food.objects.all_with_deleted().filter(pk=self.food.pk).exists())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Because the food is now marked to be deleted
        # Updating the order status should delete it
        order.status = ORDER_STATUS_COMPLETED
        order.save()

        request = self.factory.delete(url)

        response = self.authenticate_request(
            request,
            views.FoodViewSet,
            user=self.owner,
            view_actions={
                'delete': 'delete'
            },
            **url_kwargs
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
        self.assertRaises(
            Food.DoesNotExist,
            Food.objects.get,
            pk=self.food.pk
        )

        # If the food is not yet marked as deleted, but has no
        # unfinished orders, a 204 should be returned.
        url_kwargs['pk'] = self.other_food.pk
        orderedfood.original = self.other_food
        orderedfood.save()

        request = self.factory.delete(url)
        response = self.authenticate_request(
            request,
            views.FoodViewSet,
            user=self.owner,
            view_actions={
                'delete': 'delete'
            },
            **url_kwargs
        )

        self.assertFalse(Food.objects.filter(pk=self.food.pk).exists())
        self.assertFalse(Food.objects.all_with_deleted().filter(pk=self.food.pk).exists())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
