import mock
from Lunchbreak.exceptions import LunchbreakException
from Lunchbreak.test import LunchbreakTestCase

from ..models import FoodType, IngredientGroup, Store


class IngredientGroupTestCase(LunchbreakTestCase):

    @mock.patch('googlemaps.Client.geocode')
    def test_ingredientgroup(self, mock_geocode):
        self.mock_geocode_results(mock_geocode)
        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        foodtype = FoodType.objects.create(name='type')

        group = IngredientGroup(
            name='group',
            foodtype=foodtype,
            store=store,
            maximum=0,
            minimum=1
        )

        try:
            group.save()
        except LunchbreakException:
            try:
                group.minimum = 0
                group.save()

                group.maximum = 1
                group.save()
            except Exception as e:
                self.fail(e)
        else:
            self.fail()
