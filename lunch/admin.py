from django.contrib import admin
from lunch.models import Store, StoreCategory, Food, Ingredient, IngredientGroup, IngredientGroupName

admin.site.register(Store)
admin.site.register(StoreCategory)

admin.site.register(Food)

admin.site.register(Ingredient)
admin.site.register(IngredientGroup)
admin.site.register(IngredientGroupName)
