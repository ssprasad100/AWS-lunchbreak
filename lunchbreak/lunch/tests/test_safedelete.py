from . import LunchTestCase


class SafeDeleteTestCase(LunchTestCase):

    def setUp(self):
        super().setUp()

    def test_food_delete(self):
        """Test whether food that is still in an active order is safe deleted.

        If a food is used in an active order, then it should be deleted once
        the order has finished. The OrderedFood and Order cannot be deleted
        in the meantime.
        """

