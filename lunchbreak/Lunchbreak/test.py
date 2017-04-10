import json

import mock
from django.conf import settings
from django.test.utils import override_settings
from freezegun import freeze_time
from lunch.models import Store
from pendulum import Pendulum
from rest_framework.test import APITestCase, force_authenticate


class LunchbreakTestCase(APITestCase):

    MOCK_TIMEZONE = {
        'dstOffset': 0,
        'rawOffset': 0,
        'status': 'OK',
        'timeZoneId': 'Europe/Brussels',
        'timeZoneName': 'Central European Summer Time'
    }
    MOCK_ADDRESS = [
        {
            'geometry': {
                'location': {
                    'lat': 1,
                    'lng': 1
                }
            },
            'address_components': [
                {
                    'long_name': 'Wetteren',
                    'types': [
                        'locality',
                    ]
                }
            ]
        }
    ]

    midday = Pendulum.create(
        year=1996,
        month=10,
        day=2,
        hour=12,
        tz=settings.TIME_ZONE
    )

    @override_settings(
        DEFAULT_URL_SCHEME='http',
        ROOT_URLCONF='Lunchbreak.urls.tests',
        GOOGLE_CLOUD_SECRET='AIza',
        DEBUG=True,
        TESTING=True
    )
    def run(self, *args, **kwargs):
        super(LunchbreakTestCase, self).run(*args, **kwargs)

    @mock.patch('googlemaps.Client.timezone')
    @mock.patch('googlemaps.Client.geocode')
    @freeze_time(midday, tick=True)
    def setUp(self, mock_geocode, mock_timezone):
        super().setUp()

        self.mock_geocode_results(mock_geocode)
        self.mock_timezone_result(mock_timezone)
        self.store = Store.objects.create(
            name='valid',
            country='Belgie',
            province='Oost-Vlaanderen',
            city='Wetteren',
            postcode='9230',
            street='Dendermondesteenweg',
            number=10
        )

        self.freezer = freeze_time(self.midday, tick=True)
        self.freezer.start()

    def tearDown(self):
        super().tearDown()
        self.freezer.stop()

    def mock_timezone_result(self, mock_timezone):
        mock_timezone.return_value = self.MOCK_TIMEZONE

    def mock_geocode_results(self, mock_geocode, return_value=None, lat=None, lng=None):
        if return_value is None:
            return_value = self.MOCK_ADDRESS

        if lat is not None and lng is not None:
            return_value[0]['geometry']['location']['lat'] = lat
            return_value[0]['geometry']['location']['lng'] = lng

        mock_geocode.return_value = return_value

    def assertEqualException(self, response, exception):
        if not hasattr(response, 'data'):
            self.fail('Could not read data: ' + str(response.content))
        try:
            error_message = json.dumps(response.data, indent=4)
        except:
            error_message = response.data
        try:
            self.assertEqual(response.data['error']['code'], exception.default_code, error_message)
        except KeyError:
            self.fail(error_message)
        self.assertEqual(response.status_code, exception.status_code, error_message)

    def as_view(self, request, view, view_actions=None, *args, **kwargs):
        if isinstance(view_actions, dict):
            result_view = view.as_view(
                actions=view_actions
            )
        else:
            result_view = view.as_view()
        return result_view(request, *args, **kwargs)

    def authenticate_request(self, request, view, user=None, token=None, view_actions=None, *args, **kwargs):
        if user is None:
            user = self.user
        if token is None:
            token = self.usertoken
        force_authenticate(request, user=user, token=token)
        return self.as_view(request, view, view_actions, *args, **kwargs)

    def assertInCount(self, haystack, needles):
        self.assertEqual(len(haystack), len(needles))

        for needle in needles:
            self.assertIn(needle, haystack)
