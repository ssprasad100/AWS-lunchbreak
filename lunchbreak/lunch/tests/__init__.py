from datetime import timedelta

import mock
from django.utils import timezone
from Lunchbreak.tests.testcase import LunchbreakTestCase

from ..models import (Food, FoodType, HolidayPeriod, Ingredient,
                      IngredientGroup, IngredientRelation, Menu, Store)


class LunchTestCase(LunchbreakTestCase):

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def setUp(self, mock_geocode, mock_timezone):
        self.mock_timezone_result(mock_timezone)
        super().setUp()

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
            name='IngredientGroup 1',
            foodtype=self.foodtype,
            store=self.store,
            cost=10
        )

        self.food = Food.objects.create(
            name='Food test',
            cost=100,
            foodtype=self.foodtype,
            menu=self.menu,
        )

        self.ingredient = Ingredient.objects.create(
            name='Selected ingredient 1',
            group=self.ingredientgroup,
            cost=10
        )

        self.food, self.other_food = self.clone_model(self.food)

        self.selected_ingredient = IngredientRelation.objects.create(
            ingredient=self.ingredient,
            food=self.food,
            selected=True
        )
        self.deselected_ingredient = Ingredient.objects.create(
            name='Deselected ingredient 11',
            group=self.ingredientgroup,
            cost=10
        )
        IngredientRelation.objects.create(
            ingredient=self.deselected_ingredient,
            food=self.food,
            selected=False
        )

        self.unique_food = Food.objects.create(
            name='Unique food',
            cost=1,
            foodtype=self.foodtype,
            menu=self.menu,
        )

        self.unique_ingredient = Ingredient.objects.create(
            name='Unique ingredient',
            group=self.ingredientgroup,
            cost=10
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
