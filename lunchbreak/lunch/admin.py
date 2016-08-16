from django import forms
from django.contrib import admin
from imagekit.admin import AdminThumbnail

from .models import (Food, FoodType, HolidayPeriod, Ingredient,
                     IngredientGroup, IngredientRelation, Menu, OpeningPeriod,
                     Quantity, Region, Store, StoreCategory, StoreHeader)

admin.site.register(StoreCategory)
admin.site.register(Region)


@admin.register(Quantity)
class QuantityAdmin(admin.ModelAdmin):
    list_display = (
        'foodtype',
        'store',
        'min',
        'max',
        'id',
    )
    readonly_fields = (
        'id',
        'last_modified',
    )


@admin.register(StoreHeader)
class StoreHeaderAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'admin_ldpi',
    )
    admin_ldpi = AdminThumbnail(image_field='ldpi')
    readonly_fields = (
        'admin_ldpi',
        'ldpi',
        'mdpi',
        'hdpi',
        'xhdpi',
        'xxhdpi',
        'xxxhdpi',
    )
    fields = (
        'original',
    ) + readonly_fields


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'city',
        'country',
        'wait',
        'id',
    )
    readonly_fields = (
        'id',
        'latitude',
        'longitude',
        'hearts',
    )


@admin.register(OpeningPeriod)
class OpeningPeriodAdmin(admin.ModelAdmin):
    list_display = (
        'store',
        'day',
        'time',
        'duration',
        'id',
    )
    readonly_fields = (
        'id',
        'start',
    )


@admin.register(HolidayPeriod)
class HolidayPeriodAdmin(admin.ModelAdmin):
    list_display = (
        'store',
        'description',
        'start',
        'end',
        'closed',
        'id',
    )
    readonly_fields = (
        'id',
    )


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'priority',
        'store',
        'id',
    )
    readonly_fields = (
        'id',
    )


@admin.register(FoodType)
class FoodTypeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'quantifier',
        'inputtype',
        'id',
    )
    readonly_fields = (
        'id',
    )


class IngredientsRelationInline(admin.TabularInline):
    model = IngredientRelation
    extra = 1
    fields = ['ingredient']

class FoodForm(forms.ModelForm):

    class Meta:
        model = Food
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredientgroups'].queryset = IngredientGroup.objects.filter(
            store_id=self.instance.store_id
        )

    def get_queryset(self, request):
        print(self)


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    form = FoodForm
    list_display = (
        'name',
        'cost',
        'menu',
        'store',
        'id',
    )
    readonly_fields = (
        'last_modified',
        'id',
    )
    inlines = (IngredientsRelationInline,)
    list_filter = [
        'store'
    ]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'group',
        'store',
        'id',
    )


@admin.register(IngredientGroup)
class IngredientGroupAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'maximum',
        'minimum',
        'priority',
        'cost',
        'foodtype',
        'store',
        'id',
    )


class BaseTokenAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'device',
    )
