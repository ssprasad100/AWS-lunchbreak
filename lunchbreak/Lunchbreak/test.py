import requests
from rest_framework.test import APITestCase, force_authenticate
import json


class LunchbreakTestCase(APITestCase):

    MOCK_ADDRESS = {
        'results': [
            {
                'geometry': {
                    'location': {
                        'lat': 1,
                        'lng': 1
                    }
                }
            }
        ]
    }

    def mock_address_response(self, mock_get, mock_json, return_value=None, lat=None, lng=None):
        if return_value is None:
            return_value = self.MOCK_ADDRESS

            if lat is not None and lng is not None:
                return_value['results'][0]['geometry']['location']['lat'] = lat
                return_value['results'][0]['geometry']['location']['lng'] = lng

        mock_get.return_value = requests.Response()
        mock_json.return_value = return_value

    def assertEqualException(self, response, exception):
        error_message = json.dumps(response.data, indent=4)
        self.assertEqual(response.data['error']['code'], exception.code, error_message)
        self.assertEqual(response.status_code, exception.status_code, error_message)

    def authenticate_request(self, request, view, user=None, *args, **kwargs):
        if user is None:
            user = self.user
        force_authenticate(request, user=user, token=self.usertoken)
        return view.as_view()(request, *args, **kwargs)
