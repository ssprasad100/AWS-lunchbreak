from django.contrib import admin
from lunch.admin import BaseTokenAdmin

from .models import Employee, EmployeeToken, Staff, StaffToken


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': (
                    'name',
                    'password',
                    'owner',
                )
            }
        ),
        (
            None,
            {
                'fields': (
                    'staff',
                )
            }
        )
    )
    readonly_fields = ('password',)
    list_display = ('name', 'staff', 'owner',)
    list_filter = ('staff',)
    search_fields = ('name', 'staff',)
    ordering = ('staff', 'name',)


@admin.register(StaffToken)
class StaffTokenAdmin(BaseTokenAdmin):
    pass


@admin.register(EmployeeToken)
class EmployeeToken(BaseTokenAdmin):
    pass


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    readonly_fields = ('password', 'merchant',)
    list_display = ('store', 'email', 'first_name', 'last_name',)
    list_filter = ('store',)
    search_fields = ('first_name', 'last_name', 'store__name',)
    ordering = ('store', 'first_name', 'last_name',)
