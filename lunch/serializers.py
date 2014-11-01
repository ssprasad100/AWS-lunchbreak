from lunch.models import Store, DefaultFood, Food, StoreCategory, DefaultIngredient, Ingredient, IngredientGroup

from rest_framework import serializers


class StoreCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreCategory
        fields = ('id', 'name')


class StoreSerializer(serializers.ModelSerializer):
    categories = serializers.RelatedField(many=True)

    class Meta:
        model = Store
        fields = ('id', 'name', 'country', 'province', 'city', 'code', 'street', 'number', 'latitude', 'longitude', 'categories')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'store')


class ShortIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name')


class DefaultIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultIngredient
        fields = ('id', 'name')


class IngredientGroupSerializer(serializers.ModelSerializer):
    ingredients = ShortIngredientSerializer(many=True)

    class Meta:
        model = IngredientGroup
        fields = ('id', 'name', 'maximum', 'ingredients')


class DefaultFoodSerializer(serializers.ModelSerializer):
    ingredientGroups = IngredientGroupSerializer(many=True)

    class Meta:
        model = DefaultFood
        fields = ('id', 'name', 'cost', 'ingredientGroups', 'ingredients')


class FoodSerializer(serializers.ModelSerializer):
    ingredientGroups = IngredientGroupSerializer(many=True)

    class Meta:
        model = Food
        fields = ('id', 'name', 'cost', 'ingredientGroups', 'ingredients', 'store')
