from datetime import timedelta

import mock
from customers.models import User, UserToken
from django.utils import timezone
from django_sms.models import Phone
from lunch.models import (Food, FoodType, HolidayPeriod, Ingredient,
                          IngredientGroup, IngredientRelation, Menu, Store)
from Lunchbreak.test import LunchbreakTestCase
from push_notifications.models import SERVICE_APNS
from rest_framework.test import APIRequestFactory

from ..models import Employee, Staff


class BusinessTestCase(LunchbreakTestCase):

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
    EMAIL_OTHER = 'other@cloock.be'

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def setUp(self, mock_geocode, mock_timezone):
        super().setUp()
        self.mock_timezone_result(mock_timezone)
        self.factory = APIRequestFactory()

        self.mock_geocode_results(
            mock_geocode,
            lat=51.0111595,
            lng=3.9075993
        )

        self.phone = Phone.objects.create(
            phone=self.PHONE_USER,
            confirmed_at=timezone.now()
        )

        self.user = User.objects.create(
            phone=self.phone,
            name=self.NAME_USER
        )

        self.usertoken = UserToken.objects.create(
            identifier='something',
            device='something',
            user=self.user,
            registration_id='something',
            service=SERVICE_APNS
        )

        self.other_phone = Phone.objects.create(
            phone=self.VALID_PHONE,
            confirmed_at=timezone.now()
        )

        self.other_user = User.objects.create(
            phone=self.other_phone,
            name=self.NAME_ALTERNATE
        )

        self.other_usertoken = UserToken.objects.create(
            identifier='something',
            device='something',
            user=self.other_user,
            registration_id='something',
            service=SERVICE_APNS
        )

        self.store = Store.objects.create(
            name='self',
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
            staff=self.staff,
            name='Owner',
            owner=True
        )
        self.employee = Employee.objects.create(
            staff=self.staff,
            name='Employee'
        )

        self.other_store = Store.objects.create(
            name='other self',
            country='België',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        self.other_staff = Staff.objects.create(
            store=self.other_store,
            email=self.EMAIL_OTHER
        )

        self.other_owner = Employee.objects.create(
            staff=self.other_staff,
            name='Owner',
            owner=True
        )
        self.other_employee = Employee.objects.create(
            staff=self.other_staff,
            name='Employee'
        )

        self.other_owner = Employee.objects.create(
            name=self.NAME_USER,
            staff=self.other_staff,
            owner=True
        )

        self.foodtype = FoodType.objects.create(
            name='FoodType test'
        )

        self.menu = Menu.objects.create(
            name='Menu test',
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
            menu=self.menu
        )

        IngredientRelation.objects.bulk_create([
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 1',
                    group=self.ingredientgroup,
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 2',
                    group=self.ingredientgroup,
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 3',
                    group=self.ingredientgroup,
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 4',
                    group=self.ingredientgroup,
                ),
                food=self.food
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 5',
                    group=self.ingredientgroup,
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
