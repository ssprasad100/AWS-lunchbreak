from django.contrib import admin
from django.utils.translation import ugettext as _
from lunch.admin import BaseTokenAdmin
from Lunchbreak.forms import PasswordChangeForm

from .models import Employee, EmployeeToken, Staff, StaffToken


class StaffChangeForm(PasswordChangeForm):

    class Meta:
        model = Staff
        fields = ('password', 'password1', 'password2', 'store',
                  'email', 'first_name', 'last_name', 'merchant',)


class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 0
    fields = ('name', 'owner',)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    form = StaffChangeForm
    list_display = ('store', 'last_name', 'first_name', 'email',)
    inlines = (EmployeeInline,)
    list_filter = ('store',)
    search_fields = ('first_name', 'last_name', 'email', 'store__name',)
    ordering = ('store__name', 'last_name', 'first_name',)

    fieldsets = (
        (
            _('Gegevens'),
            {
                'fields': ('store', 'email', 'first_name', 'last_name',)
            },
        ),
        (
            _('Wachtwoord'),
            {
                'fields': ('password', 'password1', 'password2',)
            },
        ),
        (
            _('Online betalingen'),
            {
                'fields': ('merchant',)
            },
        ),
    )


class EmployeeChangeForm(PasswordChangeForm):

    class Meta:
        model = Employee
        fields = ('password', 'password1', 'password2', 'staff',
                  'name', 'owner',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeChangeForm
    list_display = ('get_store', 'name', 'owner',)
    list_filter = ('owner', 'staff__store',)
    search_fields = ('name', 'staff__store__name',)
    ordering = ('staff__store__name', 'name',)
    readonly_fields = ('get_store',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'staff__store',
        )

    def get_store(self, instance):
        if instance.staff is None:
            return None
        return instance.staff.store
    get_store.short_description = _('winkel')

    fieldsets = (
        (
            _('Gegevens'),
            {
                'fields': ('staff', 'get_store', 'name', 'owner',)
            },
        ),
        (
            _('Wachtwoord'),
            {
                'fields': ('password', 'password1', 'password2',)
            },
        ),
    )


@admin.register(StaffToken)
class StaffTokenAdmin(BaseTokenAdmin):
    list_display = ('staff',) + BaseTokenAdmin.list_display
    search_fields = ('staff__store__name',)


@admin.register(EmployeeToken)
class EmployeeToken(BaseTokenAdmin):
    list_display = ('employee',) + BaseTokenAdmin.list_display
    search_fields = ('employee__name',)
