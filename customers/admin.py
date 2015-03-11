from customers.models import Order, OrderedFood, UserToken, User
from django.contrib import admin
from lunch.admin import FoodAdmin


@admin.register(OrderedFood)
class OrderedFoodAdmin(FoodAdmin):
    list_display = FoodAdmin.list_display + ('amount', 'order',)
    fields = FoodAdmin.fields + ('amount', 'order',)
    readonly_fields = ('cost',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'confirmedAt',)
    fields = ('phone', 'name', 'digitsId', 'requestId', 'confirmedAt',)
    readonly_fields = ('digitsId', 'requestId', 'confirmedAt',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'orderedTime', 'pickupTime', 'status', 'paid',)
    fields = ('user', 'store', 'pickupTime', 'status', 'paid', 'orderedTime',)
    readonly_fields = ('orderedTime',)


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'device', 'user',)
    fields = ('identifier', 'device', 'user',)
