from customers.models import Order, OrderedFood, Reservation, User, UserToken
from django.contrib import admin
from lunch.admin import BaseTokenAdmin


@admin.register(OrderedFood)
class OrderedFoodAdmin(admin.ModelAdmin):
    list_display = ('amount', 'amount_food', 'cost', 'order', 'original', 'ingredientgroups')
    readonly_fields = ('ingredientgroups',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'confirmed_at',)
    readonly_fields = ('digits_id', 'request_id', 'confirmed_at',)


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
