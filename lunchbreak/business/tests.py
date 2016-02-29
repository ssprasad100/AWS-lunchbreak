# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from customers.config import ORDER_STATUS_COMPLETED
from customers.models import Order, OrderedFood, User, UserToken
from django.core.urlresolvers import reverse
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

    def setUp(self):
        super(BusinessTests, self).setUp()
        self.factory = APIRequestFactory()

        self.user = User.objects.create(
            phone=BusinessTests.PHONE_USER,
            name=BusinessTests.NAME_USER
        )

        self.userToken = UserToken.objects.create(
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

        self.foodType = FoodType.objects.create(
            name='FoodType test'
        )

        self.foodCategory = FoodCategory.objects.create(
            name='FoodCategory test',
            store=self.store
        )

        self.ingredientGroup = IngredientGroup.objects.create(
            name='IngredientGroup test',
            foodType=self.foodType,
            store=self.store
        )

        self.food = Food.objects.create(
            name='Food test',
            cost=1.00,
            foodType=self.foodType,
            category=self.foodCategory,
            store=self.store
        )

        IngredientRelation.objects.bulk_create([
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 1',
                    group=self.ingredientGroup,
                    store=self.store
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 2',
                    group=self.ingredientGroup,
                    store=self.store
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 3',
                    group=self.ingredientGroup,
                    store=self.store
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 4',
                    group=self.ingredientGroup,
                    store=self.store
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 5',
                    group=self.ingredientGroup,
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

    def testDeleteFood(self):
        food = Food.objects.get(id=self.food.id)
        food.pk = None
        food.save()

        order = Order.objects.create(
            user=self.user,
            store=self.store,
            pickup=timezone.now() + timedelta(days=1)
        )

        orderedFood = OrderedFood.objects.create(
            cost=1,
            order=order,
            original=food,
            useOriginal=True
        )

        duplicateFood = Food.objects.get(id=self.food.id)
        duplicateFood.pk = None
        duplicateFood.save()

        urlKwargs = {
            'pk': food.id
        }
        url = reverse(
            'business-food-single',
            kwargs=urlKwargs
        )

        # Trying to delete it while there still is a depending OrderedFood
        # should return 200
        request = self.factory.delete(url, format=BusinessTests.FORMAT)
        response = self.authenticateRequest(
            request,
            views.FoodSingleView,
            user=self.owner,
            **urlKwargs
        )

        try:
            Food.objects.get(id=food.id)
        except:
            self.fail('Food got deleted when there still was an incomplete OrderedFood.')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Because the food is now marked to be deleted
        # Updating the order status should delete it
        order.status = ORDER_STATUS_COMPLETED
        order.save()

        request = self.factory.delete(url, format=BusinessTests.FORMAT)
        response = self.authenticateRequest(
            request,
            views.FoodSingleView,
            user=self.owner,
            **urlKwargs
        )

        self.assertRaises(Food.DoesNotExist, Food.objects.get, id=food.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # If the food is not yet marked as deleted, but has no
        # unfinished orders, a 204 should be returned.
        urlKwargs['pk'] = duplicateFood.id
        orderedFood.original = duplicateFood
        orderedFood.save()

        request = self.factory.delete(url, format=BusinessTests.FORMAT)
        response = self.authenticateRequest(
            request,
            views.FoodSingleView,
            user=self.owner,
            **urlKwargs
        )

        self.assertRaises(Food.DoesNotExist, Food.objects.get, id=food.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
