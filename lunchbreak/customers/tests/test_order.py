from datetime import timedelta

import mock
from django.core.urlresolvers import reverse
from django.utils import timezone
from lunch.exceptions import LinkingError, NoDeliveryToAddress
from lunch.models import Food
from rest_framework import status

from . import CustomersTestCase
from .. import views
from ..config import ORDER_STATUS_COMPLETED
from ..exceptions import OrderedFoodNotOriginal
from ..models import Address, Order, OrderedFood


class OrderTestCase(CustomersTestCase):

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_order(self, mock_geocode, mock_timezone):
        """
        Test an order's total and whether marked Food's are deleted on save.
        """
        self.mock_timezone_result(mock_timezone)

        self.mock_geocode_results(mock_geocode)
        self.food, original = self.clone_model(self.food)

        content = {
            'receipt': (timezone.now() + timedelta(days=1)).isoformat(),
            'store': self.store.id,
            'orderedfood': [
                {
                    'original': original.id,
                    'total': original.cost * original.amount,
                    'amount': original.amount
                },
                {
                    'original': original.id,
                    'total': original.cost * original.amount,
                    'amount': original.amount
                }
            ]
        }
        url = reverse('customers-order-list')

        view_actions = {
            'post': 'create'
        }

        def create_order():
            request = self.factory.post(url, content)
            response = self.authenticate_request(
                request,
                views.OrderViewSet,
                view_actions=view_actions
            )
            if response.status_code == status.HTTP_201_CREATED:
                order = Order.objects.get(id=response.data['id'])
                self.assertEqual(order.total, original.cost * 2)
                return (response, order)
            return (response, None)

        response, order = create_order()
        response.render()
        self.assertIsNotNone(order)

        original.delete()
        self.assertTrue(original.deleted)
        order.status = ORDER_STATUS_COMPLETED
        order.save()
        self.assertRaises(
            Food.DoesNotExist,
            Food.objects.get,
            id=original.id
        )
        self.assertEqual(
            OrderedFood.objects.filter(
                placed_order=order
            ).count(),
            0
        )

        # Test delivery address exceptions
        self.food, original = self.clone_model(self.food)
        content['orderedfood'] = [
            {
                'original': original.id,
                'total': original.cost * original.amount,
                'amount': original.amount
            },
            {
                'original': original.id,
                'total': original.cost * original.amount,
                'amount': original.amount
            }
        ]

        address = Address.objects.create(
            user=self.user,
            country='België',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )
        address, address_other = self.clone_model(address)
        address_other.user = self.user_other
        address_other.save()

        content['delivery_address'] = address.id
        response, order = create_order()
        self.assertEqualException(response, NoDeliveryToAddress)

        content['delivery_address'] = address_other.id
        response, order = create_order()
        self.assertEqualException(response, LinkingError)

        # Orders meant to be picked up cannot have receipt be None
        del content['receipt']
        del content['delivery_address']
        response, order = create_order()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_with_ingredients(self):
        selected_ingredientrelations = self.food.ingredientrelation_set.filter(
            selected=True
        )
        selected_ingredients = [r.ingredient for r in selected_ingredientrelations]

        orderedfood = [
            {
                'original': self.food,
                'amount': 1,
                'total': self.food.cost
            }
        ]

        order = Order.objects.create_with_orderedfood(
            orderedfood=orderedfood,
            user=self.user,
            store=self.store,
            receipt=timezone.now() + timedelta(hours=1)
        )

        of = order.orderedfood.all().first()
        self.assertTrue(of.is_original)
        self.assertFalse(of.ingredients.all().exists())

        # Adding the same ingredients as selected on the food doesn't set the
        # ingredients on the OrderedFood.
        orderedfood[0]['ingredients'] = selected_ingredients
        order = Order.objects.create_with_orderedfood(
            orderedfood=orderedfood,
            user=self.user,
            store=self.store,
            receipt=timezone.now() + timedelta(hours=1)
        )

        of = order.orderedfood.all().first()
        self.assertTrue(of.is_original)
        self.assertFalse(of.ingredients.all().exists())

        orderedfood[0]['ingredients'] = [self.unique_ingredient]
        self.assertEqual(
            Food.objects.closest(
                ingredients=orderedfood[0]['ingredients'],
                original=self.food
            ),
            self.unique_food
        )
        self.assertRaises(
            OrderedFoodNotOriginal,
            Order.objects.create_with_orderedfood,
            orderedfood=orderedfood,
            user=self.user,
            store=self.store,
            receipt=timezone.now() + timedelta(hours=1)
        )
