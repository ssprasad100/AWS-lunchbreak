from django_gocardless.serializers import RedirectFlowSerializer
from django_sms.models import Phone
from lunch import serializers as lunch_serializers
from lunch.models import Food, Store
from lunch.serializers import FoodSerializer
from Lunchbreak.serializers import MoneyField, PrimaryModelSerializer
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers

from .config import PAYMENTLINK_COMPLETION_REDIRECT_URL
from .models import (Address, Group, GroupOrder, Order, OrderedFood,
                     PaymentLink, User, UserToken)


class StoreHeartSerializer(lunch_serializers.StoreDetailSerializer):
    hearted = serializers.BooleanField()

    class Meta:
        model = Store
        fields = lunch_serializers.StoreDetailSerializer.Meta.fields + (
            'hearted',
        )
        read_only_fields = lunch_serializers.StoreDetailSerializer.Meta.fields + (
            'hearted',
        )


class OrderedFoodSerializer(serializers.ModelSerializer):
    ingredientgroups = lunch_serializers.IngredientGroupSerializer(
        many=True,
        read_only=True
    )
    total = MoneyField()

    class Meta:
        model = OrderedFood
        fields = (
            'id',
            'ingredients',
            'amount',
            'original',
            'ingredientgroups',
            'cost',
            'total',
            'is_original',
            'comment',
            'status',
        )
        read_only_fields = (
            'id',
            'ingredientgroups',
            'is_original',
            'cost',
            'status',
        )
        extra_kwargs = {
            'amount': {
                'required': True
            }
        }


class OrderedFoodPriceSerializer(serializers.ModelSerializer):
    food = FoodSerializer(read_only=True)

    class Meta:
        model = OrderedFood
        fields = (
            'ingredients',
            'amount',
            'original',
            'cost',
            'food',
        )
        extra_kwargs = {
            'ingredients': {
                'write_only': True,
            },
            'amount': {
                'write_only': True,
            },
            'original': {
                'write_only': True,
            },
        }
        read_only_fields = (
            'cost',
            'food',
        )

    def to_representation(self, obj):
        original = obj['original']
        if 'ingredients' in obj:
            ingredients = obj['ingredients']
            food_closest = Food.objects.closest(ingredients, original)
            food_closest.check_ingredients(
                ingredients=ingredients
            )

            obj['cost'] = OrderedFood.calculate_cost(ingredients, food_closest)
            obj['food'] = food_closest
        else:
            obj['cost'] = original.cost
            obj['food'] = original

        return super().to_representation(obj)


class PrimaryAddressSerializer(PrimaryModelSerializer):

    class Meta:
        model = Address
        fields = (
            'country',
            'province',
            'city',
            'postcode',
            'street',
            'number',
            'latitude',
            'longitude'
        )
        read_only = fields


class GroupSerializer(PrimaryModelSerializer):

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'description',
            'delivery',
            'payment_online_only',
            'deadline',
            'delay',
            'discount',
        )
        read_only_fields = (
            'id',
        )


class OrderNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = (
            'user',
            'placed',
            'receipt',
            'status',
            'total',
            'total_confirmed',
            'discount',
            'description',
            'payment',
            'payment_method',
            'paid',
        )
        read_only_fields = fields


class GroupOrderSerializer(serializers.ModelSerializer):
    group = GroupSerializer(
        read_only=True
    )

    class Meta:
        model = GroupOrder
        fields = (
            'id',
            'group',
            'date',
            'status',
        )
        read_only_fields = (
            'id',
            'group',
            'date',
        )
        extra_kwargs = {
            'status': {
                'write_only': True
            }
        }


class GroupOrderDetailSerializer(GroupOrderSerializer):
    orders = OrderNestedSerializer(
        read_only=True,
        many=True
    )

    class Meta(GroupOrderSerializer.Meta):
        fields = GroupOrderSerializer.Meta.fields + (
            'orders',
        )
        read_only_fields = GroupOrderSerializer.Meta.read_only_fields + (
            'orders',
        )


class OrderSerializer(serializers.ModelSerializer):
    """Used after placing an order for confirmation."""

    orderedfood = OrderedFoodSerializer(
        many=True,
        write_only=True
    )
    delivery_address = PrimaryAddressSerializer(
        queryset=Address.objects.all(),
        required=False
    )
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    group = GroupSerializer(
        queryset=Group.objects.all(),
        required=False
    )

    class Meta:
        model = Order
        fields = (
            'id',
            'store',
            'receipt',
            'total',
            'total_confirmed',
            'discount',
            'orderedfood',
            'status',
            'description',
            'user',
            'payment_method',
            'delivery_address',
            'paid',
            'group',
            'group_order',
        )
        read_only_fields = (
            'id',
            'total',
            'total_confirmed',
            'discount',
            'status',
            'paid',
            'group',
            'group_order',
        )

    def create(self, validated_data):
        return Order.objects.create_with_orderedfood(
            **validated_data
        )


class OrderDetailSerializer(OrderSerializer):

    """Used for listing a specific or all orders."""

    store = lunch_serializers.StoreSerializer(
        read_only=True
    )
    orderedfood = OrderedFoodSerializer(
        many=True,
        read_only=True
    )

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + (
            'placed',
            'description',
            'paid',
        )
        read_only_fields = OrderSerializer.Meta.read_only_fields + (
            'store',
            'placed',
            'receipt',
            'orderedfood',
            'description',
            'payment_method',
            'paid',
        )


class UserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Phone
        fields = (
            'phone',
        )
        extra_kwargs = {
            'phone': {
                'validators': [
                    validate_international_phonenumber
                ],
                'write_only': True
            }
        }


class UserTokenLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserToken
        fields = (
            'device',
            'service',
            'registration_id',
        )
        extra_kwargs = {
            'device': {
                'write_only': True
            },
            'service': {
                'write_only': True
            },
            'registration_id': {
                'write_only': True
            },
        }


class UserLoginSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(
        write_only=True
    )
    token = UserTokenLoginSerializer(
        write_only=True
    )
    name = serializers.CharField(
        max_length=191,
        required=False,
        write_only=True
    )
    phone = serializers.CharField(
        write_only=True,
        validators=[
            validate_international_phonenumber
        ]
    )

    class Meta:
        model = User
        fields = (
            'pin',
            'token',
            'name',
            'phone',
        )
        extra_kwargs = {
            'phone': {
                'validators': [
                    validate_international_phonenumber
                ]
            }
        }


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'name',
        )


class UserDetailSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(
        required=False,
        write_only=True
    )
    device = serializers.CharField(
        required=False,
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'phone',
            'pin',
            'device',
        )
        read_only_fields = (
            'id',
        )
        extra_kwargs = {
            'phone': {
                'write_only': True
            }
        }


class UserTokenSerializer(lunch_serializers.TokenSerializer):

    class Meta(lunch_serializers.TokenSerializer.Meta):
        model = UserToken


class UserTokenDetailSerializer(UserTokenSerializer):
    user = UserDetailSerializer()

    class Meta(UserTokenSerializer.Meta):
        fields = UserTokenSerializer.Meta.fields + (
            'user',
            'identifier'
        )
        read_only_fields = UserTokenSerializer.Meta.read_only_fields + (
            'user',
            'identifier'
        )


class UserTokenUpdateSerializer(UserTokenDetailSerializer):
    user = UserDetailSerializer(
        read_only=True
    )

    class Meta:
        model = UserTokenDetailSerializer.Meta.model
        fields = UserTokenDetailSerializer.Meta.fields
        read_only_fields = (
            'id',
            'identifier',
            'device',
            'active',
            'user',
        )


class PaymentLinkSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    redirectflow = RedirectFlowSerializer(
        read_only=True
    )

    class Meta:
        model = PaymentLink
        fields = (
            'user',
            'redirectflow',
        )
        read_only_fields = (
            'store',
            'redirectflow',
        )

    def create(self, validated_data):
        return PaymentLink.create(
            user=validated_data['user'],
            store=self.context['store'],
            completion_redirect_url=PAYMENTLINK_COMPLETION_REDIRECT_URL
        )

    def update(self, instance, validated_data):
        return PaymentLink.create(
            user=validated_data['user'],
            store=self.context['store'],
            instance=instance,
            completion_redirect_url=PAYMENTLINK_COMPLETION_REDIRECT_URL
        )
