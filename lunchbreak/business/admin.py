from business.models import Employee, EmployeeToken, Staff, StaffToken
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from lunch.admin import BaseTokenAdmin

from .forms import StaffChangeForm, StaffCreationForm


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


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = StaffChangeForm
    add_form = StaffCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        (
            None,
            {
                'fields': ('email', 'password')
            }
        ),
        (
            'Permissions',
            {
                'fields': ('is_superuser',)
            }
        ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2')
            }
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(Staff, UserAdmin)
admin.site.unregister(Group)
