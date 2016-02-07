from django.contrib import admin
from imagekit.admin import AdminThumbnail
from lunch.models import (Food, FoodCategory, FoodType, HolidayPeriod,
                          Ingredient, IngredientGroup, IngredientRelation,
                          OpeningHours, Quantity, Store, StoreCategory,
                          StoreHeader)

admin.site.register(StoreCategory)


@admin.register(Quantity)
class QuantityAdmin(admin.ModelAdmin):
    list_display = (
        'foodType',
        'store',
        'amountMin',
        'amountMax',
        'id',
    )
    readonly_fields = (
        'id',
        'lastModified',
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
        'minTime',
        'id',
    )
    readonly_fields = (
        'id',
        'latitude',
        'longitude',
        'hearts',
    )


@admin.register(OpeningHours)
class OpeningHoursAdmin(admin.ModelAdmin):
    list_display = (
        'store',
        'day',
        'opening',
        'closing',
        'id',
    )
    readonly_fields = (
        'id',
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


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
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
        'inputType',
        'id',
    )
    readonly_fields = (
        'id',
    )


class IngredientsRelationInline(admin.TabularInline):
    model = IngredientRelation
    extra = 3


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'cost',
        'category',
        'store',
        'id',
    )
    readonly_fields = (
        'lastModified',
        'id',
    )
    inlines = (IngredientsRelationInline,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'group',
        'store',
    )


@admin.register(IngredientGroup)
class IngredientGroupAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'maximum',
        'minimum',
        'priority',
        'cost',
        'foodType',
        'store',
        'id',
    )


class BaseTokenAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'device',
    )
