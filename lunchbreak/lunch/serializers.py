from Lunchbreak.serializers import RequestAttributeDefault
from rest_framework import serializers
from versioning_prime.mixins import VersionedMixin

from .fields import CurrentUserAttributeDefault
from .models import (BaseToken, Food, FoodType, HolidayPeriod, Ingredient,
                     IngredientGroup, IngredientRelation, Menu, OpeningPeriod,
                     Quantity, Store, StoreCategory)


class StoreCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreCategory
        fields = (
            'id',
            'name',
        )
        read_only_fields = (
            'id',
        )


class StoreSerializer(VersionedMixin, serializers.ModelSerializer):
    hearted = serializers.BooleanField(
        default=False
    )
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
            'gocardless_enabled',
            'payconiq_enabled',
            'cash_enabled',
            'groups_only',
            'hearted',
        )
        read_only_fields = (
            'id',
            'latitude',
            'longitude',
            'hearts_count',
            'last_modified',
            'gocardless_enabled',
            'payconiq_enabled',
            'cash_enabled',
            'hearted',
        )

    def to_representation(self, value):
        value = super().to_representation(value)

        if 'request' in self.context and hasattr(self.context['request'], 'user'):
            user = self.context['request'].user

            if user.cash_enabled_forced:
                value['cash_enabled'] = True

        return value


class StoreDetailSerializer(StoreSerializer):
    categories = StoreCategorySerializer(
        many=True,
        read_only=True
    )

    class Meta(StoreSerializer.Meta):
        fields = StoreSerializer.Meta.fields + (
            'country',
            'province',
            'city',
            'postcode',
            'street',
            'number',
            'wait',
        )


class OpeningPeriodSerializer(serializers.ModelSerializer):
    store = serializers.HiddenField(
        write_only=True,
        default=serializers.CreateOnlyDefault(
            RequestAttributeDefault(
                attribute='user.staff.store'
            )
        )
    )

    class Meta:
        model = OpeningPeriod
        fields = (
            'id',
            'day',
            'time',
            'duration',
            'store',
        )
        read_only_fields = (
            'id',
        )


class HolidayPeriodSerializer(serializers.ModelSerializer):
    store = serializers.HiddenField(
        write_only=True,
        default=serializers.CreateOnlyDefault(
            RequestAttributeDefault(
                attribute='user.staff.store'
            )
        )
    )

    class Meta:
        model = HolidayPeriod
        fields = (
            'id',
            'description',
            'start',
            'end',
            'closed',
            'store',
        )
        read_only_fields = (
            'id',
        )


class IngredientSerializer(serializers.ModelSerializer):

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


class IngredientDetailSerializer(IngredientSerializer):

    class Meta(IngredientSerializer.Meta):
        fields = IngredientSerializer.Meta.fields + (
            'last_modified',
        )
        read_only_fields = IngredientSerializer.Meta.read_only_fields + (
            'last_modified',
        )


class IngredientRelationSerializer(serializers.HyperlinkedModelSerializer):
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


class IngredientRelationDetailSerializer(serializers.HyperlinkedModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = IngredientRelation
        fields = (
            'selected',
            'ingredient',
        )


class IngredientGroupSerializer(serializers.ModelSerializer):

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
            'calculation',
        )
        read_only_fields = (
            'id',
        )


class IngredientGroupDetailSerializer(IngredientGroupSerializer):
    ingredients = IngredientSerializer(
        many=True
    )

    class Meta(IngredientGroupSerializer.Meta):
        fields = IngredientGroupSerializer.Meta.fields + (
            'ingredients',
        )


class MenuSerializer(serializers.ModelSerializer):
    store = serializers.ModelField(
        model_field=Menu()._meta.get_field('store'),
        write_only=True,
        default=serializers.CreateOnlyDefault(
            CurrentUserAttributeDefault('staff.store')
        )
    )

    class Meta:
        model = Menu
        fields = (
            'id',
            'name',
            'priority',
            'store',
        )
        read_only_fields = (
            'id',
        )


class MenuDetailSerializer(MenuSerializer):
    store = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta(MenuSerializer.Meta):
        pass


class FoodTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodType
        fields = (
            'id',
            'name',
            'quantifier',
            'inputtype',
            'store',

            'wait',
            'preorder_time',
            'preorder_days',
        )
        read_only_fields = (
            'id',
        )


class QuantitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Quantity
        fields = (
            'id',
            'minimum',
            'maximum',
            'last_modified',
        )
        read_only_fields = (
            'id',
            'last_modified',
        )


class QuantityDetailSerializer(QuantitySerializer):

    class Meta:
        model = QuantitySerializer.Meta.model
        fields = QuantitySerializer.Meta.fields + (
            'foodtype',
        )
        read_only_fields = QuantitySerializer.Meta.read_only_fields


class BaseFoodSerializer(VersionedMixin, serializers.ModelSerializer):
    """This serializer is not meant to be returned!"""

    foodtype = FoodTypeSerializer(
        many=False
    )
    menu = MenuSerializer(
        many=False
    )
    quantity = QuantitySerializer(
        many=False
    )
    store = serializers.PrimaryKeyRelatedField(
        read_only=True,
        source='menu.store'
    )

    class Meta:
        model = Food
        fields = (
            'id',
            'name',
            'amount',
            'cost',
            'menu',
            'foodtype',
            'priority',
            'has_ingredients',
            'quantity',
            'wait',
            'preorder_time',
            'preorder_days',
            'preorder_disabled',
        )
        read_only_fields = (
            'id',
            'has_ingredients',
        )


class FoodSerializer(BaseFoodSerializer):

    class Meta(BaseFoodSerializer.Meta):
        fields = BaseFoodSerializer.Meta.fields + (
            'has_ingredients',
        )
        read_only_fields = BaseFoodSerializer.Meta.read_only_fields + (
            'has_ingredients',
        )


class FoodDetailSerializer(BaseFoodSerializer):
    ingredients = IngredientRelationDetailSerializer(
        source='ingredientrelations',
        many=True
    )

    class Meta(BaseFoodSerializer.Meta):
        fields = BaseFoodSerializer.Meta.fields + (
            'description',
            'commentable',
            'ingredients',
            'store',
            'last_modified',
            # 'ingredientgroups', see to_representation
        )
        read_only_fields = BaseFoodSerializer.Meta.read_only_fields + (
            # 'ingredientgroups', see to_representation
            'last_modified',
        )

    def to_representation(self, obj):
        result = super().to_representation(obj)

        # Add ingredientgroup ingredients to Food.ingredients representation
        ingredientrelations_added = []
        ingredientgroups = obj.ingredientgroups.filter(
            # Do not include empty groups
            ingredients__isnull=False
        ).prefetch_related(
            'ingredients'
        ).distinct()
        ingredients = obj.ingredients.all().select_related(
            'group'
        )

        for ingredientgroup in ingredientgroups:
            group_ingredients = ingredientgroup.ingredients.all()
            for ingredient in group_ingredients:
                if ingredient not in ingredients:
                    ingredientrelations_added.append(
                        IngredientRelation(
                            ingredient=ingredient
                        )
                    )

        result['ingredients'] += IngredientRelationDetailSerializer(
            many=True,
            context=self.context
        ).to_representation(
            ingredientrelations_added
        )

        # Add the ingredientgroups of the ingredients that are not in
        # Food.ingredientgroups to the representation.
        ingredientgroups_added = []
        for ingredient in ingredients:
            if ingredient.group not in ingredientgroups \
                    and ingredient.group not in ingredientgroups_added:
                ingredientgroups_added.append(
                    ingredient.group
                )

        result['ingredientgroups'] = IngredientGroupSerializer(
            many=True,
            context=self.context
        ).to_representation(
            ingredientgroups_added + list(ingredientgroups)
        )

        return result


class TokenSerializer(serializers.ModelSerializer):

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
            'device',
            'service',
            'active',
        )


class TokenDetailSerializer(TokenSerializer):

    class Meta(TokenSerializer.Meta):
        fields = TokenSerializer.Meta.fields + (
            'identifier',
        )
        read_only_fields = TokenSerializer.Meta.read_only_fields + (
            'identifier',
        )
