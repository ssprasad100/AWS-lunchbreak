from django.http.request import HttpRequest
from rest_framework.request import Request

from ..permissions import StoreOwnerOnlyPermission, StoreOwnerPermission
from .testcase import BusinessTestCase


class OwnerPermissionTestCase(BusinessTestCase):

    def test_store_owner(self):
        permission = StoreOwnerPermission()
        http_request = HttpRequest()
        request = Request(
            request=http_request
        )

        for request_method in StoreOwnerPermission.READ_REQUESTS:
            request.method = request_method
            self.assertTrue(
                permission.has_permission(
                    request=request,
                    view=None
                )
            )

        request.user = self.owner
        request.method = 'POST'
        self.assertTrue(
            permission.has_permission(
                request=request,
                view=None
            )
        )

        request.user = self.employee
        self.assertFalse(
            permission.has_permission(
                request=request,
                view=None
            )
        )

        request.user = self.staff
        self.assertFalse(
            permission.has_permission(
                request=request,
                view=None
            )
        )

    def test_store_owner_only(self):
        permission = StoreOwnerOnlyPermission()
        http_request = HttpRequest()
        request = Request(
            request=http_request
        )

        request.user = self.owner
        request.method = 'GET'
        self.assertTrue(
            permission.has_permission(
                request=request,
                view=None
            )
        )

        request.user = self.employee
        self.assertFalse(
            permission.has_permission(
                request=request,
                view=None
            )
        )

        request.user = self.staff
        self.assertFalse(
            permission.has_permission(
                request=request,
                view=None
            )
        )

    def test_object_permission(self):
        permission = StoreOwnerPermission()
        http_request = HttpRequest()
        request = Request(
            request=http_request
        )

        self.assertFalse(
            permission.has_object_permission(
                request=request,
                view=None,
                obj=None
            )
        )

        allowed_access = [self.owner, self.employee]
        denied_access = [self.other_owner, self.other_employee]

        access_users = allowed_access + denied_access

        for access_user in access_users:
            request.user = access_user
            self.assertEqual(
                permission.has_object_permission(
                    request=request,
                    view=None,
                    obj=self.menu
                ),
                access_user in allowed_access
            )
            self.assertEqual(
                permission.has_object_permission(
                    request=request,
                    view=None,
                    obj=self.store
                ),
                access_user in allowed_access
            )
