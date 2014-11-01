from django.contrib import admin
from lunch.models import Store, StoreCategory, DefaultFood, Food, DefaultIngredient, Ingredient, IngredientGroup


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    readonly_fields = ('latitude', 'longitude',)


admin.site.register(StoreCategory)


@admin.register(DefaultFood)
class DefaultFoodAdmin(admin.ModelAdmin):
    fields = ('name', 'cost', 'ingredients',)
    filter_horizontal = ('ingredients',)


@admin.register(Food)
class FoodAdmin(DefaultFoodAdmin):
    fields = ('name', 'cost', 'ingredients', 'store',)

admin.site.register(DefaultIngredient)
admin.site.register(Ingredient)

admin.site.register(IngredientGroup)
