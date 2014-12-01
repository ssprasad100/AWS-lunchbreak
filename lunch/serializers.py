from lunch.models import Store, DefaultFood, Food, StoreCategory, DefaultIngredient, Ingredient, IngredientGroup, User, Token

from rest_framework import serializers


class StoreCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreCategory
        fields = ('id', 'name')


class StoreSerializer(serializers.ModelSerializer):
    categories = serializers.RelatedField(many=True, read_only=True)

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


class UserSerializer(serializers.ModelSerializer):
    pin = serializers.CharField()
    device = serializers.CharField()

    def to_internal_value(self, data):
        name = data.get('name')
        phone = data.get('phone')

        if not name:
            raise serializers.ValidationError({
                'name': 'This field is required'
            })

        if not phone:
            raise serializers.ValidationError({
                'phone': 'This field is required'
            })

        print name
        print phone
        # TODO Check whether the phone number is a valid phone number
        return {
            'name': name,
            'phone': phone
        }

    class Meta:
        model = User
        fields = ('name', 'phone', 'pin', 'device')
        write_only_fields = ('name', 'phone', 'pin', 'device')


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Token
        fields = ('id', 'identifier', 'device')
        read_only_fields = ('id', 'identifier')
