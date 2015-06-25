from django.contrib import admin
from lunch.models import (DefaultFood, DefaultFoodCategory, DefaultIngredient,
                          DefaultIngredientGroup, DefaultIngredientRelation,
                          Food, FoodCategory, FoodType, HolidayPeriod,
                          Ingredient, IngredientGroup, IngredientRelation,
                          OpeningHours, Store, StoreCategory)

admin.site.register(StoreCategory)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'minTime', 'id',)
    readonly_fields = ('id', 'latitude', 'longitude', 'hearts',)


@admin.register(OpeningHours)
class OpeningHoursAdmin(admin.ModelAdmin):
    list_display = ('store', 'day', 'opening', 'closing', 'id',)
    fields = ('store', 'day', 'opening', 'closing', 'id',)
    readonly_fields = ('id',)


@admin.register(HolidayPeriod)
class HolidayPeriodAdmin(admin.ModelAdmin):
    list_display = ('store', 'description', 'start', 'end', 'closed', 'id',)
    fields = ('store', 'description', 'start', 'end', 'closed', 'id',)
    readonly_fields = ('id',)


@admin.register(DefaultFoodCategory)
class DefaultFoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'id',)
    fields = ('id', 'name', 'priority',)
    readonly_fields = ('id',)


@admin.register(FoodCategory)
class FoodCategoryAdmin(DefaultFoodCategoryAdmin):
    list_display = DefaultFoodCategoryAdmin.list_display + ('store',)
    fields = DefaultFoodCategoryAdmin.fields + ('store',)


@admin.register(FoodType)
class FoodTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'quantifier', 'inputType', 'id',)
    fields = ('name', 'icon', 'quantifier', 'inputType', 'id',)
    readonly_fields = ('id',)


class DefaultIngredientsRelationInline(admin.TabularInline):
    model = DefaultIngredientRelation
    extra = 3


class IngredientsRelationInline(DefaultIngredientsRelationInline):
    model = IngredientRelation


@admin.register(DefaultFood)
class DefaultFoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'category', 'id',)
    fields = list_display + ('foodType', 'lastModified',)
    readonly_fields = ('lastModified', 'id',)
    inlines = (DefaultIngredientsRelationInline,)


@admin.register(Food)
class FoodAdmin(DefaultFoodAdmin):
    list_display = DefaultFoodAdmin.list_display + ('store',)
    fields = DefaultFoodAdmin.fields + ('store',)
    inlines = (IngredientsRelationInline,)


@admin.register(DefaultIngredient)
class DefaultIngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'group', 'id',)
    readonly_fields = ('id', 'lastModified',)
    fields = ('name', 'cost', 'group', 'icon',) + readonly_fields


@admin.register(Ingredient)
class IngredientAdmin(DefaultIngredientAdmin):
    list_display = DefaultIngredientAdmin.list_display + ('store',)
    fields = DefaultIngredientAdmin.fields + ('store',)


@admin.register(DefaultIngredientGroup)
class DefaultIngredientGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'maximum', 'minimum', 'priority', 'cost', 'foodType', 'id',)
    fields = list_display
    readonly_fields = ('id',)


@admin.register(IngredientGroup)
class IngredientGroupAdmin(admin.ModelAdmin):
    list_display = DefaultIngredientGroupAdmin.list_display + ('store',)
    fields = list_display
    readonly_fields = ('id',)
