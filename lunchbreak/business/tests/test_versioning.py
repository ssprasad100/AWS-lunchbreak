from datetime import time

from django.core.urlresolvers import reverse
from lunch.models import FoodType
from rest_framework import status

from ..views import FoodViewSet, StoreViewSet
from .testcase import BusinessTestCase


class VersioningTestCase(BusinessTestCase):

    def update_preorder_time(self, preorder_time, **kwargs):
        url_kwargs = {
            'pk': self.store.pk
        }
        url = reverse(
            'business:store-detail',
            kwargs=url_kwargs
        )
        request = self.factory.patch(
            url,
            {
                'preorder_time': preorder_time,
            },
            **kwargs
        )
        return self.authenticate_request(
            request=request,
            view=StoreViewSet,
            user=self.owner,
            token=self.ownertoken,
            view_actions={
                'patch': 'update',
            },
            partial=True,
            **url_kwargs
        )

    def test_store_preorder_time(self):
        """Test whether when editing Store.preorder_time changes it for all
        of the FoodTypes."""

        preorder_time = time(hour=23)

        for foodtype in FoodType.objects.filter(store=self.store):
            self.assertNotEqual(
                foodtype.preorder_time,
                preorder_time
            )

        response = self.update_preorder_time(
            preorder_time,
            HTTP_X_VERSION='2.2.1'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        for foodtype in FoodType.objects.filter(store=self.store):
            self.assertEqual(
                foodtype.preorder_time,
                preorder_time
            )

        new_preorder_time = time(hour=22)
        response = self.update_preorder_time(
            new_preorder_time,
            HTTP_X_VERSION='2.2.2'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        for foodtype in FoodType.objects.filter(store=self.store):
            self.assertEqual(
                foodtype.preorder_time,
                preorder_time
            )

    def update_preorder_days(self, preorder_days, **kwargs):
        url_kwargs = {
            'pk': self.food.pk
        }
        url = reverse(
            'business:food-detail',
            kwargs=url_kwargs
        )
        request = self.factory.patch(
            url,
            {
                'preorder_days': preorder_days,
            },
            **kwargs
        )
        return self.authenticate_request(
            request=request,
            view=FoodViewSet,
            user=self.owner,
            token=self.ownertoken,
            view_actions={
                'patch': 'update',
            },
            partial=True,
            **url_kwargs
        )

    def test_food_preorder_days(self):
        """Test whether setting Food.preorder_days to 0 in older API sets it to None."""

        self.food.preorder_days = 100
        self.food.save()

        response = self.update_preorder_days(
            preorder_days=0,
            HTTP_X_VERSION='2.2.1'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.food.refresh_from_db()
        self.assertEqual(
            self.food.preorder_days,
            None
        )

        response = self.update_preorder_days(
            preorder_days=0,
            HTTP_X_VERSION='2.2.2'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.food.refresh_from_db()
        self.assertEqual(
            self.food.preorder_days,
            0
        )
