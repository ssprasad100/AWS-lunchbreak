from lunch.models import Store, Food, StoreCategory, Ingredient, IngredientGroup

from rest_framework import serializers


class StoreSerializer(serializers.ModelSerializer):
    categories = serializers.RelatedField(many=True)

    class Meta:
        model = Store
        fields = ('id', 'name', 'country', 'province', 'city', 'code', 'street', 'number', 'latitude', 'longitude', 'categories')


class StoreCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreCategory
        fields = ('id', 'name')


class FoodSerializer(serializers.ModelSerializer):

    class Meta:
        model = Food
        fields = ('id', 'name', 'cost', 'store', 'ingredientGroups')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name')


class IngredientGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientGroup
        fields = ('id', 'name', 'maximum', 'ingredients')
