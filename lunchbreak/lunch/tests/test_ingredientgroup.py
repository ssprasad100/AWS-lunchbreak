from itertools import permutations

import mock
from customers.models import OrderedFood
from Lunchbreak.exceptions import LunchbreakException

from . import LunchTestCase
from ..config import COST_GROUP_ADDITIONS, COST_GROUP_ALWAYS, COST_GROUP_BOTH
from ..models import FoodType, Ingredient, IngredientGroup, Store


class IngredientGroupTestCase(LunchTestCase):

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_ingredientgroup(self, mock_geocode, mock_timezone):
        self.mock_timezone_result(mock_timezone)
        self.mock_geocode_results(mock_geocode)
        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        foodtype = FoodType.objects.create(name='type')

        group = IngredientGroup(
            name='group',
            foodtype=foodtype,
            store=store,
            maximum=0,
            minimum=1
        )

        try:
            group.save()
        except LunchbreakException:
            try:
                group.minimum = 0
                group.save()

                group.maximum = 1
                group.save()
            except Exception as e:
                self.fail(e)
        else:
            self.fail()

    def all_permutations(self, iterable):
        permuts = (x for i in range(len(iterable), 0, -1) for x in permutations(iterable, i))
        return tuple(permuts) + ((),)

    def setUp(self):
        super().setUp()

        self.ingredientgroup.cost = 10
        self.ingredientgroup.save()

        self.ingredientgroup2 = IngredientGroup.objects.create(
            name='IngredientGroup 2',
            foodtype=self.foodtype,
            store=self.store,
            cost=10
        )

        self.ingredientgroup2_ingredients = [
            Ingredient.objects.create(
                name='Deselected ingredient 21 ingredientgroup2',
                group=self.ingredientgroup2,
                cost=10
            ),
            Ingredient.objects.create(
                name='Deselected ingredient 22 ingredientgroup2',
                group=self.ingredientgroup2,
                cost=10
            ),
        ]

        self.food.ingredientgroups.add(self.ingredientgroup2)

    def ingredient_options(self):

        food_selected_ingredients, food_deselected_ingredients = self.food.all_ingredients
        food_selected_groups = {ingredient.group for ingredient in food_selected_ingredients}

        def get_option(selected, added, removed):
            selected_groups = {ingredient.group for ingredient in selected}
            added_groups = {
                ingredient.group for ingredient in added
                if ingredient.group not in food_selected_groups
            }
            removed_groups = {
                group for group in food_selected_groups
                if group not in selected_groups
            }

            return {
                'ingredients': {
                    'selected': selected,
                    'added': added,
                    'removed': removed,
                },
                'groups': {
                    'selected': selected_groups,
                    'added': added_groups,
                    'removed': removed_groups,
                },
            }

        for reselected_ingredients in self.all_permutations(food_selected_ingredients):
            removed = [
                ingredient for ingredient in food_selected_ingredients
                if ingredient not in reselected_ingredients
            ]

            yield get_option(
                selected=reselected_ingredients,
                added=[],
                removed=removed
            )

            for added in self.all_permutations(food_deselected_ingredients):
                selected = []
                selected.extend(reselected_ingredients)
                selected.extend(added)
                yield get_option(
                    selected=selected,
                    added=added,
                    removed=removed
                )

    def test_cost_group_always(self):
        self.ingredientgroup.calculation = COST_GROUP_ALWAYS
        self.ingredientgroup.save()
        self.ingredientgroup2.calculation = COST_GROUP_ALWAYS
        self.ingredientgroup2.save()

        all_ingredients = self.ingredientgroup.ingredients.all()
        self.assertEqual(
            len(all_ingredients),
            3
        )

        for option in self.ingredient_options():
            calculated_cost = OrderedFood.calculate_cost(
                ingredients=option['ingredients']['selected'],
                food=self.food
            )

            diff_group_cost = 0
            for group in option['groups']['added']:
                diff_group_cost += group.cost
            for group in option['groups']['removed']:
                diff_group_cost -= group.cost

            self.assertEqual(
                calculated_cost,
                self.food.cost + diff_group_cost
            )

    def test_cost_group_additions(self):
        self.ingredientgroup.calculation = COST_GROUP_ADDITIONS
        self.ingredientgroup.save()
        self.ingredientgroup2.calculation = COST_GROUP_ADDITIONS
        self.ingredientgroup2.save()

        all_ingredients = self.ingredientgroup.ingredients.all()
        self.assertEqual(
            len(all_ingredients),
            3
        )

        for option in self.ingredient_options():
            calculated_cost = OrderedFood.calculate_cost(
                ingredients=option['ingredients']['selected'],
                food=self.food
            )

            diff_group_cost = 0
            for group in option['groups']['added']:
                diff_group_cost += group.cost
            for group in option['groups']['removed']:
                diff_group_cost -= group.cost

            diff_ingredients_cost = 0
            for ingredient in option['ingredients']['added']:
                diff_ingredients_cost += ingredient.cost

            self.assertEqual(
                calculated_cost,
                self.food.cost + diff_group_cost + diff_ingredients_cost
            )

    def test_cost_group_both(self):
        self.ingredientgroup.calculation = COST_GROUP_BOTH
        self.ingredientgroup.save()
        self.ingredientgroup2.calculation = COST_GROUP_BOTH
        self.ingredientgroup2.save()

        all_ingredients = self.ingredientgroup.ingredients.all()
        self.assertEqual(
            len(all_ingredients),
            3
        )

        for option in self.ingredient_options():
            calculated_cost = OrderedFood.calculate_cost(
                ingredients=option['ingredients']['selected'],
                food=self.food
            )

            diff_group_cost = 0
            for group in option['groups']['added']:
                diff_group_cost += group.cost
            for group in option['groups']['removed']:
                diff_group_cost -= group.cost

            diff_ingredients_cost = 0
            for ingredient in option['ingredients']['added']:
                diff_ingredients_cost += ingredient.cost
            for ingredient in option['ingredients']['removed']:
                diff_ingredients_cost -= ingredient.cost

            self.assertEqual(
                calculated_cost,
                self.food.cost + diff_group_cost + diff_ingredients_cost
            )
