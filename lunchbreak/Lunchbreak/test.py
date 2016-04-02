import json

import requests
from django.conf import settings
from django.test.utils import override_settings
from rest_framework.test import APITestCase, force_authenticate


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

    def setUp(self):
        from django.contrib.sites.models import Site
        self.site = Site.objects.get_current()
        self.site.domain = settings.HOST
        self.site.save()

    @override_settings(
        DEFAULT_URL_SCHEME='http',
        ROOT_URLCONF='Lunchbreak.urls.tests'
    )
    def run(self, *args, **kwargs):
        super(LunchbreakTestCase, self).run(*args, **kwargs)

    def mock_address_response(self, mock_get, mock_json, return_value=None, lat=None, lng=None):
        if return_value is None:
            return_value = self.MOCK_ADDRESS

            if lat is not None and lng is not None:
                return_value['results'][0]['geometry']['location']['lat'] = lat
                return_value['results'][0]['geometry']['location']['lng'] = lng

        mock_get.return_value = requests.Response()
        mock_json.return_value = return_value

    def assertEqualException(self, response, exception):
        if not hasattr(response, 'data'):
            self.fail('Could not read data: ' + str(response.content))
        error_message = json.dumps(response.data, indent=4)
        self.assertEqual(response.data['error']['code'], exception.code, error_message)
        self.assertEqual(response.status_code, exception.status_code, error_message)

    def as_view(self, request, view, view_actions=None, *args, **kwargs):
        if isinstance(view_actions, dict):
            result_view = view.as_view(
                actions=view_actions
            )
        else:
            result_view = view.as_view()
        return result_view(request, *args, **kwargs)

    def authenticate_request(self, request, view, user=None, view_actions=None, *args, **kwargs):
        if user is None:
            user = self.user
        force_authenticate(request, user=user, token=self.usertoken)
        return self.as_view(request, view, view_actions, *args, **kwargs)
