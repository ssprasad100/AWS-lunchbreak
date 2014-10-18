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


class IngredientGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientGroup
        fields = ('id', 'name', 'maximum')


class DefaultIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultIngredient
        fields = ('id', 'name')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'store')


class DefaultFoodSerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultFood
        fields = ('id', 'name', 'cost', 'ingredientGroups', 'defaultIngredients')


class FoodSerializer(serializers.ModelSerializer):

    class Meta:
        model = Food
        fields = ('id', 'name', 'cost', 'ingredientGroups', 'defaultIngredients', 'store')
