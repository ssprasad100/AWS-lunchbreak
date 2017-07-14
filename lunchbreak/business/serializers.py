from customers import serializers as customers_serializers
from customers.models import Group, Order, OrderedFood, User
from lunch import serializers as lunch_serializers
from lunch.config import TOKEN_IDENTIFIER_LENGTH
from lunch.models import (Food, Ingredient, IngredientGroup,
                          IngredientRelation, Store, StoreHeader)
from Lunchbreak.serializers import MoneyField, RequestAttributeDefault
from payconiq.serializers import MerchantSerializer, TransactionSerializer
from rest_framework import serializers
from versioning_prime.mixins import VersionedMixin

from .models import (AbstractPassword, Employee, EmployeeToken, Staff,
                     StaffToken)


class StoreDetailSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
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
            'country',
            'province',
            'city',
            'postcode',
            'street',
            'number',
            'wait',
            'enabled',
            'gocardless_enabled',
            'payconiq_enabled',
            'cash_enabled',
        )
        read_only_fields = (
            'id',
            'latitude',
            'longitude',
            'hearts_count',
            'categories',
        )


class StoreGoCardlessSerializer(serializers.BaseSerializer):

    def to_representation(self, url):
        return {
            'authorisation_link': url
        }


class StorePayconiqSerializer(MerchantSerializer):
    store = serializers.HiddenField(
        write_only=True,
        default=serializers.CreateOnlyDefault(
            RequestAttributeDefault(
                attribute='user.staff.store'
            )
        )
    )

    class Meta(MerchantSerializer.Meta):
        fields = MerchantSerializer.Meta.fields + (
            'store',
        )


class EmployeePasswordRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id',)


class StaffPasswordRequestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=191
    )

    class Meta:
        model = Staff
        fields = ('email',)


class PasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=191,
        write_only=True
    )
    password_reset = serializers.CharField(
        max_length=TOKEN_IDENTIFIER_LENGTH,
        write_only=True
    )

    class Meta:
        model = AbstractPassword
        fields = (
            'password',
            'password_reset',
            'email',
        )
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class EmployeePasswordSerializer(PasswordSerializer):

    class Meta(PasswordSerializer.Meta):
        model = Employee


class StaffPasswordSerializer(PasswordSerializer):

    class Meta(PasswordSerializer.Meta):
        model = Staff


class BusinessTokenSerializer(lunch_serializers.TokenDetailSerializer):
    password = serializers.CharField(
        max_length=191,
        write_only=True
    )

    class Meta(lunch_serializers.TokenDetailSerializer.Meta):
        fields = lunch_serializers.TokenDetailSerializer.Meta.fields + (
            'password',
        )
        read_only_fields = (
            'id',
            'identifier',
            'active',
        )


class StaffSerializer(serializers.ModelSerializer):
    store = StoreDetailSerializer()

    class Meta:
        model = Staff
        fields = (
            'id',
            'store',
        )
        read_only_fields = (
            'id',
        )


class StaffTokenSerializer(BusinessTokenSerializer):
    email = serializers.EmailField(
        source='staff.email',
        write_only=True,
        required=False
    )

    class Meta(BusinessTokenSerializer.Meta):
        model = StaffToken
        fields = BusinessTokenSerializer.Meta.fields + (
            'email',
            'staff',
        )
        extra_kwargs = {
            'staff': {
                'required': False
            }
        }


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = (
            'id',
            'name',
            'owner',
        )
        read_only_fields = (
            'id',
        )


class EmployeeTokenSerializer(BusinessTokenSerializer):

    class Meta(BusinessTokenSerializer.Meta):
        model = EmployeeToken
        fields = BusinessTokenSerializer.Meta.fields + (
            'employee',
        )


class OrderedFoodSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderedFood
        fields = (
            'id',
            'ingredients',
            'amount',
            'original',
            'cost',
            'is_original',
            'comment',
            'status',
        )
        read_only_fields = (
            'id',
            'ingredients',
            'amount',
            'original',
            'cost',
            'is_original',
            'comment',
            # 'status',
        )


class OrderSpreadSerializer(VersionedMixin, serializers.Serializer):
    amount = serializers.IntegerField(
        read_only=True
    )
    average = MoneyField(
        read_only=True
    )
    sum = MoneyField(
        read_only=True
    )
    unit = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        fields = (
            'amount',
            'average',
            'sum',
            'unit',
        )
        read_only_fields = fields


class GroupSerializer(serializers.ModelSerializer):
    store = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Store.objects.all(),
        default=serializers.CreateOnlyDefault(
            RequestAttributeDefault(
                attribute='user.staff.store'
            )
        )
    )

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'description',
            'email',
            'delivery',
            'payment_online_only',
            'deadline',
            'delay',
            'discount',
            'store',
        )
        read_only_fields = (
            'id',
        )


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'phone',
        )


class OrderSerializer(customers_serializers.OrderSerializer):
    user = UserSerializer(
        read_only=True
    )
    group = GroupSerializer(
        read_only=True
    )
    transaction = TransactionSerializer(
        read_only=True
    )

    class Meta(customers_serializers.OrderSerializer.Meta):
        fields = (
            'id',
            'user',
            'placed',
            'receipt',
            'status',
            'total',
            'total_confirmed',
            'discount',
            'description',
            'payment_method',
            'paid',
            'group',
            'group_order',
            'transaction',
        )
        read_only_fields = (
            'id',
            'user',
            'placed',
            'receipt',
            'total',
            'total_confirmed',
            'discount',
            'description',
            'payment_method',
            'paid',
            'group',
            'group_order',
            'transaction',
        )


class OrderDetailSerializer(OrderSerializer):
    orderedfood = OrderedFoodSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = OrderSerializer.Meta.fields + (
            'orderedfood',
        )
        read_only_fields = (
            'id',
            'user',
            'placed',
            'receipt',
            'total',
            'discount',
            'orderedfood',
            'description',
            'paid',
            'group_order',
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


class IngredientRelationSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRelation
        fields = (
            'ingredient',
            'selected',
        )
        extra_kwargs = {
            'selected': {
                'write_only': True
            }
        }


class PopularFoodSerializer(serializers.ModelSerializer):
    orderedfood_count = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        model = Food
        fields = (
            'id',
            'orderedfood_count',
        )
        read_only_fields = (
            'id',
            'orderedfood_count',
        )


class FoodSerializer(serializers.ModelSerializer):
    ingredients = lunch_serializers.IngredientRelationSerializer(
        source='ingredientrelations',
        many=True,
        required=False,
        read_only=True
    )
    ingredientrelations = IngredientRelationSerializer(
        many=True,
        required=False,
        write_only=True
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
            'description',
            'amount',
            'cost',
            'foodtype',
            'preorder_days',
            'commentable',
            'priority',

            'store',
            'menu',
            'ingredients',
            'ingredientgroups',

            'ingredientrelations',
            'deleted',
            'enabled',
            'last_modified',
        )
        read_only_fields = (
            'id',
            'ingredients',
            'store',
            'last_modified',
        )

    def create_or_update(self, validated_data, food=None):
        update = food is not None
        relations = validated_data.pop('ingredientrelations', None)

        if not update:
            food = super().create(validated_data)
        else:
            food = super().update(food, validated_data)

        if relations is not None:
            if update:
                IngredientRelation.objects.filter(food=food).delete()
            for relation in relations:
                IngredientRelation.objects.update_or_create(
                    food=food,
                    **relation
                )

        return food

    def create(self, validated_data):
        return self.create_or_update(validated_data)

    def update(self, instance, validated_data):
        return self.create_or_update(validated_data, instance)


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


class IngredientGroupDetailSerializer(serializers.ModelSerializer):
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = IngredientGroup
        fields = (
            'id',
            'name',
            'maximum',
            'minimum',
            'ingredients',
            'priority',
            'cost',
            'foodtype',
            'calculation',
        )
        read_only_fields = (
            'id',
            'ingredients',
        )


class FoodDetailSerializer(lunch_serializers.FoodDetailSerializer):

    class Meta(lunch_serializers.FoodDetailSerializer.Meta):
        fields = lunch_serializers.FoodDetailSerializer.Meta.fields + (
            'enabled',
            'deleted',
        )


class StoreHeaderSerializer(serializers.ModelSerializer):
    store = serializers.HiddenField(
        write_only=True,
        default=serializers.CreateOnlyDefault(
            RequestAttributeDefault(
                attribute='user.staff.store'
            )
        )
    )

    class Meta:
        model = StoreHeader
        fields = (
            'store',
            'original',
        )
