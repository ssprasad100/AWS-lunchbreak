import mock
from django.core.urlresolvers import reverse
from pendulum import Pendulum
from rest_framework import status

from . import CustomersTestCase
from ..models import Group
from ..views import StoreGroupViewSet


class GroupTestCase(CustomersTestCase):

    @mock.patch('customers.tasks.send_group_created_emails.apply_async')
    def setUp(self, mock_task):
        super().setUp()

        self.group = Group.objects.create(
            name='Test Group',
            store=self.store,
            email='andreas@cloock.be',
            deadline=Pendulum.now(self.store.timezone).add(hours=1).time()
        )
        self.group.members.add(self.user)

    def test_store_groups(self):
        """Test whether the Store groups request returns joined groups."""

        url = reverse(
            'customers-store-groups-list',
            kwargs={
                'parent_lookup_pk': self.store.id
            }
        )
        self.group.members.remove(self.user)

        def get_groups():
            request = self.factory.get(url)
            return self.authenticate_request(
                request,
                StoreGroupViewSet,
                view_actions={
                    'get': 'list'
                },
                parent_lookup_pk=self.store.id
            )

        response = get_groups()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            len(response.data),
            0
        )

        self.group.members.add(self.user)

        response = get_groups()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            len(response.data),
            1
        )
        self.assertEqual(
            response.data[0]['id'],
            self.group.id
        )

    @mock.patch('customers.tasks.send_group_created_emails.apply_async')
    def test_send_created_emails(self, mock_task):
        """Test whether the Celery email task is triggered on creation."""
        Group.objects.create(
            name='Signal test',
            store=self.store,
            email='test@cloock.be'
        )
        self.assertTrue(mock_task.called)
