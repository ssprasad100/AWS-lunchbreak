import mock

from .testcase import BusinessTestCase
from ..models import Staff


class NotifyModelMixinTestCase(BusinessTestCase):

    @mock.patch('push_notifications.models.DeviceQuerySet.send_message')
    def test_notify(self, mock_message):
        self.staff.notify('Hallo')
        self.assertTrue(mock_message.called)
        mock_message.reset_mock()

        Staff.objects.filter(
            id=self.staff.id
        ).notify('Hallo')
        self.assertTrue(mock_message.called)
        mock_message.reset_mock()
