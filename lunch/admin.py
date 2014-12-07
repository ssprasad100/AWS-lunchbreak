from django.contrib import admin
from lunch.models import Store, StoreCategory, DefaultFood, Food, DefaultIngredient, Ingredient, IngredientGroup, Token, User, DefaultFoodCategory, FoodCategory


admin.site.register(StoreCategory)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
	readonly_fields = ('latitude', 'longitude',)


@admin.register(DefaultFoodCategory)
class DefaultFoodCategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)
	fields = ('name',)


@admin.register(FoodCategory)
class FoodCategoryAdmin(DefaultFoodCategoryAdmin):
	list_display = ('name', 'store',)
	fields = ('name', 'store',)


@admin.register(DefaultFood)
class DefaultFoodAdmin(admin.ModelAdmin):
	list_display = ('name', 'cost', 'category',)
	fields = ('name', 'cost', 'ingredients', 'category',)
	filter_horizontal = ('ingredients',)


@admin.register(Food)
class FoodAdmin(DefaultFoodAdmin):
	list_display = ('name', 'cost', 'store', 'category',)
	fields = ('name', 'cost', 'ingredients', 'store', 'category',)


@admin.register(DefaultIngredient)
class DefaultIngredientAdmin(admin.ModelAdmin):
	list_display = ('name', 'cost', 'group',)
	fields = ('name', 'cost', 'group',)


@admin.register(Ingredient)
class IngredientAdmin(DefaultIngredientAdmin):
	list_display = ('name', 'cost', 'group', 'store')
	fields = ('name', 'cost', 'group', 'store')


@admin.register(IngredientGroup)
class IngredientGroupAdmin(admin.ModelAdmin):
	list_display = ('name', 'maximum',)
	fields = ('name', 'maximum',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ('phone', 'name', 'userId', 'requestId', 'confirmed', 'confirmedAt',)
	fields = ('phone', 'name', 'userId', 'requestId', 'confirmed', 'confirmedAt',)


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
	list_display = ('identifier', 'device', 'user',)
	fields = ('identifier', 'device', 'user',)
