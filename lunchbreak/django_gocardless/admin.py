from django.contrib import admin

from .models import (Customer, CustomerBankAccount, Mandate, Merchant, Payment,
                     Payout, RedirectFlow, Subscription)


class EditOnly(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
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


@admin.register(Payout)
class PayoutAdmin(EditOnly):
    pass


@admin.register(Payment)
class PaymentAdmin(EditOnly):
    pass


@admin.register(Subscription)
class SubscriptionAdmin(EditOnly):
    pass
