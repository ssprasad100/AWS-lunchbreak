
import mock
from Lunchbreak.test import LunchbreakTestCase

from ..config import INPUT_AMOUNT, INPUT_SI_SET, INPUT_SI_VARIABLE
from ..models import FoodType, Quantity, Store


class FoodTypeTestCase(LunchbreakTestCase):

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    def test_foodtype(self, mock_geocode, mock_timezone):
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

        foodtype = FoodType.objects.create(name='type')

        quantity = Quantity.objects.create(
            foodtype=foodtype,
            store=store,
            minimum=1,
            maximum=10
        )

        inputtypes = [
            {
                'type': INPUT_AMOUNT,
                'float': False,
                'integer': True
            }, {
                'type': INPUT_SI_SET,
                'float': True,
                'integer': True
            }, {
                'type': INPUT_SI_VARIABLE,
                'float': True,
                'integer': True
            }
        ]

        for it in inputtypes:
            foodtype.inputtype = it['type']

            self.assertEqual(foodtype.is_valid_amount(1), it['integer'])
            self.assertEqual(foodtype.is_valid_amount(1.5), it['float'])

            quantity.minimum = 1.5
            quantity.maximum = 9.5

            try:
                quantity.save()
            except:
                if it['float']:
                    self.fail(
                        'Input type is float, but raises exception.'
                    )
                elif it['integer']:
                    quantity.minimum = 1
                    quantity.maximum = 9

                    try:
                        quantity.save()
                    except:
                        self.fail(
                            'Input type is integer, but raises exception.'
                        )
