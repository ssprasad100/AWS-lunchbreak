from customers.models import Order, OrderedFood, User, UserToken
from django.contrib import admin
from lunch.admin import BaseTokenAdmin


@admin.register(OrderedFood)
class OrderedFoodAdmin(admin.ModelAdmin):
    list_display = ('amount', 'foodAmount', 'cost', 'order', 'original', 'ingredientGroups')
    readonly_fields = ('ingredientGroups',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'confirmedAt',)
    readonly_fields = ('digitsId', 'requestId', 'confirmedAt',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'orderedTime', 'pickupTime', 'status', 'paid',)
    readonly_fields = ('orderedTime',)


@admin.register(UserToken)
class UserTokenAdmin(BaseTokenAdmin):
    pass
