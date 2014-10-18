from django.contrib import admin
from lunch.models import Store, StoreCategory, DefaultFood, Food, DefaultIngredient, Ingredient, IngredientGroup

admin.site.register(Store)
admin.site.register(StoreCategory)

admin.site.register(DefaultFood)
admin.site.register(Food)

admin.site.register(DefaultIngredient)
admin.site.register(Ingredient)

admin.site.register(IngredientGroup)
