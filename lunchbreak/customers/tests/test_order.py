import json
from decimal import Decimal

import mock
from django.core.urlresolvers import reverse
from django_gocardless.exceptions import MerchantAccessError
from django_gocardless.models import Merchant as GoCardlessMerchant
from django_gocardless.models import RedirectFlow
from lunch.exceptions import LinkingError, NoDeliveryToAddress
from lunch.models import Food
from payconiq.models import Transaction
from payconiq.views import WebhookView
from rest_framework import status
from rest_framework.exceptions import NotFound

from . import CustomersTestCase
from .. import views
from ..config import (ORDER_STATUS_COMPLETED, ORDER_STATUS_DENIED,
                      ORDER_STATUS_NOT_COLLECTED, ORDER_STATUS_PLACED,
                      ORDER_STATUS_RECEIVED, ORDER_STATUS_STARTED,
                      ORDER_STATUS_WAITING, PAYMENT_METHOD_CASH,
                      PAYMENT_METHOD_GOCARDLESS, PAYMENT_METHOD_PAYCONIQ)
from ..exceptions import CashDisabled
from ..models import Address, ConfirmedOrder, Order, OrderedFood, PaymentLink


class OrderTestCase(CustomersTestCase):

    def place_order(self, content, **extra):
        url = reverse('customers:order-list')
        request = self.factory.post(url, content, **extra)
        response = self.authenticate_request(
            request,
            views.OrderViewSet,
            view_actions={
                'post': 'create'
            }
        )
        if response.status_code == status.HTTP_201_CREATED:
            order = Order.objects.get(
                id=response.data['id']
            )
            return (response, order)
        return (response, None)

    def order_test_versioning(self, get_content, version, mock_is_open):
        self.food, original = self.clone_model(self.food)
        content = get_content(original=original)

        def create_order():
            response, order = self.place_order(
                content=content,
                HTTP_X_VERSION=version
            )
            if order is not None:
                self.assertEqual(order.total, original.cost * 2)
            return response, order

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
        order_orderedfood = OrderedFood.objects.filter(
            placed_order=order
        )
        self.assertEqual(
            order_orderedfood.count(),
            2
        )
        for orderedfood in order_orderedfood.all():
            self.assertIsNone(orderedfood.original)

        # Test delivery address exceptions
        self.food, original = self.clone_model(self.food)
        content = get_content(original=original)
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
        address_other.user = self.other_user
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

    @mock.patch('customers.models.User.notify')
    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_order_decimals(self, mock_geocode, mock_timezone, mock_is_open, mock_notify):
        """
        Test an order's total and whether marked Food's are deleted on save.
        """
        self.mock_timezone_result(mock_timezone)
        self.mock_geocode_results(mock_geocode)

        def get_content(original):
            return {
                'receipt': self.midday.add(days=1).isoformat(),
                'store': self.store.id,
                'orderedfood': [
                    {
                        'original': original.id,
                        'total': Decimal(original.cost) * original.amount / Decimal(100),
                        'amount': original.amount
                    },
                    {
                        'original': original.id,
                        'total': Decimal(original.cost) * original.amount / Decimal(100),
                        'amount': original.amount
                    }
                ]
            }

        self.order_test_versioning(
            get_content=get_content,
            version='2.1.0',
            mock_is_open=mock_is_open
        )

    @mock.patch('customers.models.User.notify')
    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_order_integers(self, mock_geocode, mock_timezone, mock_is_open, mock_notify):
        """
        Test an order's total and whether marked Food's are deleted on save.
        """
        self.mock_timezone_result(mock_timezone)
        self.mock_geocode_results(mock_geocode)

        def get_content(original):
            return {
                'receipt': self.midday.add(days=1).isoformat(),
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

        self.order_test_versioning(
            get_content=get_content,
            version='2.2.0',
            mock_is_open=mock_is_open
        )

    @mock.patch('lunch.models.Store.is_open')
    def test_order_with_ingredients(self, mock_is_open):
        selected_ingredientrelations = self.food.ingredientrelations.filter(
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
            receipt=self.midday.add(hours=1)
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
            receipt=self.midday.add(hours=1)
        )

        of = order.orderedfood.all().first()
        self.assertTrue(of.is_original)
        self.assertFalse(of.ingredients.all().exists())

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
                receipt=self.midday.add(days=1)._datetime,
                user=self.user
            )
            self.assertEqual(mock_signal.call_count, 1)

        for order_status, status_signal in mocks.items():
            with mock.patch(status_signal) as mock_signal:
                self.assertEqual(mock_signal.call_count, 0)
                Order.objects.create(
                    store=self.store,
                    receipt=self.midday.add(days=1)._datetime,
                    user=self.user,
                    status=order_status
                )
                self.assertEqual(mock_signal.call_count, 1)
                mock_signal.reset_mock()
                order.status = order_status
                order.save()
                self.assertEqual(mock_signal.call_count, 1)

    @mock.patch('customers.serializers.OrderSerializer.create')
    def test_ignore_floating_errors(self, mock_create):
        self.food, original = self.clone_model(self.food)

        content = {
            'receipt': self.midday.add(days=1).isoformat(),
            'store': self.store.id,
            'orderedfood': [
                {
                    'total': '4.000000000000001',
                    'amount': original.amount,
                }
            ]
        }
        url = reverse('customers:order-list')

        view_actions = {
            'post': 'create'
        }

        mock_create.side_effect = NotFound()

        request = self.factory.post(url, content)
        response = self.authenticate_request(
            request,
            views.OrderViewSet,
            view_actions=view_actions
        )

        response.render()
        self.assertTrue(mock_create.called)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def place_payconiq_order(self, mock_geocode, mock_timezone,
                             mock_is_open, mock_notify, mock_transaction,
                             transaction_status, confirmed):
        self.mock_timezone_result(mock_timezone)

        self.mock_geocode_results(mock_geocode)
        self.food, original = self.clone_model(self.food)

        total = original.cost * original.amount

        transaction = Transaction.objects.create(
            remote_id='12345',
            amount=total,
            merchant=self.payconiq
        )
        mock_transaction.return_value = transaction

        content = {
            'receipt': self.midday.add(days=1).isoformat(),
            'store': self.store.id,
            'payment_method': PAYMENT_METHOD_PAYCONIQ,
            'orderedfood': [
                {
                    'original': original.id,
                    'total': total,
                    'amount': original.amount
                }
            ]
        }

        def assert_confirmed(order, confirmed, denied):
            self.assertEqual(
                ConfirmedOrder.objects.filter(
                    pk=order.pk
                ).exists(),
                confirmed
            )
            order = Order.objects.get(
                pk=order.pk
            )
            if denied:
                self.assertEqual(
                    order.status,
                    ORDER_STATUS_DENIED
                )
            else:
                self.assertEqual(
                    order.status,
                    ORDER_STATUS_PLACED
                )

        response, order = self.place_order(content)
        self.assertIsNotNone(order)
        assert_confirmed(order, False, False)

        url = reverse('payconiq:webhook')
        data = {
            '_id': transaction.remote_id,
            'status': transaction_status
        }
        request = self.factory.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        response = WebhookView.as_view()(request)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        assert_confirmed(order, confirmed, not confirmed)
        Transaction.objects.all().delete()

    @mock.patch('payconiq.views.WebhookView.is_valid')
    @mock.patch('payconiq.models.Transaction.start')
    @mock.patch('customers.models.User.notify')
    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_payconiq_order(self, mock_geocode, mock_timezone,
                            mock_is_open, mock_notify, mock_transaction, mock_is_valid):
        mock_is_valid.return_value = True
        self.place_payconiq_order(
            mock_geocode, mock_timezone, mock_is_open, mock_notify,
            mock_transaction, transaction_status=Transaction.SUCCEEDED, confirmed=True
        )

        failed_statuses = [
            Transaction.TIMEDOUT,
            Transaction.CANCELED,
            Transaction.FAILED,
        ]
        for failed_status in failed_statuses:
            self.place_payconiq_order(
                mock_geocode, mock_timezone, mock_is_open, mock_notify,
                mock_transaction, transaction_status=failed_status, confirmed=False
            )

    @mock.patch('customers.models.User.notify')
    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_cash_order(self, mock_geocode, mock_timezone,
                        mock_is_open, mock_notify):
        self.store.cash_enabled = False
        self.store.save()

        content = {
            'receipt': self.midday.add(days=1).isoformat(),
            'store': self.store.id,
            'payment_method': PAYMENT_METHOD_CASH,
            'orderedfood': [
                {
                    'original': self.food.id,
                    'total': self.food.cost,
                    'amount': self.food.amount
                }
            ]
        }

        response, order = self.place_order(content)
        self.assertEqualException(
            response,
            CashDisabled
        )

        self.user.cash_enabled_forced = True
        self.user.save()

        response, order = self.place_order(content)
        self.assertIsNotNone(order)

        self.store.cash_enabled = True
        self.store.save()

        response, order = self.place_order(content)
        self.assertIsNotNone(order)

    @mock.patch('business.models.Staff.notify')
    @mock.patch('customers.models.User.notify')
    @mock.patch('customers.models.PaymentLink.delete')
    @mock.patch(
        'django_gocardless.models.RedirectFlow.is_completed',
        new_callable=mock.PropertyMock
    )
    @mock.patch('django_gocardless.models.Payment.create')
    def test_create_payment(self, mock_payment, mock_is_completed,
                            mock_pl_delete, mock_user_notify, mock_staff_notify):
        """Test whether the statuses completed and not collected trigger the
        creation of a payment."""

        mock_payment.return_value = None
        mock_is_completed.return_value = True
        redirectflow = RedirectFlow.objects.create(
            id='RED12345',
            merchant=self.gocardless
        )
        PaymentLink.objects.create(
            user=self.user,
            store=self.store,
            redirectflow=redirectflow
        )
        order = Order.objects.create(
            store=self.store,
            receipt=self.midday.add(days=1)._datetime,
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
            GoCardlessMerchant.DoesNotExist,
            self.gocardless.refresh_from_db
        )
        self.assertTrue(mock_pl_delete.called)
        mock_pl_delete.reset_mock()
        self.assertTrue(mock_staff_notify.called)
        mock_staff_notify.reset_mock()
        self.assertTrue(mock_user_notify.called)
        mock_user_notify.reset_mock()
