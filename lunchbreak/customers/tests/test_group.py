from . import CustomersTestCase
from ..config import (INVITE_STATUS_ACCEPTED, INVITE_STATUS_IGNORED,
                      INVITE_STATUS_WAITING)
from ..exceptions import (AlreadyMembership, InvalidStatusChange,
                          NoInvitePermissions)
from ..models import Group, Invite, Membership


class GroupTestCase(CustomersTestCase):

    def test_already_membership(self):
        group = Group.create(
            name='Test',
            user=self.user
        )

        Membership.objects.create(
            group=group,
            user=self.user_other
        )

        self.assertRaises(
            AlreadyMembership,
            Invite.objects.create,
            group=group,
            user=self.user_other,
            invited_by=self.user
        )

        Group.objects.all().delete()

    def test_permission(self):
        group = Group.create(
            name='Test',
            user=self.user
        )

        Invite.objects.create(
            group=group,
            user=self.user_other,
            invited_by=self.user
        )

        self.assertRaises(
            NoInvitePermissions,
            Invite.objects.create,
            group=group,
            user=self.user,
            invited_by=self.user_other
        )

        Group.objects.all().delete()

    def test_accept(self):
        group = Group.create(
            name='Test',
            user=self.user
        )

        invite = Invite.objects.create(
            group=group,
            user=self.user_other,
            invited_by=self.user
        )

        invite.status = INVITE_STATUS_ACCEPTED
        invite.save()

        self.assertIsNotNone(invite.membership)

    def test_delete(self):
        group = Group.create(
            name='Test',
            user=self.user
        )

        invite = Invite.objects.create(
            group=group,
            user=self.user_other,
            invited_by=self.user
        )

        invite.delete()
        self.assertRaises(
            Invite.DoesNotExist,
            Invite.objects.get,
            group=group,
            user=self.user_other,
            invited_by=self.user,
        )

        invite.status = INVITE_STATUS_ACCEPTED
        invite.save()
        invite.delete()
        self.assertEqual(
            Invite.objects.filter(
                group=group,
                user=self.user_other,
                invited_by=self.user
            ).count(),
            1
        )

    def test_status(self):
        group = Group.create(
            name='Test',
            user=self.user
        )

        status_tree = {
            INVITE_STATUS_WAITING: {
                'valid': [
                    INVITE_STATUS_ACCEPTED,
                    INVITE_STATUS_IGNORED
                ],
                'invalid': [
                ]
            },
            INVITE_STATUS_ACCEPTED: {
                'valid': [],
                'invalid': [
                    INVITE_STATUS_WAITING,
                    INVITE_STATUS_IGNORED
                ]
            },
            INVITE_STATUS_IGNORED: {
                'valid': [],
                'invalid': [
                    INVITE_STATUS_WAITING,
                    INVITE_STATUS_ACCEPTED
                ]
            },
        }

        def invite_reset(status):
            Invite.objects.all().delete()
            Membership.objects.filter(
                group=group,
                user=self.user_other
            ).delete()
            return Invite.objects.create(
                group=group,
                user=self.user_other,
                invited_by=self.user,
                status=status
            )

        for status_from, status_to in status_tree.items():
            for status_valid in status_to['valid']:
                invite = invite_reset(status_from)
                invite.status = status_valid
                invite.save()
            for status_invalid in status_to['invalid']:
                invite = invite_reset(status_from)
                invite.status = status_invalid
                self.assertRaises(
                    InvalidStatusChange,
                    invite.save
                )

        Group.objects.all().delete()

    # def test_already_invited(self):
    #     group = Group.create(
    #         name='Test',
    #         user=self.user
    #     )

    #     Invite.objects.create(
    #         group=group,
    #         user=self.user_other,
    #         invited_by=self.user
    #     )

    #     self.assertRaises(
    #         IntegrityError,
    #         Invite.objects.create,
    #         group=group,
    #         user=self.user_other,
    #         invited_by=self.user
    #     )

    #     Group.objects.all().delete()
