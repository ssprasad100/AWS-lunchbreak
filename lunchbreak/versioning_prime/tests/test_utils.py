from ..utils import import_base
from .serializers import TestField, TestSerializer
from .testcase import VersioningPrimeTestCase


class UtilsTestCase(VersioningPrimeTestCase):

    def test_import_base(self):
        base, field = import_base(
            'versioning_prime.tests.test_utils.TestSerializer'
        )
        self.assertEqual(base, TestSerializer)
        self.assertIsNone(field)

        base, field = import_base(
            'versioning_prime.tests.test_utils.TestSerializer.specific_field'
        )
        self.assertEqual(base, TestSerializer)
        self.assertEqual(field, 'specific_field')

        base, field = import_base(
            'versioning_prime.tests.test_utils.TestField'
        )
        self.assertEqual(base, TestField)
        self.assertIsNone(field)
