from lunch.models import (BaseToken, Food, FoodCategory, FoodType,
                          HolidayPeriod, Ingredient, IngredientGroup,
                          IngredientRelation, OpeningHours, Quantity, Store,
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
        fields = ('id', 'name', 'city', 'street', 'latitude', 'longitude', 'categories', 'heartsCount', 'lastModified',)
        read_only_fields = fields


class StoreSerializer(ShortStoreSerializer):
    categories = StoreCategorySerializer(many=True, read_only=True)

    class Meta:
        model = ShortStoreSerializer.Meta.model
        fields = ShortStoreSerializer.Meta.fields + ('country', 'province', 'city', 'postcode', 'street', 'number', 'minTime', 'orderTime',)
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


# Only here for RAML (atm)
class HoursSerializer(serializers.Serializer):
    holidayPeriods = HolidayPeriodSerializer(many=True, read_only=True)
    openingHours = OpeningHoursSerializer(many=True, read_only=True)

    class Meta:
        fields = ('holidayPeriods', 'openingHours',)
        read_only_fields = fields


class NestedIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'cost', 'icon', 'alwaysVisible', 'store',)
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


class ShortQuantitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Quantity
        fields = ('id', 'amountMin', 'amountMax', 'lastModified',)
        read_only_fields = ('id', 'lastModified',)


class QuantitySerializer(ShortQuantitySerializer):

    class Meta:
        model = ShortQuantitySerializer.Meta.model
        fields = ShortQuantitySerializer.Meta.fields + ('foodType',)
        read_only_fields = ShortQuantitySerializer.Meta.read_only_fields


class SingleFoodSerializer(serializers.ModelSerializer):
    ingredientGroups = IngredientGroupSerializer(many=True, read_only=True)
    category = ShortFoodCategorySerializer(many=False)
    foodType = FoodTypeSerializer(many=False)
    ingredients = ShortIngredientRelationSerializer(source='ingredientrelation_set', many=True)
    quantity = ShortQuantitySerializer(many=False)

    class Meta:
        model = Food
        fields = (
            'id',
            'name',
            'description',
            'amount',
            'cost',
            'foodType',
            'minDays',
            'canComment',
            'priority',

            'category',
            'ingredients',
            'store',

            'lastModified',
            # 'deleted',

            'ingredientGroups',
            'quantity',
        )
        read_only_fields = (
            'id',
            'ingredientGroups',
            'lastModified',
        )


class MultiFoodSerializer(serializers.ModelSerializer):
    foodType = FoodTypeSerializer(many=False)
    category = ShortFoodCategorySerializer(many=False)
    quantity = ShortQuantitySerializer(many=False)

    class Meta:
        model = Food
        fields = ('id', 'name', 'amount', 'cost', 'category', 'foodType', 'priority', 'hasIngredients', 'quantity', 'minDays',)
        read_only_fields = ('id', 'hasIngredients',)


class TokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseToken
        fields = ('id', 'identifier', 'device', 'service', 'registration_id', 'active',)
        read_only_fields = ('id', 'identifier', 'device', 'service', 'registration_id', 'active',)
