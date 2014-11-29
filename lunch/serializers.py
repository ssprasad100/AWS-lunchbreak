from lunch.models import Store, DefaultFood, Food, StoreCategory, DefaultIngredient, Ingredient, IngredientGroup, User, Token

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
        fields = ('id', 'name', 'cost')


class DefaultIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultIngredient
        fields = ('id', 'name', 'cost')


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


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Token
        fields = ('id', 'identifier', 'device', 'digitsId')
        write_only_fields = ('device', 'digitsId')


class UserSerializer(serializers.ModelSerializer):
    device = serializers.CharField('device', label='device', write_only=True, required=True)

    class Meta:
        model = User
        fields = ('name', 'phone', 'device')
        write_only_fields = ('name', 'phone')


class UserConfirmationSerializer(serializers.ModelSerializer):
    requestId = serializers.CharField('requestId', label='requestId', write_only=True, required=True)
    pin = serializers.CharField('pin', label='pin', write_only=True, required=True)

    class Meta:
        model = User
        fields = ('digitsId', 'requestId', 'pin')
