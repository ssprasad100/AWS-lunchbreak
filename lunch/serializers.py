from lunch.models import (DefaultFood, DefaultFoodCategory, DefaultIngredient,
                          Food, FoodCategory, FoodType, HolidayPeriod,
                          Ingredient, IngredientGroup, OpeningHours, Store,
                          StoreCategory)
from rest_framework import serializers


class StoreCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreCategory
        fields = ('id', 'name',)


class StoreSerializer(serializers.ModelSerializer):
    categories = StoreCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Store
        fields = ('id', 'name', 'country', 'province', 'city', 'postcode', 'street', 'number', 'latitude', 'longitude', 'categories', 'minTime',)


class OpeningHoursSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningHours
        fields = ('id', 'day', 'opening', 'closing',)


class HolidayPeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = HolidayPeriod
        fields = ('id', 'description', 'start', 'end', 'closed',)


class ShortIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'cost',)


class DefaultIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultIngredient
        fields = ('id', 'name', 'cost', 'icon',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'store', 'icon',)


class IngredientGroupSerializer(serializers.ModelSerializer):
    ingredients = ShortIngredientSerializer(many=True)

    class Meta:
        model = IngredientGroup
        fields = ('id', 'name', 'maximum', 'ingredients',)


class DefaultFoodCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultFoodCategory
        fields = ('id', 'name', 'priority',)


class FoodCategorySerializer(DefaultFoodCategorySerializer):

    class Meta:
        model = FoodCategory
        fields = DefaultFoodCategorySerializer.Meta.fields + ('store',)


class FoodTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodType
        fields = ('name', 'icon', 'quantifier', 'inputType',)


class DefaultFoodSerializer(serializers.ModelSerializer):
    ingredientGroups = IngredientGroupSerializer(many=True)
    category = DefaultFoodCategorySerializer(many=False)
    foodType = FoodTypeSerializer(many=False)

    class Meta:
        model = DefaultFood
        fields = ('id', 'name', 'cost', 'ingredientGroups', 'ingredients', 'category', 'foodType',)


class FoodSerializer(serializers.ModelSerializer):
    ingredientGroups = IngredientGroupSerializer(many=True, read_only=True)
    category = FoodCategorySerializer(many=False)
    foodType = FoodTypeSerializer(many=False)

    def create(self, validated_data):
        ingredients = Ingredient.objects.filter(id__in=validated_data['ingredients'])
        return Food(name=validated_data['name'], cost=validated_data['cost'], ingredients=ingredients, store=validated_data['store'], category=validated_data['category'], icon=validated_data['icon'])

    class Meta:
        model = Food
        fields = ('id', 'name', 'cost', 'ingredientGroups', 'ingredients', 'store', 'category', 'foodType',)
        read_only_fields = ('id', 'ingredientGroups',)
