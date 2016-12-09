from django.core.urlresolvers import reverse
from rest_framework import status

from . import CustomersTestCase
from ..models import Group
from ..views import StoreGroupViewSet


class GroupTestCase(CustomersTestCase):

    def setUp(self):
        super().setUp()

        self.group = Group.objects.create(
            name='Test Group',
            store=self.store,
            email='andreas@cloock.be'
        )

    def test_store_groups(self):
        """Test whether the Store groups request returns joined groups."""

        url = reverse(
            'customers-store-groups-list',
            kwargs={
                'parent_lookup_pk': self.store.id
            }
        )

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
