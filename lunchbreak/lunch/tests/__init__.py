from Lunchbreak.test import LunchbreakTestCase

from ..models import FoodType


class LunchTestCase(LunchbreakTestCase):

    def setUp(self):
        super().setUp()

        self.foodtype = FoodType.objects.create(
            name='type'
        )
