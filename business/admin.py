from business.models import Employee, EmployeeToken, Staff, StaffToken
from django.contrib import admin
from lunch.admin import BaseTokenAdmin


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'password',
                )
            }
        ),
        (
            None,
            {
                'fields': (
                    'store',
                )
            }
        )
    )
    readonly_fields = ('password',)
    list_display = ('store',)
    list_filter = ('store',)
    search_fields = ('store',)
    ordering = ('store',)


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
