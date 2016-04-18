from rest_framework import serializers

from .models import (BaseToken, Food, FoodCategory, FoodType, HolidayPeriod,
                     Ingredient, IngredientGroup, IngredientRelation,
                     OpeningPeriod, Quantity, Store, StoreCategory)


class StoreCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreCategory
        fields = (
            'id',
            'name',
            'icon',
        )
        read_only_fields = (
            'id',
        )


class ShortStoreSerializer(serializers.ModelSerializer):
    categories = StoreCategorySerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Store
        fields = (
            'id',
            'name',
            'city',
            'street',
            'latitude',
            'longitude',
            'categories',
            'hearts_count',
            'last_modified',
        )
        read_only_fields = fields


class StoreSerializer(ShortStoreSerializer):
    categories = StoreCategorySerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = ShortStoreSerializer.Meta.model
        fields = ShortStoreSerializer.Meta.fields + (
            'country',
            'province',
            'city',
            'postcode',
            'street',
            'number',
            'wait',
            'preorder_time',
        )
        read_only_fields = ShortStoreSerializer.Meta.read_only_fields


class OpeningPeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningPeriod
        fields = (
            'id',
            'opening_day',
            'closing_day',
            'opening_time',
            'closing_time',
        )
        read_only_fields = (
            'id',
        )


class HolidayPeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = HolidayPeriod
        fields = (
            'id',
            'description',
            'start',
            'end',
            'closed',
        )


# Only here for RAML (atm)
class HoursSerializer(serializers.Serializer):
    holidayperiods = HolidayPeriodSerializer(
        many=True,
        read_only=True
    )
    openingperiods = OpeningPeriodSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        fields = (
            'holidayperiods',
            'openingperiods',
        )
        read_only_fields = fields


class NestedIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'cost',
            'group',
        )
        read_only_fields = (
            'id',
        )


class IngredientRelationSerializer(serializers.HyperlinkedModelSerializer):
    ingredient = NestedIngredientSerializer()

    class Meta:
        model = IngredientRelation
        fields = (
            'selected',
            'ingredient',
        )


class ShortIngredientRelationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )

    class Meta:
        model = IngredientRelation
        fields = (
            'id',
            'selected',
        )
        read_only_fields = (
            'id',
        )


class ShortIngredientGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientGroup
        fields = (
            'id',
            'name',
            'maximum',
            'minimum',
            'priority',
            'cost',
            'foodtype',
        )
        read_only_fields = (
            'id',
        )


class IngredientGroupSerializer(ShortIngredientGroupSerializer):
    ingredients = NestedIngredientSerializer(
        many=True
    )

    class Meta:
        model = ShortIngredientGroupSerializer.Meta.model
        fields = ShortIngredientGroupSerializer.Meta.fields + (
            'ingredients',
        )
        read_only_fields = ShortIngredientGroupSerializer.Meta.read_only_fields


class ShortFoodCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodCategory
        fields = (
            'id',
            'name',
            'priority',
        )
        read_only_fields = (
            'id',
        )


class FoodCategorySerializer(ShortFoodCategorySerializer):

    class Meta:
        model = FoodCategory
        fields = ShortFoodCategorySerializer.Meta.fields + (
            'store',
        )
        read_only_fields = ShortFoodCategorySerializer.Meta.read_only_fields


class FoodTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodType
        fields = (
            'id',
            'name',
            'quantifier',
            'inputtype',
            'customisable',
        )
        read_only_fields = (
            'id',
        )


class ShortQuantitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Quantity
        fields = (
            'id',
            'min',
            'max',
            'last_modified',
        )
        read_only_fields = (
            'id',
            'last_modified',
        )


class QuantitySerializer(ShortQuantitySerializer):

    class Meta:
        model = ShortQuantitySerializer.Meta.model
        fields = ShortQuantitySerializer.Meta.fields + (
            'foodtype',
        )
        read_only_fields = ShortQuantitySerializer.Meta.read_only_fields


class SingleFoodSerializer(serializers.ModelSerializer):
    ingredientgroups = ShortIngredientGroupSerializer(
        many=True,
        read_only=True
    )
    category = ShortFoodCategorySerializer(
        many=False
    )
    foodtype = FoodTypeSerializer(
        many=False
    )
    ingredients = IngredientRelationSerializer(
        source='ingredientrelation_set',
        many=True
    )
    quantity = ShortQuantitySerializer(
        many=False
    )

    class Meta:
        model = Food
        fields = (
            'id',
            'name',
            'description',
            'amount',
            'cost',
            'foodtype',
            'preorder_days',
            'commentable',
            'priority',

            'category',
            'ingredients',
            'store',

            'last_modified',

            'ingredientgroups',
            'quantity',
        )
        read_only_fields = (
            'id',
            'ingredientgroups',
            'last_modified',
        )

    def to_representation(self, obj):
        result = super(SingleFoodSerializer, self).to_representation(obj)

        ingredientrelations_added = []
        ingredientgroups = obj.ingredientgroups.all().prefetch_related(
            'ingredient_set'
        )
        obj_ingredients = obj.ingredients.all()

        for ingredientgroup in ingredientgroups:
            ingredients = ingredientgroup.ingredient_set.all()
            for ingredient in ingredients:
                if ingredient not in obj_ingredients:
                    ingredientrelations_added.append(
                        IngredientRelation(ingredient=ingredient)
                    )

        serializer = IngredientRelationSerializer(
            many=True
        )
        relation_representation = serializer.to_representation(ingredientrelations_added)

        result['ingredients'] += relation_representation

        return result


class MultiFoodSerializer(serializers.ModelSerializer):
    foodtype = FoodTypeSerializer(
        many=False
    )
    category = ShortFoodCategorySerializer(
        many=False
    )
    quantity = ShortQuantitySerializer(
        many=False
    )

    class Meta:
        model = Food
        fields = (
            'id',
            'name',
            'amount',
            'cost',
            'category',
            'foodtype',
            'priority',
            'has_ingredients',
            'quantity',
            'preorder_days',
        )
        read_only_fields = (
            'id',
            'has_ingredients',
        )


class MultiTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = BaseToken
        fields = (
            'id',
            'device',
            'service',
            'registration_id',
            'active',
        )
        read_only_fields = (
            'id',
            'identifier',
            'device',
            'service',
            'active',
        )


class TokenSerializer(MultiTokenSerializer):

    class Meta:
        model = MultiTokenSerializer.Meta.model
        fields = MultiTokenSerializer.Meta.fields + (
            'identifier',
        )
        read_only_fields = MultiTokenSerializer.Meta.read_only_fields + (
            'identifier',
        )
