from rest_framework.test import APITestCase, force_authenticate


class LunchbreakTestCase(APITestCase):

    def assertEqualException(self, response, exception):
        self.assertEqual(response.data['error']['code'], exception.code)
        self.assertEqual(response.status_code, exception.status_code)

    def authenticateRequest(self, request, view, user=None, *args, **kwargs):
        if user is None:
            user = self.user
        force_authenticate(request, user=user, token=self.userToken)
        return view.as_view()(request, *args, **kwargs)
