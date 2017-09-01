from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils.translation import ugettext as _
from frontend.templatetags.filters import amount
from lunch.admin import BaseTokenAdmin
from Lunchbreak.forms import PasswordChangeForm
from Lunchbreak.utils import format_money

from .models import (Address, ConfirmedOrder, Group, GroupOrder, Heart, Order,
                     OrderedFood, PaymentLink, TemporaryOrder, User, UserToken)

admin.site.unregister(DjangoGroup)


class PaymentLinkInline(admin.TabularInline):
    model = PaymentLink
    extra = 0


class GroupInline(admin.TabularInline):
    model = Group.members.through
    extra = 0


class UserChangeForm(PasswordChangeForm):

    class Meta:
        model = User
        fields = ('password', 'password1', 'password2', 'phone',
                  'name', 'email', 'enabled', 'is_staff',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserChangeForm

    list_display = ('get_name', 'phone', 'email', 'confirmed_at', 'created_at',)
    inlines = (GroupInline, PaymentLinkInline,)
    search_fields = ('name', 'phone__phone', 'email',)
    list_filter = ('enabled',)
    ordering = ('-phone__created_at',)

    def get_name(self, obj):
        return str(obj)
    get_name.short_description = _('naam')

    def confirmed_at(self, obj):
        return obj.phone.confirmed_at
    confirmed_at.short_description = _('bevestigd op')

    def created_at(self, obj):
        return obj.phone.created_at
    created_at.short_description = _('aangemaakt op')

    fieldsets = (
        (
            _('Gegevens'),
            {
                'fields': ('phone', 'name', 'email', 'enabled', 'cash_enabled_forced',)
            },
        ),
        (
            _('Wachtwoord'),
            {
                'fields': ('password', 'password1', 'password2',)
            },
        ),
        (
            _('Beheer'),
            {
                'fields': ('is_staff', 'is_superuser',)
            },
        ),
    )
    add_fieldsets = fieldsets


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


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'email', 'discount',
                    'members_count', 'delivery', 'payment_online_only',)
    search_fields = ('name', 'store__name', 'email',)
    list_filter = ('delivery', 'payment_online_only', 'store',)

    def members_count(self, instance):
        return instance.members.all().count()
    members_count.short_description = _('leden')


class OrderInline(admin.TabularInline):
    model = Order
    fields = ('id', 'user', 'store', 'placed', 'receipt', 'status', 'total',
              'total_confirmed', 'discount',)
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]


@admin.register(GroupOrder)
class GroupOrderAdmin(admin.ModelAdmin):
    list_display = ('group', 'date', 'status',)
    inlines = (OrderInline,)
    search_fields = ('group__name',)
    list_filter = ('status', 'date', 'group',)


@admin.register(Heart)
class HeartAdmin(admin.ModelAdmin):
    list_display = ('store', 'user', 'added',)
    search_fields = ('store__name', 'user__name',)
    list_filter = ('added', 'store',)
    ordering = ('-added',)


@admin.register(OrderedFood)
class OrderedFoodAdmin(admin.ModelAdmin):
    list_display = ('original', 'user', 'status', 'cost_display',
                    'amount_display', 'total_display', 'is_original', )
    search_fields = ('order', 'order__user', 'original',),
    list_filter = ('is_original', 'status',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'original__foodtype',
        ).prefetch_related(
            'order__user',
        )

    def cost_display(self, instance):
        return format_money(instance.cost)
    cost_display.short_description = _('kostprijs')
    cost_display.admin_order_field = 'cost'

    def amount_display(self, instance):
        return amount(instance.amount, instance.original.foodtype.inputtype)
    amount_display.short_description = _('hoeveelheid')
    amount_display.admin_order_field = 'amount'

    def total_display(self, instance):
        return format_money(instance.total)
    total_display.short_description = _('totale prijs')
    total_display.admin_order_field = 'total'

    def user(self, instance):
        return instance.order.user
    user.short_description = _('gebruiker')


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
        return format_money(total)
    total_display.short_description = _('totaal')
    total_display.admin_order_field = 'total'

    def count_display(self, instance):
        return instance.orderedfood.all().count()
    count_display.short_description = OrderedFood._meta.verbose_name_plural


class OrderAdmin(AbstractOrderAdmin):
    list_display = ('store', 'user', 'status', 'payment_method',
                    'total_display', 'confirmed', 'placed', 'receipt',)
    search_fields = ('store__name', 'user__name',)
    list_filter = ('placed', 'receipt', 'payment_method', 'status', 'store',)
    ordering = ('-placed', '-receipt',)
    readonly_fields = ('confirmed',)

    def confirmed(self, obj):
        return obj.confirmed
    confirmed.short_description = _('bevestigd')
    confirmed.boolean = True


admin.site.register([Order, ConfirmedOrder], OrderAdmin)


@admin.register(TemporaryOrder)
class TemporaryOrderAdmin(AbstractOrderAdmin):
    list_display = ('store', 'user', 'count_display',)
    search_fields = ('store__name', 'user__name',)
    list_filter = ('store',)


@admin.register(UserToken)
class UserTokenAdmin(BaseTokenAdmin):
    list_display = ('user',) + BaseTokenAdmin.list_display
    search_fields = ('user__name',)
