from lunch.models import Store
from rest_framework import permissions

from .models import Employee, Staff


class StoreOwnerPermission(permissions.BasePermission):

    READ_REQUESTS = ['GET']

    def has_permission(self, request, view):
        if request.method not in StoreOwnerPermission.READ_REQUESTS:
            return isinstance(request.user, Employee) and request.user.owner
        return True

    def has_object_permission(self, request, view, obj):
        authenticated_store = None
        user = getattr(request, 'user', None)
        if isinstance(user, Employee):
            authenticated_store = user.staff.store
        elif isinstance(user, Staff):
            authenticated_store = user.store

        if authenticated_store is not None:
            return authenticated_store == (
                obj if isinstance(obj, Store)
                else getattr(obj, 'store', None)
            )
        return False


class StoreOwnerOnlyPermission(StoreOwnerPermission):

    def has_permission(self, request, view):
        return isinstance(request.user, Employee) and request.user.owner
