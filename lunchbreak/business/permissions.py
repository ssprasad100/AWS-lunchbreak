from rest_framework import permissions

from .models import Employee, Staff


class StoreOwnerPermission(permissions.BasePermission):

    READ_REQUESTS = ['GET']

    def has_permission(self, request, view):
        if request.method not in StoreOwnerPermission.READ_REQUESTS:
            return isinstance(request.user, Employee) and request.user.owner
        return True

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'store'):
            store = None
            if isinstance(request.user, Employee):
                store = request.user.staff.store
            elif isinstance(request.user, Staff):
                store = request.user.store

            if store is not None:
                return store == obj.store
            return False
        return True


class StoreOwnerOnlyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return isinstance(request.user, Employee) and request.user.owner

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'store'):
            store = None
            if isinstance(request.user, Employee):
                store = request.user.staff.store
            elif isinstance(request.user, Staff):
                store = request.user.store

            if store is not None:
                return store == obj.store
            return False
        return True
