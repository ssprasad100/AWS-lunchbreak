from django.contrib import admin
from lunch.models import Store, StoreCategory, DefaultFood, Food, DefaultIngredient, Ingredient, IngredientGroup, DefaultFoodCategory, FoodCategory, FoodType, OpeningHours, HolidayPeriod


admin.site.register(StoreCategory)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
	list_display = ('name', 'city', 'country', 'minTime')
	readonly_fields = ('latitude', 'longitude',)


@admin.register(OpeningHours)
class OpeningHoursAdmin(admin.ModelAdmin):
	list_display = ('store', 'day', 'opening', 'closing',)
	fields = ('store', 'day', 'opening', 'closing',)


@admin.register(HolidayPeriod)
class HolidayPeriodAdmin(admin.ModelAdmin):
	list_display = ('store', 'description', 'start', 'end', 'closed',)
	fields = ('store', 'description', 'start', 'end', 'closed',)


@admin.register(DefaultFoodCategory)
class DefaultFoodCategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'priority',)
	fields = ('name', 'priority',)


@admin.register(FoodCategory)
class FoodCategoryAdmin(DefaultFoodCategoryAdmin):
	list_display = DefaultFoodCategoryAdmin.list_display + ('store',)
	fields = DefaultFoodCategoryAdmin.fields + ('store',)


@admin.register(FoodType)
class FoodTypeAdmin(admin.ModelAdmin):
	list_display = ('name', 'icon', 'quantifier', 'inputType',)
	fields = ('name', 'icon', 'quantifier', 'inputType',)


@admin.register(DefaultFood)
class DefaultFoodAdmin(admin.ModelAdmin):
	list_display = ('name', 'cost', 'category',)
	fields = ('name', 'cost', 'ingredients', 'category', 'foodType',)
	filter_horizontal = ('ingredients',)


@admin.register(Food)
class FoodAdmin(DefaultFoodAdmin):
	list_display = ('name', 'cost', 'store', 'category',)
	fields = ('name', 'cost', 'ingredients', 'store', 'category', 'foodType',)


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
