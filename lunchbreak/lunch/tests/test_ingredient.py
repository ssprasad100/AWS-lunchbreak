from . import LunchTestCase
from ..exceptions import LinkingError
from ..models import Ingredient, IngredientGroup, IngredientRelation


class IngredientTestCase(LunchTestCase):

    def setUp(self):
        super().setUp()

        self.food.ingredients.all().delete()
        self.food.ingredientgroups.all().delete()

        self.other_ingredientgroup = IngredientGroup.objects.create(
            name='IngredientGroup test',
            foodtype=self.foodtype,
            store=self.store,
            cost=1
        )

        self.ingredient = Ingredient.objects.create(
            name='Ingredient test case',
            cost=1,
            group=self.ingredientgroup
        )
        self.other_ingredient = Ingredient.objects.create(
            name='Ingredient test case',
            cost=1,
            group=self.other_ingredientgroup
        )

    def test_valid_ingredient_in_group(self):
        """Test whether an ingredient that's in a group of a food is valid for ordering."""

        self.assertRaises(
            LinkingError,
            self.food.check_ingredients,
            ingredients=[self.ingredient]
        )

        self.food.ingredientgroups.add(self.ingredientgroup)

        self.food.check_ingredients(
            ingredients=[self.ingredient]
        )

    def test_valid_ingredient_in_ingredients(self):
        """Test whether an ingredient that's in the ingredients of a food is valid for ordering."""

        self.assertRaises(
            LinkingError,
            self.food.check_ingredients,
            ingredients=[self.ingredient]
        )

        IngredientRelation.objects.create(
            ingredient=self.ingredient,
            food=self.food
        )

        self.food.check_ingredients(
            ingredients=[self.ingredient]
        )

    def test_valid_ingredient_in_both(self):
        """Test whether an ingredient that's in the ingredients and group of a food is valid for ordering."""

        self.assertRaises(
            LinkingError,
            self.food.check_ingredients,
            ingredients=[self.ingredient]
        )

        IngredientRelation.objects.create(
            ingredient=self.ingredient,
            food=self.food
        )
        self.food.ingredientgroups.add(self.ingredientgroup)

        self.food.check_ingredients(
            ingredients=[self.ingredient]
        )
