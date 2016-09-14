import mock
from django.core.exceptions import ValidationError
from Lunchbreak.test import LunchbreakTestCase

from ..models import FoodType, Quantity, Store


class QuantityTestCase(LunchbreakTestCase):

    @mock.patch('googlemaps.Client.geocode')
    def test_quantity(self, mock_geocode):
        self.mock_geocode_results(mock_geocode)
        foodtype = FoodType.objects.create(name='type')

        store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        self.assertRaises(
            ValidationError,
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
