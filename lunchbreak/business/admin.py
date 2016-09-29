from django.contrib import admin
from django.utils.translation import ugettext as _
from lunch.admin import BaseTokenAdmin

from .models import Employee, EmployeeToken, Staff, StaffToken


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('store', 'last_name', 'first_name', 'email',)
    list_filter = ('store',)
    search_fields = ('first_name', 'last_name', 'email', 'store__name',)
    ordering = ('store__name', 'last_name', 'first_name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_store', 'name', 'owner',)
    list_filter = ('owner', 'staff__store',)
    search_fields = ('name', 'staff__store__name',)
    ordering = ('staff__store__name', 'name',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'staff__store',
        )

    def get_store(self, instance):
        return instance.staff.store
    get_store.short_description = _('winkel')


@admin.register(StaffToken)
class StaffTokenAdmin(BaseTokenAdmin):
    list_display = ('staff',) + BaseTokenAdmin.list_display
    search_fields = ('staff__store__name',)


@admin.register(EmployeeToken)
class EmployeeToken(BaseTokenAdmin):
    list_display = ('employee',) + BaseTokenAdmin.list_display
    search_fields = ('employee__name',)
