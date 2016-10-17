from lunch.config import (COST_GROUP_ADDITIONS, COST_GROUP_ALWAYS,
                          COST_GROUP_BOTH)

from . import CustomersTestCase
from ..models import OrderedFood


class OrderedFoodTestCase(CustomersTestCase):

    def test_orderedfood_calculate_cost(self):
        self.ingredientgroup.calculation = COST_GROUP_ALWAYS
        self.ingredientgroup.save()

        selected_ingredientrelations = self.food.ingredientrelation_set.filter(
            selected=True
        )
        selected_ingredients = [r.ingredient for r in selected_ingredientrelations]
        selected_ingredient = selected_ingredients[0]
        deselected_ingredient = self.food.ingredientrelation_set.filter(
            selected=False
        ).first().ingredient

        # Check whether the calculated cost with all of the ingredients
        # remains the same.
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost
        )

        # Check whether the calculated cost with none of the ingredients
        # equals that of the food - the cost of the ingredient group
        self.assertEqual(
            OrderedFood.calculate_cost(
                [],
                self.food
            ),
            self.food.cost - self.ingredientgroup.cost
        )

        # Check whether the calculated cost with 1 missing ingredient
        # remains the same.
        selected_ingredients.remove(selected_ingredient)
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost
        )

        # Check whether the calculated cost with 1 added ingredient
        # remains the same.
        selected_ingredients.append(selected_ingredient)
        selected_ingredients.append(deselected_ingredient)
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost
        )
        selected_ingredients.remove(deselected_ingredient)

        # Check whether the value changes only when adding
        self.ingredientgroup.calculation = COST_GROUP_ADDITIONS
        self.ingredientgroup.save()
        deselected_ingredient.group.refresh_from_db()

        # Check whether the calculated cost with all of the ingredients
        # remains the same.
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost
        )

        # Check whether the calculated cost with 1 missing ingredient
        # remains the same.
        selected_ingredients.remove(selected_ingredient)
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost
        )

        # Check whether the calculated cost with 1 added ingredient
        # remains the same.
        selected_ingredients.append(selected_ingredient)
        selected_ingredients.append(deselected_ingredient)
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost + deselected_ingredient.cost
        )
        selected_ingredients.remove(deselected_ingredient)

        # Check whether the calculated cost with none of the ingredients
        # equals that of the food - the cost of the ingredient group
        self.assertEqual(
            OrderedFood.calculate_cost(
                [],
                self.food
            ),
            self.food.cost - self.ingredientgroup.cost
        )

        # Check whether the value changes only when adding and removing
        self.ingredientgroup.calculation = COST_GROUP_BOTH
        self.ingredientgroup.save()

        # Check whether the calculated cost with all of the ingredients
        # remains the same.
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost
        )

        # Check whether the calculated cost with 1 missing ingredient
        # remains the same.
        selected_ingredients.remove(selected_ingredient)
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost - selected_ingredient.cost
        )

        # Check whether the calculated cost with 1 added ingredient
        # remains the same.
        selected_ingredients.append(selected_ingredient)
        selected_ingredients.append(deselected_ingredient)
        self.assertEqual(
            OrderedFood.calculate_cost(
                selected_ingredients,
                self.food
            ),
            self.food.cost + deselected_ingredient.cost
        )
        selected_ingredients.remove(deselected_ingredient)

        # Check whether the calculated cost with none of the ingredients
        # equals that of the food - the separate costs of the ingredients
        cost_separate_ingredients = 0
        for ingredient in selected_ingredients:
            cost_separate_ingredients += ingredient.cost
        self.assertEqual(
            OrderedFood.calculate_cost(
                [],
                self.food
            ),
            self.food.cost - cost_separate_ingredients
        )
