import mock
from django.core.urlresolvers import reverse
from rest_framework import status

from . import CustomersTestCase
from ..models import Group
from ..tasks import send_group_created_emails
from ..views import StoreGroupViewSet


class BaseGroupTestCase(CustomersTestCase):

    @mock.patch('customers.tasks.send_group_created_emails.apply_async')
    def setUp(self, mock_task):
        super().setUp()

        self.group = Group.objects.create(
            name='Test Group',
            store=self.store,
            email='andreas@cloock.be',
            deadline=self.midday.time()
        )
        self.group.members.add(self.user)


class GroupTestCase(BaseGroupTestCase):

    def get_groups(self):
        url = reverse(
            'customers:store-groups-list',
            kwargs={
                'parent_lookup_pk': self.store.id
            }
        )
        request = self.factory.get(url)
        return self.authenticate_request(
            request,
            StoreGroupViewSet,
            view_actions={
                'get': 'list'
            },
            parent_lookup_pk=self.store.id
        )

    def test_store_groups(self):
        """Test whether the Store groups request returns joined groups."""
        self.group.members.remove(self.user)

        response = self.get_groups()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            len(response.data),
            0
        )

        self.group.members.add(self.user)

        response = self.get_groups()
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

    def test_user_cash_enabled_forced(self):
        """Test whether User.cash_enabled_forced makes Group.payment_online_only == False."""

        self.group.members.add(self.user)

        def validate(expected):
            response = self.get_groups()
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK
            )
            self.assertEqual(
                len(response.data),
                1
            )
            self.assertEqual(
                response.data[0]['payment_online_only'],
                expected
            )

        # Group.payment_online_only == False
        # User.cash_enabled_forced == False
        # Result == False
        self.group.payment_online_only = False
        self.group.save()
        self.user.cash_enabled_forced = False
        self.user.save()
        validate(expected=False)

        # Group.payment_online_only == True
        # User.cash_enabled_forced == False
        # Result == True
        self.group.payment_online_only = True
        self.group.save()

        validate(expected=True)

        # Group.payment_online_only == False
        # User.cash_enabled_forced == True
        # Result == False
        self.group.payment_online_only = False
        self.group.save()
        self.user.cash_enabled_forced = True
        self.user.save()

        validate(expected=False)

        # Group.payment_online_only == True
        # User.cash_enabled_forced == True
        # Result == False
        self.group.payment_online_only = True
        self.group.save()
        self.user.cash_enabled_forced = True
        self.user.save()

        validate(expected=False)

    @mock.patch('customers.tasks.send_group_created_emails.apply_async')
    def test_send_created_emails(self, mock_task):
        """Test whether the Celery email task is triggered on creation."""
        Group.objects.create(
            name='Signal test',
            store=self.store,
            email='test@cloock.be'
        )
        self.assertTrue(mock_task.called)

    @mock.patch('customers.tasks.send_group_created_emails.apply_async')
    @mock.patch('django.core.mail.EmailMultiAlternatives.send')
    def test_no_email(self, mock_send, mock_task):
        """Test whether a group created email task is ignored if the group doesn't exist."""
        send_group_created_emails(-1)
        self.assertFalse(mock_send.called)

    @mock.patch('customers.tasks.send_group_created_emails.apply_async')
    @mock.patch('django.core.mail.EmailMultiAlternatives.send')
    def test_email_successful(self, mock_send, mock_task):
        """Test whether setting up the group created email goes okay."""
        send_group_created_emails(self.group.id)
        self.assertEqual(mock_send.call_count, 2)
