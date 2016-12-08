from datetime import timedelta

import mock
from business.models import Staff
from django.core.urlresolvers import reverse
from django.utils import timezone
from django_gocardless.exceptions import MerchantAccessError
from django_gocardless.models import Merchant, RedirectFlow
from lunch.exceptions import LinkingError, NoDeliveryToAddress
from lunch.models import Food
from pendulum import Pendulum
from rest_framework import status

from . import CustomersTestCase
from .. import views
from ..config import (ORDER_STATUS_COMPLETED, ORDER_STATUS_DENIED,
                      ORDER_STATUS_NOT_COLLECTED, ORDER_STATUS_PLACED,
                      ORDER_STATUS_RECEIVED, ORDER_STATUS_STARTED,
                      ORDER_STATUS_WAITING, PAYMENT_METHOD_CASH,
                      PAYMENT_METHOD_GOCARDLESS)
from ..exceptions import OrderedFoodNotOriginal
from ..models import Address, Order, OrderedFood, PaymentLink


class OrderTestCase(CustomersTestCase):

    @mock.patch('customers.models.User.notify')
    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_order(self, mock_geocode, mock_timezone, mock_is_open, mock_notify):
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

        mock_is_open.reset_mock()
        response, order = create_order()
        response.render()
        self.assertIsNotNone(order)
        self.assertTrue(mock_is_open.called)

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

    @mock.patch('lunch.models.Store.is_open')
    def test_order_with_ingredients(self, mock_is_open):
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

    def test_order_signals(self):
        """Test whether all order status signals are sent."""

        mocks = {
            ORDER_STATUS_PLACED: 'customers.signals.order_created.send',
            ORDER_STATUS_DENIED: 'customers.signals.order_denied.send',
            ORDER_STATUS_RECEIVED: 'customers.signals.order_received.send',
            ORDER_STATUS_STARTED: 'customers.signals.order_started.send',
            ORDER_STATUS_WAITING: 'customers.signals.order_waiting.send',
            ORDER_STATUS_COMPLETED: 'customers.signals.order_completed.send',
            ORDER_STATUS_NOT_COLLECTED: 'customers.signals.order_not_collected.send'
        }

        created_signal = mocks.pop(ORDER_STATUS_PLACED)
        with mock.patch(created_signal) as mock_signal:
            self.assertEqual(mock_signal.call_count, 0)
            order = Order.objects.create(
                store=self.store,
                receipt=Pendulum.tomorrow()._datetime,
                user=self.user
            )
            self.assertEqual(mock_signal.call_count, 1)

        for order_status, status_signal in mocks.items():
            with mock.patch(status_signal) as mock_signal:
                self.assertEqual(mock_signal.call_count, 0)
                Order.objects.create(
                    store=self.store,
                    receipt=Pendulum.tomorrow()._datetime,
                    user=self.user,
                    status=order_status
                )
                self.assertEqual(mock_signal.call_count, 1)
                mock_signal.reset_mock()
                order.status = order_status
                order.save()
                self.assertEqual(mock_signal.call_count, 1)

    @mock.patch('business.models.Staff.notify')
    @mock.patch('customers.models.User.notify')
    @mock.patch('customers.models.PaymentLink.delete')
    @mock.patch('django_gocardless.models.RedirectFlow.is_completed', new_callable=mock.PropertyMock)
    @mock.patch('django_gocardless.models.Payment.create')
    def test_create_payment(self, mock_payment, mock_is_completed,
                            mock_pl_delete, mock_user_notify, mock_staff_notify):
        """Test whether the statuses completed and not collected trigger the
        creation of a payment."""

        mock_payment.return_value = None
        mock_is_completed.return_value = True
        merchant = Merchant.objects.create()
        Staff.objects.create(
            store=self.store,
            email='andreas@cloock.be',
            first_name='Andreas',
            last_name='Backx',
            merchant=merchant
        )
        redirectflow = RedirectFlow.objects.create(
            id='RED12345',
            merchant=merchant
        )
        PaymentLink.objects.create(
            user=self.user,
            store=self.store,
            redirectflow=redirectflow
        )
        order = Order.objects.create(
            store=self.store,
            receipt=Pendulum.tomorrow()._datetime,
            user=self.user,
            payment_method=PAYMENT_METHOD_GOCARDLESS
        )

        for order_status in [ORDER_STATUS_COMPLETED, ORDER_STATUS_NOT_COLLECTED]:
            order.status = order_status
            order.save()
            self.assertTrue(mock_payment.called)
            mock_payment.reset_mock()
            self.assertFalse(mock_user_notify.called)
            mock_user_notify.reset_mock()

        mock_payment.side_effect = MerchantAccessError()
        order.status = ORDER_STATUS_COMPLETED
        order.save()

        self.assertEqual(
            order.payment_method,
            PAYMENT_METHOD_CASH
        )
        self.assertRaises(
            Merchant.DoesNotExist,
            merchant.refresh_from_db
        )
        self.assertTrue(mock_pl_delete.called)
        mock_pl_delete.reset_mock()
        self.assertTrue(mock_staff_notify.called)
        mock_staff_notify.reset_mock()
        self.assertTrue(mock_user_notify.called)
        mock_user_notify.reset_mock()
