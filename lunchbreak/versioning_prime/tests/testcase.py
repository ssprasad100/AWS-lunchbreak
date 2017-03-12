import mock
from rest_framework.test import APITestCase


class VersioningPrimeTestCase(APITestCase):

    maxDiff = None

    def setUp(self):
        self.patcher = mock.patch(
            'versioning_prime.apps.VersioningPrimeConfig.get_allowed_versions'
        )
        self.mock_allowed_versions = self.patcher.start()
        self.mock_allowed_versions.return_value = [
            '0.8.1',
            '0.9.0',
            '0.9.1',
            '1.0.0',
            '1.0.1',
            '1.1.0',
            '1.1.1',
        ]

    def tearDown(self):
        self.patcher.stop()
