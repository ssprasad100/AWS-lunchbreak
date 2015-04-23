from lunch.models import (BaseToken, DefaultFood, DefaultFoodCategory,
                          DefaultIngredient, DefaultIngredientRelation, Food,
                          FoodCategory, FoodType, HolidayPeriod, Ingredient,
                          IngredientGroup, OpeningHours, Store, StoreCategory)
from rest_framework import serializers


class StoreCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreCategory
        fields = ('id', 'name', 'icon',)


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


class DefaultIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultIngredient
        fields = ('id', 'name', 'cost', 'icon', 'group',)


class IngredientSerializer(DefaultIngredientSerializer):

    class Meta:
        model = Ingredient
        fields = DefaultIngredientSerializer.Meta.fields + ('store',)


class ShortDefaultIngredientRelationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')

    class Meta:
        model = DefaultIngredientRelation
        fields = ('id', 'typical',)


class IngredientGroupSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = IngredientGroup
        fields = ('id', 'name', 'maximum', 'ingredients', 'priority',)


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
        fields = ('id', 'name', 'icon', 'quantifier', 'inputType', 'required',)


class DefaultFoodSerializer(serializers.ModelSerializer):
    ingredientGroups = IngredientGroupSerializer(many=True, read_only=True)
    category = DefaultFoodCategorySerializer(many=False)
    foodType = FoodTypeSerializer(many=False)
    ingredients = ShortDefaultIngredientRelationSerializer(source='defaultingredientrelation_set', many=True)

    class Meta:
        model = DefaultFood
        fields = ('id', 'name', 'cost', 'ingredientGroups', 'ingredients', 'category', 'foodType',)
        read_only_fields = ('id', 'ingredientGroups',)


class FoodSerializer(DefaultFoodSerializer):
    ingredients = ShortDefaultIngredientRelationSerializer(source='ingredientrelation_set', many=True)

    def create(self, validated_data):
        ingredients = Ingredient.objects.filter(id__in=validated_data['ingredients'])
        return Food(name=validated_data['name'], cost=validated_data['cost'], ingredients=ingredients, store=validated_data['store'], category=validated_data['category'], icon=validated_data['icon'])

    class Meta:
        model = Food
        fields = DefaultFoodSerializer.Meta.fields + ('store',)
        read_only_fields = DefaultFoodSerializer.Meta.read_only_fields


class ShortDefaultFoodSerializer(serializers.ModelSerializer):
    foodType = FoodTypeSerializer(many=False)
    category = DefaultFoodCategorySerializer(many=False)

    class Meta:
        model = DefaultFood
        fields = ('id', 'name', 'cost', 'category', 'foodType', 'hasIngredients',)
        read_only_fields = ('id', 'hasIngredients',)


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseToken
        fields = ('id', 'identifier', 'device',)
        read_only_fields = ('id', 'identifier', 'device',)
