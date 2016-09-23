from datetime import timedelta

from customers.config import ORDER_STATUS_COMPLETED
from customers.models import Order, OrderedFood
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils import timezone
from lunch.models import Food
from rest_framework import status

from .. import views
from .testcase import BusinessTestCase


class StagedDeleteTestCase(BusinessTestCase):

    def test_food_delete(self):
        food = Food.objects.get(id=self.food.id)
        food.pk = None
        food.save()

        orderedfood = OrderedFood(
            cost=1,
            original=food,
            is_original=True
        )

        order = Order.objects.create_with_orderedfood(
            user=self.user,
            store=self.store,
            receipt=timezone.now() + timedelta(days=1),
            orderedfood=[orderedfood]
        )

        food_duplicate = Food.objects.get(id=self.food.id)
        food_duplicate.pk = None
        food_duplicate.save()

        url_kwargs = {
            'pk': food.id
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

        self.assertTrue(Food.objects.filter(id=food.id).exists())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Because the food is now marked to be deleted
        # Updating the order status should delete it
        order.status = ORDER_STATUS_COMPLETED
        order.save()

        request = self.factory.delete(url)

        self.assertRaises(
            Http404,
            self.authenticate_request,
            request,
            views.FoodViewSet,
            user=self.owner,
            view_actions={
                'delete': 'delete'
            },
            **url_kwargs
        )
        self.assertRaises(Food.DoesNotExist, Food.objects.get, id=food.id)

        # If the food is not yet marked as deleted, but has no
        # unfinished orders, a 204 should be returned.
        url_kwargs['pk'] = food_duplicate.id
        orderedfood.original = food_duplicate
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

        self.assertRaises(Food.DoesNotExist, Food.objects.get, id=food.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
