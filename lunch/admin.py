from django.contrib import admin
from lunch.models import Store, StoreCategory, DefaultFood, Food, DefaultIngredient, Ingredient, IngredientGroup, Token, User, DefaultFoodCategory, FoodCategory, Icon, Order, OrderedFood


admin.site.register(StoreCategory)


@admin.register(Icon)
class IconAdmin(admin.ModelAdmin):
	list_display = ('iconId', 'description',)
	fields = ('iconId', 'description',)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
	list_display = ('name', 'city', 'country',)
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
	fields = ('name', 'cost', 'ingredients', 'category', 'icon',)
	filter_horizontal = ('ingredients',)


@admin.register(Food)
class FoodAdmin(DefaultFoodAdmin):
	list_display = ('name', 'cost', 'store', 'category',)
	fields = ('name', 'cost', 'ingredients', 'store', 'category', 'icon',)


@admin.register(OrderedFood)
class OrderedFoodAdmin(FoodAdmin):
	list_display = FoodAdmin.list_display + ('amount',)
	fields = FoodAdmin.fields + ('amount',)


@admin.register(DefaultIngredient)
class DefaultIngredientAdmin(admin.ModelAdmin):
	list_display = ('name', 'cost', 'group',)
	fields = ('name', 'cost', 'group', 'icon',)


@admin.register(Ingredient)
class IngredientAdmin(DefaultIngredientAdmin):
	list_display = ('name', 'cost', 'group', 'store',)
	fields = ('name', 'cost', 'group', 'store', 'icon',)


@admin.register(IngredientGroup)
class IngredientGroupAdmin(admin.ModelAdmin):
	list_display = ('name', 'maximum',)
	fields = ('name', 'maximum',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ('phone', 'name', 'userId', 'requestId', 'confirmedAt',)
	fields = ('phone', 'name', 'userId', 'requestId', 'confirmedAt',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('user', 'store', 'orderedTime', 'pickupTime', 'status', 'paid',)
	fields = ('user', 'store', 'pickupTime', 'status', 'paid', 'food',)
	readonly_fields = ('orderedTime',)


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
	list_display = ('identifier', 'device', 'user',)
	fields = ('identifier', 'device', 'user',)
