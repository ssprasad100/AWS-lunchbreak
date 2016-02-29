from django.contrib import admin
from django_gocardless.models import (Customer, CustomerBankAccount, Mandate,
                                      Merchant, RedirectFlow)


class EditOnly(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Merchant)
class MerchantAdmin(EditOnly):
    pass


@admin.register(Customer)
class CustomerAdmin(EditOnly):
    pass


@admin.register(CustomerBankAccount)
class CustomerBankAccountAdmin(EditOnly):
    pass


@admin.register(Mandate)
class MandateAdmin(EditOnly):
    pass


@admin.register(RedirectFlow)
class RedirectFlowAdmin(EditOnly):
    pass
