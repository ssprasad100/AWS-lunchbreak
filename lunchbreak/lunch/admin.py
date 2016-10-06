from django import forms
from django.contrib import admin
from imagekit.admin import AdminThumbnail

from .models import (DeliveryPeriod, Food, FoodType, HolidayPeriod, Ingredient,
                     IngredientGroup, IngredientRelation, Menu, OpeningPeriod,
                     Quantity, Region, Store, StoreCategory, StoreHeader)


@admin.register(StoreCategory)
class StoreCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(StoreHeader)
class StoreHeaderAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'admin_ldpi',)
    readonly_fields = (
        'admin_ldpi', 'ldpi', 'mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi',
    )
    fields = ('original',) + readonly_fields

    admin_ldpi = AdminThumbnail(image_field='ldpi')


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'wait',)
    readonly_fields = ('timezone', 'latitude', 'longitude', 'hearts',)
    search_fields = ('name', 'city', 'street', 'country')
    list_filter = ('city', 'country',)
    ordering = ('name',)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'postcode',)
    search_fields = ('name', 'country', 'postcode',)
    ordering = ('country', 'name',)


class PeriodAdmin(admin.ModelAdmin):
    list_display = ('store', 'day', 'time', 'duration',)
    search_fields = ('store__name',)
    list_filter = ('day', 'store',)
    ordering = ('store__name', 'day',)


admin.site.register(OpeningPeriod, PeriodAdmin)
admin.site.register(DeliveryPeriod, PeriodAdmin)


@admin.register(HolidayPeriod)
class HolidayPeriodAdmin(admin.ModelAdmin):
    list_display = ('store', 'start', 'end', 'closed',)
    search_fields = ('store__name', 'description',)
    list_filter = ('closed', 'store',)
    ordering = ('store__name', 'start', 'end', 'closed',)


@admin.register(FoodType)
class FoodTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantifier', 'inputtype', 'customisable',)
    search_fields = ('name', 'quantifier',)
    list_filter = ('customisable', 'inputtype',)
    ordering = ('name', 'customisable',)


@admin.register(IngredientGroup)
class IngredientGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'priority', 'calculation',)
    search_fields = ('name', 'store__name',)
    list_filter = ('calculation', 'store',)
    ordering = ('store__name', 'priority', 'name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'group', 'last_modified',)
    search_fields = ('name', 'store__name', 'group__name',)
    list_filter = ('store',)
    ordering = ('store__name', 'name', 'group__name', 'last_modified',)


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'priority',)
    search_fields = ('name', 'store__name',)
    list_filter = ('store',)
    ordering = ('store__name', 'priority', 'name',)


@admin.register(Quantity)
class QuantityAdmin(admin.ModelAdmin):
    list_display = ('store', 'foodtype', 'minimum', 'maximum', 'last_modified',)
    search_fields = ('store__name', 'foodtype_name',)
    list_filter = ('store',)
    ordering = ('store__name', 'foodtype__name', 'last_modified',)


class IngredientsRelationInline(admin.TabularInline):
    model = IngredientRelation
    extra = 1
    fields = ('ingredient', 'selected',)


class FoodForm(forms.ModelForm):

    class Meta:
        model = Food
        exclude = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredientgroups'].queryset = IngredientGroup.objects.filter(
            store_id=self.instance.store_id
        )


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    form = FoodForm
    list_display = ('name', 'store', 'menu', 'priority', 'cost',)
    inlines = (IngredientsRelationInline,)
    search_fields = ('name', 'store__name', 'menu__name',)
    list_filter = ('store',)
    ordering = ('store__name', 'name', 'priority',)


class BaseTokenAdmin(admin.ModelAdmin):
    list_display = ('device',)
