from django.contrib import admin
from lunch.admin import BaseTokenAdmin

from .models import (Group, Invite, Membership, Order, OrderedFood,
                     Reservation, User, UserToken)


@admin.register(OrderedFood)
class OrderedFoodAdmin(admin.ModelAdmin):
    list_display = ('amount', 'amount_food', 'cost', 'order', 'original', 'ingredientgroups')
    readonly_fields = ('ingredientgroups',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'confirmed_at',)
    readonly_fields = ('digits_id', 'request_id', 'confirmed_at',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass


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
    list_display = ('user', 'store', 'placed', 'pickup', 'status', 'paid',)
    readonly_fields = ('placed',)


@admin.register(UserToken)
class UserTokenAdmin(BaseTokenAdmin):
    pass
