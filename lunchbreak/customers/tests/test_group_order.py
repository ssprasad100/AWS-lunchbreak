from decimal import Decimal

import mock
from lunch.exceptions import LinkingError
from pendulum import Pendulum

from ..config import (ORDER_STATUS_COMPLETED, ORDER_STATUS_PLACED,
                      ORDER_STATUS_RECEIVED, ORDER_STATUS_STARTED,
                      ORDER_STATUS_WAITING)
from ..exceptions import OnlinePaymentRequired
from ..models import Group, GroupOrder, Order
from ..tasks import send_group_order_email
from .test_group import BaseGroupTestCase


class GroupOrderTestCase(BaseGroupTestCase):

    @property
    def receipt(self):
        return Pendulum.now(
            self.group.store.timezone
        ).at(
            hour=self.group.receipt_time.hour,
            minute=self.group.receipt_time.minute,
            second=self.group.receipt_time.second
        ).add(
            minutes=1
        )

    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('customers.models.Order.is_valid')
    def test_same_store(self, mock_is_valid, mock_is_open, mock_task):
        """Test whether Order.store == Order.group.store."""

        self.assertRaises(
            LinkingError,
            Order.objects.create_with_orderedfood,
            orderedfood=[],
            store=self.other_store,
            receipt=self.receipt,
            group=self.group,
            user=self.user
        )

    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    def test_email_task_triggered(self, mock_task):
        """Test whether the Celery email task is triggered on creation."""

        GroupOrder.objects.create(
            group=self.group,
            date=self.midday.date()
        )

        self.assertEqual(
            mock_task.call_count,
            1
        )

    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('customers.models.Order.is_valid')
    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    def test_create_group_order(self, mock_task, mock_is_valid, mock_is_open):
        """Test whether creating an Order with a group creates a group Order."""

        order = Order.objects.create_with_orderedfood(
            orderedfood=[],
            store=self.store,
            receipt=self.receipt,
            group=self.group,
            user=self.user
        )

        # Creating an order with a group should create a GroupOrder
        self.assertIsNotNone(order.group_order)
        self.assertEqual(
            self.group.group_orders.all().count(),
            1
        )
        self.assertEqual(
            order.group_order.date,
            order.receipt.date()
        )

        # It shouldn't create a duplicate for the same date
        order = Order.objects.create_with_orderedfood(
            orderedfood=[],
            store=self.store,
            receipt=self.receipt,
            group=self.group,
            user=self.user
        )

        self.assertIsNotNone(order.group_order)
        self.assertEqual(
            self.group.group_orders.all().count(),
            1
        )

        # It should create a new GroupOrder if the receipt is for a different date
        order = Order.objects.create_with_orderedfood(
            orderedfood=[],
            store=self.store,
            receipt=Pendulum.now().add(days=1).at(
                hour=self.group.receipt_time.hour,
                minute=self.group.receipt_time.minute,
                second=self.group.receipt_time.second
            ),
            group=self.group,
            user=self.user
        )

        self.assertIsNotNone(order.group_order)
        self.assertEqual(
            self.group.group_orders.all().count(),
            2
        )

    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('customers.models.Order.is_valid')
    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    @mock.patch('customers.tasks.send_group_created_emails.apply_async')
    def test_discount(self, mock_emailstask, mock_task, mock_is_valid, mock_is_open):
        """Test whether a discount is applied to an order.

        Order.total is calculated including discount, Order.total_confirmed is
        not adjusted with a discount. We assume Order.total_confirmed already
        includes the discount.
        """

        group = Group.objects.create(
            name='Test Discount',
            store=self.store,
            email='test_discount@cloock.be',
            discount=10
        )
        group.members.add(self.user)

        total = Decimal(self.food.cost) * Decimal(self.food.amount)
        order = Order.objects.create_with_orderedfood(
            store=self.store,
            receipt=Pendulum.now().add(days=1).at(
                hour=self.group.receipt_time.hour,
                minute=self.group.receipt_time.minute,
                second=self.group.receipt_time.second
            ),
            group=group,
            user=self.user,
            orderedfood=[
                {
                    'original': self.food,
                    'total': total,
                    'amount': self.food.amount
                }
            ]
        )

        total_discounted = Decimal(total * (100 - group.discount) / 100)
        self.assertEqual(
            order.total,
            total_discounted
        )
        self.assertEqual(
            order.discount,
            group.discount
        )

        total_confirmed = Decimal(95)
        order.total_confirmed = total_confirmed
        order.save()
        self.assertEqual(
            order.total,
            total_discounted
        )
        self.assertEqual(
            order.discount,
            group.discount
        )
        # Order.total_confirmed is including discount
        self.assertEqual(
            order.total_confirmed,
            total_confirmed
        )

    def create_order(self, group_order):
        return Order.objects.create(
            store=self.store,
            receipt=group_order.receipt,
            group_order=group_order,
            user=self.user,
            placed=self.midday.subtract(days=1)._datetime
        )

    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    def test_synced_status(self, mock_task, mock_is_open):
        """Test whether changing the status on the GroupOrder changes the statuses on the orders.

        Also test whether changing the status of an Order with a GroupOrder works.
        """

        group_order = GroupOrder.objects.create(
            group=self.group,
            date=self.midday.date()
        )

        self.create_order(group_order)
        self.create_order(group_order)
        self.assertEqual(
            group_order.orders.count(),
            2
        )

        def assert_same_status():
            for order in group_order.orders.all():
                self.assertEqual(
                    group_order.status,
                    order.status
                )

        # On creation all of the statuses should be the same
        assert_same_status()

        # Changing the order status of the group order should
        # also change the status on all of the orders.
        group_order.status = ORDER_STATUS_RECEIVED
        group_order.save()
        assert_same_status()

        # Creating a new order should not change the status to the one of the GroupOrder.
        order3 = self.create_order(group_order)
        self.assertEqual(
            group_order.orders.count(),
            3
        )
        self.assertEqual(
            order3.status,
            ORDER_STATUS_PLACED
        )

        # Changing the status on an order should not be ignored
        order3.status = ORDER_STATUS_COMPLETED
        order3.save()
        self.assertEqual(
            order3.status,
            ORDER_STATUS_COMPLETED
        )

        # Changing the status again, should change all of the statuses
        group_order.status = ORDER_STATUS_COMPLETED
        group_order.save()
        assert_same_status()

    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    def test_completed_change(self, mock_task, mock_is_open):
        """Test whether a completed GroupOrder goes back to in progress if a new order comes in."""

        for status in [ORDER_STATUS_WAITING, ORDER_STATUS_COMPLETED]:
            group_order = GroupOrder.objects.create(
                group=self.group,
                date=self.midday.date(),
                status=status
            )

            self.create_order(group_order)
            group_order.refresh_from_db()
            self.assertEqual(
                group_order.status,
                ORDER_STATUS_STARTED
            )

            group_order.orders.all().delete()
            group_order.delete()

    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    @mock.patch('django.core.mail.EmailMultiAlternatives.send')
    def test_no_email(self, mock_send, mock_task):
        """Test whether a group order email task is ignored if the group order
        doesn't exist or there are no orders."""
        send_group_order_email(-1)
        self.assertFalse(mock_send.called)

        group_order = GroupOrder.objects.create(
            group=self.group,
            date=self.midday.date()
        )

        send_group_order_email(group_order.id)
        self.assertFalse(mock_send.called)

    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    @mock.patch('django.core.mail.EmailMultiAlternatives.send')
    def test_email_successful(self, mock_send, mock_task, mock_is_open):
        """Test whether setting up the group order email goes okay."""
        group_order = GroupOrder.objects.create(
            group=self.group,
            date=self.midday.date()
        )
        self.create_order(group_order)

        send_group_order_email(group_order.id)
        self.assertEqual(
            mock_send.call_count,
            1
        )

    @mock.patch('lunch.models.Store.staff')
    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    @mock.patch('django.core.mail.EmailMultiAlternatives.send')
    def test_payment_online_only_gocardless(self, mock_send, mock_task, mock_is_open, mock_staff):
        """Test whether groups where only online payments are allowed block cash orders."""

        mock_staff.gocardless_ready = True
        mock_staff.payconiq_ready = True

        # Creating a group order when payments online only is True,
        # should result in an error.
        self.group.payment_online_only = True
        self.group.save()

        group_order = GroupOrder.objects.create(
            group=self.group,
            date=self.midday.date()
        )

        # It should raise an error if both are ready
        self.assertRaises(
            OnlinePaymentRequired,
            self.create_order,
            group_order
        )
        # If only gocardless is ready
        mock_staff.gocardless_ready = False
        mock_staff.payconiq_ready = True
        self.assertRaises(
            OnlinePaymentRequired,
            self.create_order,
            group_order
        )

        # And if only payconiq is ready
        mock_staff.gocardless_ready = True
        mock_staff.payconiq_ready = False
        self.assertRaises(
            OnlinePaymentRequired,
            self.create_order,
            group_order
        )

        # Creating a group order when payments online only is False,
        # should result in successfully placing the order.
        self.group.payment_online_only = False
        self.group.save()

        order = self.create_order(group_order)

        # Editing the payments online only should not stop existing orders
        # from updating.
        self.group.payment_online_only = True
        self.group.save()

        order.save()

        # Cash payments should still be allowed even if the group only allows
        # online payments if the store has both disabled.
        mock_staff.gocardless_ready = False
        mock_staff.payconiq_ready = False
        self.create_order(group_order)

    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    def test_sync_same_status(self, mock_task, mock_is_open):
        """Test whether saving the the group order with the same status still
        syncs the status to its group orders."""
        # Create group order
        group_order = GroupOrder.objects.create(
            group=self.group,
            date=self.midday.date()
        )

        # Place an order
        self.create_order(group_order)
        group_order.refresh_from_db()
        self.assertEqual(
            group_order.status,
            ORDER_STATUS_PLACED
        )

        # Set the group status to started
        group_order.status = ORDER_STATUS_STARTED
        group_order.save()
        self.assertEqual(
            group_order.status,
            ORDER_STATUS_STARTED
        )

        # Create a new order
        order = self.create_order(group_order)
        group_order.refresh_from_db()
        self.assertEqual(
            order.status,
            ORDER_STATUS_PLACED
        )
        # The group order status shouldn't change
        self.assertEqual(
            group_order.status,
            ORDER_STATUS_STARTED
        )

        # Setting the status to the same one and saving it should still
        # trigger orders to change.
        group_order.status = ORDER_STATUS_STARTED
        group_order.save()
        order.refresh_from_db()
        self.assertEqual(
            group_order.status,
            ORDER_STATUS_STARTED
        )
        self.assertEqual(
            order.status,
            ORDER_STATUS_STARTED
        )

    @mock.patch('lunch.models.Store.is_open')
    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    def test_group_order_mail_once(self, mock_task, mock_is_open):
        """Test that a group_order_email is only scheduled once."""
        group_order = GroupOrder.objects.create(
            group=self.group,
            date=self.midday.date()
        )
        self.create_order(group_order)
        self.create_order(group_order)
        self.assertEqual(
            mock_task.call_count,
            1
        )
