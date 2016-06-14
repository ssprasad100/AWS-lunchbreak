from django.contrib import admin
from lunch.admin import BaseTokenAdmin

from .models import (Group, Invite, Membership, Order, OrderedFood,
                     PaymentLink, Reservation, User, UserToken)


@admin.register(OrderedFood)
class OrderedFoodAdmin(admin.ModelAdmin):
    list_display = ('amount', 'amount_food', 'cost', 'order', 'original', 'ingredientgroups')
    readonly_fields = ('ingredientgroups',)


class PaymentLinkInline(admin.TabularInline):
    model = PaymentLink
    extra = 2


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'confirmed_at',)
    readonly_fields = ('digits_id', 'request_id', 'confirmed_at',)
    inlines = (PaymentLinkInline,)
    search_fields = ('name',)


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 2


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    fields = ('name', 'billing',)
    inlines = (MembershipInline,)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    pass


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    pass


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    readonly_fields = ('placed',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'placed', 'receipt', 'status', 'payment',)
    readonly_fields = ('placed',)


@admin.register(UserToken)
class UserTokenAdmin(BaseTokenAdmin):
    pass
