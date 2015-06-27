from lunch.models import (BaseToken, Food, FoodCategory, FoodType,
                          HolidayPeriod, Ingredient, IngredientGroup,
                          IngredientRelation, OpeningHours, Store,
                          StoreCategory)
from rest_framework import serializers


class StoreCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreCategory
        fields = ('id', 'name', 'icon',)
        read_only_fields = ('id',)


class ShortStoreSerializer(serializers.ModelSerializer):
    categories = StoreCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Store
        fields = ('id', 'name', 'city', 'street', 'latitude', 'longitude', 'categories', 'heartsCount',)
        read_only_fields = fields


class StoreSerializer(ShortStoreSerializer):
    categories = StoreCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Store
        fields = ShortStoreSerializer.Meta.fields + ('country', 'province', 'city', 'postcode', 'street', 'number', 'minTime',)
        read_only_fields = ShortStoreSerializer.Meta.read_only_fields


class OpeningHoursSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningHours
        fields = ('id', 'day', 'opening', 'closing',)
        read_only_fields = ('id',)


class HolidayPeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = HolidayPeriod
        fields = ('id', 'description', 'start', 'end', 'closed',)


class NestedIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'cost', 'icon', 'store',)
        read_only_fields = ('id',)


class ShortIngredientRelationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')

    class Meta:
        model = IngredientRelation
        fields = ('id', 'typical',)
        read_only_fields = ('id',)


class IngredientGroupSerializer(serializers.ModelSerializer):
    ingredients = NestedIngredientSerializer(many=True)

    class Meta:
        model = IngredientGroup
        fields = ('id', 'name', 'maximum', 'minimum', 'ingredients', 'priority', 'cost', 'foodType',)
        read_only_fields = ('id',)


class ShortFoodCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodCategory
        fields = ('id', 'name', 'priority',)
        read_only_fields = ('id',)


class FoodCategorySerializer(ShortFoodCategorySerializer):

    class Meta:
        model = FoodCategory
        fields = ShortFoodCategorySerializer.Meta.fields + ('store',)
        read_only_fields = ShortFoodCategorySerializer.Meta.read_only_fields


class FoodTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodType
        fields = ('id', 'name', 'icon', 'quantifier', 'inputType',)
        read_only_fields = ('id',)


class ShortSingleFoodSerializer(serializers.ModelSerializer):
    ingredientGroups = IngredientGroupSerializer(many=True, read_only=True)
    category = ShortFoodCategorySerializer(many=False)
    foodType = FoodTypeSerializer(many=False)
    ingredients = ShortIngredientRelationSerializer(source='ingredientrelation_set', many=True)

    def create(self, validated_data):
        ingredients = Ingredient.objects.filter(id__in=validated_data['ingredients'])
        return Food(name=validated_data['name'], cost=validated_data['cost'], ingredients=ingredients, store=validated_data['store'], category=validated_data['category'], icon=validated_data['icon'])

    class Meta:
        model = Food
        fields = ('id', 'name', 'description', 'cost', 'ingredientGroups', 'ingredients', 'category', 'foodType', 'store',)
        read_only_fields = ('id', 'ingredientGroups',)


class SingleFoodSerializer(ShortSingleFoodSerializer):

    class Meta:
        model = ShortSingleFoodSerializer.Meta.model
        fields = ShortSingleFoodSerializer.Meta.fields + ('store',)
        read_only_fields = ShortSingleFoodSerializer.Meta.read_only_fields


class MultiFoodSerializer(serializers.ModelSerializer):
    foodType = FoodTypeSerializer(many=False)
    category = ShortFoodCategorySerializer(many=False)

    class Meta:
        model = Food
        fields = ('id', 'name', 'cost', 'category', 'foodType', 'hasIngredients',)
        read_only_fields = ('id', 'hasIngredients',)


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseToken
        fields = ('id', 'identifier', 'device',)
        read_only_fields = ('id', 'identifier', 'device',)
