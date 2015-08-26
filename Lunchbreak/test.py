from rest_framework.test import APITestCase


class LunchbreakTestCase(APITestCase):

    def assertEqualException(self, response, exception):
        self.assertEqual(response.data['error']['code'], exception.code)
        self.assertEqual(response.status_code, exception.status_code)
