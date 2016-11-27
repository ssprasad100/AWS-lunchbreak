import mock
from lunch.exceptions import LinkingError
from pendulum import Pendulum

from . import CustomersTestCase
from ..models import Group, GroupOrder, Order


class GroupOrderTestCase(CustomersTestCase):

    def setUp(self):
        super().setUp()

        self.group = Group.objects.create(
            name='Test Group',
            store=self.store,
            email='andreas@cloock.be'
        )

    def test_same_store(self):
        """Test whether Order.store == Order.group.store."""

        self.assertRaises(
            LinkingError,
            Order.objects.create,
            store=self.store_other,
            receipt=Pendulum.now()._datetime,
            group=self.group,
            user=self.user
        )

    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    def test_email_task_triggered(self, mock_task):
        """Test whether the Celery emailt ask is triggered on creation."""

        GroupOrder.objects.create(
            group=self.group,
            date=Pendulum.today().date()
        )

        self.assertTrue(mock_task.called)

    @mock.patch('customers.tasks.send_group_order_email.apply_async')
    def test_create_group_order(self, mock_task):
        """Test whether creating an Order with a group creates a group Order."""

        order = Order.objects.create(
            store=self.store,
            receipt=Pendulum.now()._datetime,
            group=self.group,
            user=self.user
        )

        # Creating an order with a group should create a GroupOrder
        self.assertEqual(
            self.group.group_orders.all().count(),
            1
        )
        self.assertEqual(
            self.group.group_orders.first().date,
            order.receipt.date()
        )

        # It shouldn't create a duplicate for the same date
        Order.objects.create(
            store=self.store,
            receipt=Pendulum.now()._datetime,
            group=self.group,
            user=self.user
        )

        self.assertEqual(
            self.group.group_orders.all().count(),
            1
        )

        # It should create a new GroupOrder if the receipt is for a different date
        Order.objects.create(
            store=self.store,
            receipt=Pendulum.tomorrow()._datetime,
            group=self.group,
            user=self.user
        )

        self.assertEqual(
            self.group.group_orders.all().count(),
            2
        )
