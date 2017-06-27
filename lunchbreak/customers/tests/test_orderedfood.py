import mock
from lunch.models import Food, Ingredient, IngredientRelation

from . import CustomersTestCase
from ..config import ORDEREDFOOD_STATUS_OK, ORDEREDFOOD_STATUS_OUT_OF_STOCK
from ..models import Order, OrderedFood


class OrderedFoodTestCase(CustomersTestCase):

    @mock.patch('lunch.models.Food.is_orderable')
    @mock.patch('lunch.models.Store.is_open')
    def test_status(self, mock_is_open, mock_is_orderable):
        """Test whether updating the status updates the order's total."""
        mock_is_orderable.return_value = True

        orderedfood_data = [
            {
                'original': self.food,
                'amount': 1,
                'total': self.food.cost
            }
        ]

        order = Order.objects.create_with_orderedfood(
            orderedfood=orderedfood_data,
            user=self.user,
            store=self.store,
            receipt=self.midday
        )

        orderedfood = order.orderedfood.first()
        self.assertEqual(
            orderedfood.status,
            ORDEREDFOOD_STATUS_OK
        )
        self.assertEqual(
            order.total,
            orderedfood.total
        )

        orderedfood.status = ORDEREDFOOD_STATUS_OUT_OF_STOCK
        orderedfood.save()
        order.refresh_from_db()
        self.assertEqual(
            order.total,
            0
        )

    @mock.patch('customers.models.ordered_food.uggettext_summation')
    @mock.patch('lunch.models.Food.has_ingredients')
    def test_changes(self, mock_has_ingr, mock_summation):
        """Test whether the changes are reflected well."""
        mock_has_ingr.return_value = True

        orderedfood = OrderedFood(
            id=1,
            is_original=False,
            original=Food()
        )
        from lunch.models import IngredientGroup
        group = IngredientGroup(
            name='group'
        )

        ingredient_a = Ingredient(
            id=1,
            name='a',
            group=group
        )
        ingredient_b = Ingredient(
            id=2,
            name='b',
            group=group
        )
        ingredient_c = Ingredient(
            id=3,
            name='c',
            group=group
        )
        ingredient_d = Ingredient(
            id=4,
            name='d',
            group=group
        )
        ingredient_e = Ingredient(
            id=5,
            name='e',
            group=group
        )
        ingredient_f = Ingredient(
            id=6,
            name='f',
            group=group
        )

        original_relations = [
            IngredientRelation(
                selected=True,
                ingredient=ingredient_a,
            ),
            IngredientRelation(
                selected=True,
                ingredient=ingredient_b,
            ),
            IngredientRelation(
                selected=True,
                ingredient=ingredient_c,
            ),
        ]

        test_results = [
            # Nothing added, nothing removed
            {
                'ordered_ingredients': {
                    ingredient_a,
                    ingredient_b,
                    ingredient_c
                },
                'added_ingredients': set(),
                'removed_ingredients': set(),
            },
            # 1 removed
            {
                'ordered_ingredients': {
                    ingredient_a,
                    ingredient_b,
                },
                'added_ingredients': set(),
                'removed_ingredients': {
                    ingredient_c
                },
            },
            # 2 removed
            {
                'ordered_ingredients': {
                    ingredient_a,
                },
                'added_ingredients': set(),
                'removed_ingredients': {
                    ingredient_b,
                    ingredient_c
                },
            },
            # All 3 removed
            {
                'ordered_ingredients': set(),
                'added_ingredients': set(),
                'removed_ingredients': {
                    ingredient_a,
                    ingredient_b,
                    ingredient_c
                },
            },
            # All 3 added
            {
                'ordered_ingredients': {
                    ingredient_a,
                    ingredient_b,
                    ingredient_c,
                    ingredient_d,
                    ingredient_e,
                    ingredient_f
                },
                'added_ingredients': {
                    ingredient_d,
                    ingredient_e,
                    ingredient_f
                },
                'removed_ingredients': set(),
            },
            # 2 added
            {
                'ordered_ingredients': {
                    ingredient_a,
                    ingredient_b,
                    ingredient_c,
                    ingredient_d,
                    ingredient_e,
                },
                'added_ingredients': {
                    ingredient_d,
                    ingredient_e,
                },
                'removed_ingredients': set(),
            },
            # 1 added
            {
                'ordered_ingredients': {
                    ingredient_a,
                    ingredient_b,
                    ingredient_c,
                    ingredient_d,
                },
                'added_ingredients': {
                    ingredient_d,
                },
                'removed_ingredients': set(),
            },
            # 1 added, 1 removed
            {
                'ordered_ingredients': {
                    ingredient_a,
                    ingredient_b,
                    ingredient_d,
                },
                'added_ingredients': {
                    ingredient_d,
                },
                'removed_ingredients': {
                    ingredient_c,
                },
            },
        ]

        for test_result in test_results:
            ordered_ingredients = test_result['ordered_ingredients']
            added_ingredients = test_result['added_ingredients']
            removed_ingredients = test_result['removed_ingredients']

            OrderedFood.calculate_changes(
                orderedfood=orderedfood,
                original_relations=original_relations,
                ordered_ingredients=ordered_ingredients
            )
            mock_summation.assert_any_call(
                added_ingredients,
                mock.ANY,
            )
            mock_summation.assert_any_call(
                removed_ingredients,
                mock.ANY,
            )
            self.assertEqual(
                mock_summation.call_count,
                2
            )
            mock_summation.reset_mock()

    @mock.patch('lunch.models.Food.is_orderable')
    @mock.patch('lunch.models.Store.is_open')
    def test_save_cascade(self, mock_is_open, mock_is_orderable):
        """Test whether saving an OrderedFood also saved the order attached."""
        mock_is_orderable.return_value = True

        orderedfood_data = [
            {
                'original': self.food,
                'amount': 1,
                'total': self.food.cost
            }
        ]

        order = Order.objects.create_with_orderedfood(
            orderedfood=orderedfood_data,
            user=self.user,
            store=self.store,
            receipt=self.midday
        )
        orderedfood = order.orderedfood.first()

        with mock.patch('customers.models.Order.save') as mock_order_save:
            orderedfood.save()
            self.assertEqual(
                mock_order_save.call_count,
                1
            )
