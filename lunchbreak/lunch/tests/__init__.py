from datetime import timedelta

import mock
from django.utils import timezone
from Lunchbreak.test import LunchbreakTestCase
from rest_framework.test import APIRequestFactory

from ..models import (Food, FoodType, HolidayPeriod, Ingredient,
                      IngredientGroup, IngredientRelation, Menu, Store)


class LunchTestCase(LunchbreakTestCase):

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def setUp(self, mock_geocode, mock_timezone):
        self.mock_timezone_result(mock_timezone)
        super().setUp()
        self.factory = APIRequestFactory()

        self.mock_geocode_results(
            mock_geocode,
            lat=51.0111595,
            lng=3.9075993
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

        self.other_store = Store.objects.create(
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
        )

        self.food, self.other_food = self.clone_model(self.food)

        ingredient_relations = [
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 1',
                    group=self.ingredientgroup,
                    cost=0.1
                ),
                food=self.food,
                selected=True
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 2',
                    group=self.ingredientgroup,
                    cost=0.1
                ),
                food=self.food,
                selected=True
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 3',
                    group=self.ingredientgroup,
                    cost=0.1
                ),
                food=self.food,
                selected=True
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 4',
                    group=self.ingredientgroup,
                    cost=0.1
                ),
                food=self.food,
                selected=True
            ),
            IngredientRelation(
                ingredient=Ingredient.objects.create(
                    name='Ingredient 5',
                    group=self.ingredientgroup,
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
        )

        self.unique_ingredient = Ingredient.objects.create(
            name='Unique ingredient',
            group=self.ingredientgroup,
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
        old_pk = model.pk
        model.pk = None
        model.save()
        return (model, model.__class__.objects.get(pk=old_pk),)
