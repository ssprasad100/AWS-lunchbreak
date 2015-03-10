from django.contrib import admin
from business.models import Staff, Employee


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
                'fields': ('password',)
            }),
        (None, {'fields': ('store',)})
    )
    readonly_fields = ('password',)
    list_display = ('store',)
    list_filter = ('store',)
    search_fields = ('store',)
    ordering = ('store',)

    def has_add_permission(self, request):
        return False


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
                'fields': ('name', 'password',)
            }),
        (None, {'fields': ('staff',)})
    )
    readonly_fields = ('password',)
    list_display = ('name', 'staff',)
    list_filter = ('staff',)
    search_fields = ('name', 'staff',)
    ordering = ('staff', 'name',)

    def has_add_permission(self, request):
        return False
