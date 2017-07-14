import mock
from Lunchbreak.tests.testcase import LunchbreakTestCase
from Lunchbreak.exceptions import LunchbreakException

from ..models import FoodType, Quantity, Store


class QuantityTestCase(LunchbreakTestCase):

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_quantity(self, mock_geocode, mock_timezone):
        self.mock_timezone_result(mock_timezone)
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

        foodtype = FoodType.objects.create(
            name='type',
            store=store
        )

        self.assertRaises(
            LunchbreakException,
            Quantity.objects.create,
            foodtype=foodtype,
            store=store,
            minimum=2,
            maximum=1
        )

        Quantity.objects.create(
            foodtype=foodtype,
            store=store,
            minimum=1,
            maximum=2
        )
