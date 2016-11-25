from lunch.exceptions import LinkingError
from pendulum import Pendulum

from . import CustomersTestCase
from ..models import Group, Order


class GroupOrderTestCase(CustomersTestCase):

    def setUp(self):
        super().setUp()

        self.group = Group.objects.create(
            name='Test Group',
            store=self.store,
            email='andreas@cloock.be'
        )

    def test_order_receipt(self):
        """Test whether Order.receipt is set to None on group orders."""

        order = Order.objects.create(
            store=self.store,
            receipt=Pendulum.now()._datetime,
            group=self.group,
            user=self.user
        )

        self.assertIsNone(order.receipt)

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
