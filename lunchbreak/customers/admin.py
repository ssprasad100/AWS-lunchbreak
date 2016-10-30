from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.translation import ugettext as _
from lunch.admin import BaseTokenAdmin
from Lunchbreak.utils import format_decimal

from .models import (Address, Group, Heart, Invite, Membership, Order,
                     OrderedFood, PaymentLink, Reservation, TemporaryOrder,
                     User, UserToken)


class PaymentLinkInline(admin.TabularInline):
    model = PaymentLink
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email',)
    inlines = (PaymentLinkInline,)
    search_fields = ('name', 'phone', 'email',)
    list_filter = ('enabled',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'country',)
    search_fields = ('user__name', 'city', 'country',)
    list_filter = ('city', 'country',)


@admin.register(PaymentLink)
class PaymentLinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'redirectflow', 'created_at', 'is_completed')
    readonly_fields = ('store', 'user', 'redirectflow',)
    search_fields = ('user__name', 'store__name',)
    list_filter = ('store',)
    ordering = ('redirectflow__created_at',)

    def created_at(self, paymentlink):
        return paymentlink.redirectflow.created_at

    created_at.short_description = _('aangemaakt')
    created_at.admin_order_field = 'redirectflow__created_at'

    def is_completed(self, paymentlink):
        return paymentlink.redirectflow.is_completed

    is_completed.boolean = True
    is_completed.short_description = _('afgerond')


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'invited_by',)
    search_fields = ('group__name', 'user__name',)
    list_filter = ('status',)


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 2


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'billing',)
    search_fields = ('name', 'users_name',)
    inlines = (MembershipInline,)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'leader',)
    search_fields = ('group__name', 'user__name',)
    list_filter = ('leader',)


@admin.register(Heart)
class HeartAdmin(admin.ModelAdmin):
    list_display = ('store', 'user', 'added',)
    search_fields = ('store__name', 'user__name',)
    list_filter = ('store',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('store', 'user', 'seats', 'status',)
    search_fields = ('store__name', 'user__name',)
    list_filter = ('status', 'store',)


@admin.register(OrderedFood)
class OrderedFoodAdmin(admin.ModelAdmin):
    list_display = ('original', 'order', 'total_display', 'is_original',)
    search_fields = ('order', 'order__user', 'original',)
    list_filter = ('is_original',)

    def total_display(self, instance):
        return format_decimal(instance.total)

    total_display.short_description = _('totale prijs')


class OrderedFoodInline(GenericTabularInline):
    model = OrderedFood
    readonly_fields = ('ingredients', 'comment',)
    extra = 0


class AbstractOrderAdmin(admin.ModelAdmin):
    inlines = (OrderedFoodInline,)

    def total_display(self, instance):
        total = instance.total_confirmed \
            if instance.total_confirmed is not None \
            else instance.total
        return format_decimal(total)

    total_display.short_description = _('totale prijs')

    def count_display(self, instance):
        return instance.orderedfood.all().count()

    count_display.short_description = OrderedFood._meta.verbose_name_plural


@admin.register(Order)
class OrderAdmin(AbstractOrderAdmin):
    list_display = ('store', 'user', 'placed', 'receipt',
                    'status', 'total_display', 'count_display',)
    search_fields = ('store__name', 'user__name',)
    list_filter = ('store', 'status',)
    ordering = ('-placed', '-receipt',)


@admin.register(TemporaryOrder)
class TemporaryOrderAdmin(AbstractOrderAdmin):
    list_display = ('store', 'user', 'count_display',)
    search_fields = ('store__name', 'user__name',)
    list_filter = ('store',)


@admin.register(UserToken)
class UserTokenAdmin(BaseTokenAdmin):
    list_display = ('user',) + BaseTokenAdmin.list_display
    search_fields = ('user__name',)
