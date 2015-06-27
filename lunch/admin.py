from django.contrib import admin
from lunch.models import (Food, FoodCategory, FoodType, HolidayPeriod,
                          Ingredient, IngredientGroup, IngredientRelation,
                          OpeningHours, Quantity, Store, StoreCategory)

admin.site.register(StoreCategory)

@admin.register(Quantity)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('foodType', 'store', 'amountMin', 'amountMax', 'id',)
    readonly_fields = ('id', 'lastModified',)
    fields = ('foodType', 'store', 'amountMin', 'amountMax',) + readonly_fields


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'minTime', 'id',)
    readonly_fields = ('id', 'latitude', 'longitude', 'hearts',)


@admin.register(OpeningHours)
class OpeningHoursAdmin(admin.ModelAdmin):
    list_display = ('store', 'day', 'opening', 'closing', 'id',)
    readonly_fields = ('id',)
    fields = ('store', 'day', 'opening', 'closing',) + readonly_fields


@admin.register(HolidayPeriod)
class HolidayPeriodAdmin(admin.ModelAdmin):
    list_display = ('store', 'description', 'start', 'end', 'closed', 'id',)
    readonly_fields = ('id',)
    fields = ('store', 'description', 'start', 'end', 'closed',) + readonly_fields


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'store', 'id',)
    readonly_fields = ('id',)
    fields = ('name', 'priority', 'store',) + readonly_fields


@admin.register(FoodType)
class FoodTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'quantifier', 'inputType', 'id',)
    readonly_fields = ('id',)
    fields = ('name', 'icon', 'quantifier', 'inputType',) + readonly_fields


class IngredientsRelationInline(admin.TabularInline):
    model = IngredientRelation
    extra = 3


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'category', 'store', 'id',)
    fields = list_display + ('foodType', 'lastModified',)
    readonly_fields = ('lastModified', 'id',)
    inlines = (IngredientsRelationInline,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display =('name', 'cost', 'group', 'store', 'id',)
    readonly_fields = ('id', 'lastModified',)
    fields = ('name', 'cost', 'group', 'icon', 'store',) + readonly_fields


@admin.register(IngredientGroup)
class IngredientGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'maximum', 'minimum', 'priority', 'cost', 'foodType', 'store', 'id',)
    fields = list_display
    readonly_fields = ('id',)
