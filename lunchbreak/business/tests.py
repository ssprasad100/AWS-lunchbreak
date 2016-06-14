from datetime import timedelta

import mock
from customers.config import ORDER_STATUS_COMPLETED
from customers.models import Order, OrderedFood, User, UserToken
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils import timezone
from lunch.models import (Food, FoodCategory, FoodType, HolidayPeriod,
                          Ingredient, IngredientGroup, IngredientRelation,
                          Store)
from Lunchbreak.test import LunchbreakTestCase
from push_notifications.models import SERVICE_APNS
from rest_framework import status
from rest_framework.test import APIRequestFactory

from . import views
from .models import Employee, Staff


class BusinessTests(LunchbreakTestCase):

    PHONE_USER = '+32472907604'
    NAME_USER = 'Meneer Aardappel'
    FORMAT = 'json'
    VALID_PHONE = '+32472907605'
    VALID_PHONE2 = '+32472907606'
    INVALID_PHONE = '+123456789'
    PIN = '123456'
    NAME = 'Meneer De Bolle'
    NAME_ALTERNATE = 'Mevrouw De Bolle'
    DEVICE = 'Test device'
    REGISTRATION_ID = '123456789'
    EMAIL = 'hello@cloock.be'

    @mock.patch('googlemaps.Client.geocode')
    def setUp(self, mock_geocode):
        super(BusinessTests, self).setUp()
        self.factory = APIRequestFactory()

        self.mock_geocode_results(
            mock_geocode,
            lat=51.0111595,
            lng=3.9075993
        )

        self.user = User.objects.create(
            phone=BusinessTests.PHONE_USER,
            name=BusinessTests.NAME_USER
        )

        self.usertoken = UserToken.objects.create(
            identifier='something',
            device='something',
            user=self.user,
            registration_id='something',
            service=SERVICE_APNS
        )

        self.store = Store.objects.create(
            name='BusinessTests',
            country='België',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        self.staff = Staff.objects.create(
            store=self.store,
            email=self.EMAIL
        )

        self.owner = Employee.objects.create(
            name=BusinessTests.NAME_USER,
            staff=self.staff,
            owner=True
        )

        self.foodtype = FoodType.objects.create(
            name='FoodType test'
        )

        self.foodcategory = FoodCategory.objects.create(
            name='FoodCategory test',
            store=self.store
        )

        self.ingredientgroup = IngredientGroup.objects.create(
            name='IngredientGroup test',
            foodtype=self.foodtype,
            store=self.store
        )

        self.food = Food.objects.create(
            name='Food test',
            cost=1.00,
            foodtype=self.foodtype,
            category=self.foodcategory,
            store=self.store
        )

        IngredientRelation.objects.bulk_create([
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 1',
                    group=self.ingredientgroup,
                    store=self.store
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 2',
                    group=self.ingredientgroup,
                    store=self.store
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 3',
                    group=self.ingredientgroup,
                    store=self.store
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 4',
                    group=self.ingredientgroup,
                    store=self.store
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 5',
                    group=self.ingredientgroup,
                    store=self.store
                ),
                food=self.food
            )
        ])

        HolidayPeriod.objects.bulk_create([
            HolidayPeriod(
                store=self.store,
                start=timezone.now() - timedelta(days=10),
                end=timezone.now() + timedelta(days=10),
                closed=False
            )
        ])

    def test_food_delete(self):
        food = Food.objects.get(id=self.food.id)
        food.pk = None
        food.save()

        orderedfood = OrderedFood(
            cost=1,
            original=food,
            is_original=True
        )

        order = Order.create(
            user=self.user,
            store=self.store,
            pickup=timezone.now() + timedelta(days=1),
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
