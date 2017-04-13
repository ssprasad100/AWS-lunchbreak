from lunch.models import StoreHeader
from Lunchbreak.tests.testcase import LunchbreakTestCase
from polaroid.tests import PolaroidTestCase


class StoreHeaderTestCase(LunchbreakTestCase, PolaroidTestCase):

    def test_last_modified(self):
        original_value = self.store.last_modified

        StoreHeader.objects.create(
            store=self.store,
            original=self.image
        )

        self.assertNotEqual(
            original_value,
            self.store.last_modified
        )
