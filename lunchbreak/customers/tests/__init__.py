from datetime import timedelta

import mock
from django.utils import timezone
from django_sms.models import Phone
from lunch.models import (Food, FoodType, HolidayPeriod, Ingredient,
                          IngredientGroup, IngredientRelation, Menu, Store)
from Lunchbreak.test import LunchbreakTestCase
from push_notifications.models import SERVICE_APNS
from rest_framework.test import APIRequestFactory

from ..models import User, UserToken


class CustomersTestCase(LunchbreakTestCase):

    PHONE_USER = '+32472907604'
    NAME_USER = 'Meneer Aardappel'
    FORMAT = 'json'
    VALID_PHONE = '+32472907605'
    VALID_PHONE2 = '+32479427866'
    INVALID_PHONE = '+123456789'
    PIN = '123456'
    NAME = 'Meneer De Bolle'
    NAME_OTHER = 'Mevrouw De Bolle'
    EMAIL = 'meneer@debolle.com'
    EMAIL_OTHER = 'mevrouw@debolle.com'
    DEVICE = 'Test device'
    REGISTRATION_ID = '123456789'

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def setUp(self, mock_geocode, mock_timezone):
        self.mock_timezone_result(mock_timezone)
        super().setUp()
        self.factory = APIRequestFactory()

        self.phone = Phone.objects.create(
            phone=self.PHONE_USER,
            confirmed_at=timezone.now()
        )
        self.phone_other = Phone.objects.create(
            phone=self.VALID_PHONE2,
            confirmed_at=timezone.now()
        )

        self.mock_geocode_results(
            mock_geocode,
            lat=51.0111595,
            lng=3.9075993
        )

        self.user = User.objects.create(
            phone=self.phone,
            name=self.NAME_USER
        )

        self.user_other = User.objects.create(
            phone=self.phone_other,
            name=self.NAME_OTHER
        )

        self.usertoken = UserToken.objects.create(
            identifier='something',
            device='something',
            user=self.user,
            registration_id='something',
            service=SERVICE_APNS
        )

        self.store = Store.objects.create(
            name='CustomersTestCase',
            country='België',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10,
            timezone='Europe/Brussels'
        )

        self.store_other = Store.objects.create(
            name='CustomersTestCaseOther',
            country='België',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10,
            timezone='Europe/Brussels'
        )

        self.foodtype = FoodType.objects.create(
            name='FoodType test',
            customisable=True
        )

        self.menu = Menu.objects.create(
            name='Menu test',
            store=self.store
        )

        self.ingredientgroup = IngredientGroup.objects.create(
            name='IngredientGroup test',
            foodtype=self.foodtype,
            store=self.store,
            cost=1
        )

        self.food = Food.objects.create(
            name='Food test',
            cost=100.00,
            foodtype=self.foodtype,
            menu=self.menu,
            store=self.store
        )

        ingredient_relations = [
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 1',
                    group=self.ingredientgroup,
                    store=self.store,
                    cost=0.1
                ),
                food=self.food,
                selected=True
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 2',
                    group=self.ingredientgroup,
                    store=self.store,
                    cost=0.1
                ),
                food=self.food,
                selected=True
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 3',
                    group=self.ingredientgroup,
                    store=self.store,
                    cost=0.1
                ),
                food=self.food,
                selected=True
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 4',
                    group=self.ingredientgroup,
                    store=self.store,
                    cost=0.1
                ),
                food=self.food,
                selected=True
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 5',
                    group=self.ingredientgroup,
                    store=self.store,
                    cost=0.1
                ),
                food=self.food,
                selected=False
            )
        ]
        for rel in ingredient_relations:
            rel.save()

        self.unique_food = Food.objects.create(
            name='Unique food',
            cost=1,
            foodtype=self.foodtype,
            menu=self.menu,
            store=self.store
        )

        self.unique_ingredient = Ingredient.objects.create(
            name='Unique ingredient',
            group=self.ingredientgroup,
            store=self.store,
            cost=0.1
        )

        self.unique_ingredientrelation = IngredientRelation.objects.create(
            ingredient=self.unique_ingredient,
            food=self.unique_food,
            selected=True
        )

        HolidayPeriod.objects.bulk_create([
            HolidayPeriod(
                store=self.store,
                start=timezone.now() - timedelta(days=10),
                end=timezone.now() + timedelta(days=10),
                closed=False
            )
        ])

    def clone_model(self, model):
        oldPk = model.pk
        model.pk = None
        model.save()
        return (model, model.__class__.objects.get(pk=oldPk),)
