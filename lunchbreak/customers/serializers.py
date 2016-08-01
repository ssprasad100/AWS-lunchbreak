from django_gocardless.serializers import RedirectFlowSerializer
from lunch import serializers as lunch_serializers
from lunch.models import Store
from Lunchbreak.serializers import PrimaryModelSerializer
from rest_framework import serializers
from rest_framework.fields import *  # NOQA
from rest_framework.relations import *  # NOQA

from .config import RESERVATION_STATUS_PLACED, RESERVATION_STATUS_USER
from .models import (Address, Group, Invite, Membership, Order, OrderedFood,
                     PaymentLink, Reservation, User, UserToken)


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


class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.ModelField(
        model_field=Reservation()._meta.get_field('user'),
        read_only=True,
        default=CreateOnlyDefault(serializers.CurrentUserDefault())
    )
    status = serializers.ChoiceField(
        choices=RESERVATION_STATUS_USER,
        default=serializers.CreateOnlyDefault(RESERVATION_STATUS_PLACED)
    )

    class Meta:
        model = Reservation
        fields = (
            'id',
            'user',
            'store',
            'seats',
            'placed',
            'reservation_time',
            'comment',
            'suggestion',
            'response',
            'status',
        )
        read_only_fields = (
            'id',
            'placed',
            'suggestion',
            'response',
        )
        write_only_fields = (
            'store',
            'reservation_time',
        )

    def update(self, instance, validated_data):
        return super(ReservationSerializer, self).update(
            instance,
            validated_data={
                'status': validated_data.get(
                    'status',
                    instance.status
                ),
                'comment': validated_data.get(
                    'comment', instance.comment
                )
            }
        )


class OrderedFoodSerializer(serializers.ModelSerializer):
    ingredientgroups = lunch_serializers.IngredientGroupSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = OrderedFood
        fields = (
            'id',
            'ingredients',
            'amount',
            'order',
            'original',
            'ingredientgroups',
            'cost',
            'is_original',
            'comment',
        )
        read_only_fields = (
            'id',
            'order',
            'ingredientgroups',
            'is_original',
        )


class OrderedFoodPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderedFood
        fields = (
            'ingredients',
            'amount',
            'original',
        )
        write_only_fields = fields


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

    class Meta:
        model = Order
        fields = (
            'id',
            'store',
            'receipt',
            'total',
            'total_confirmed',
            'orderedfood',
            'status',
            'description',
            'user',
            'payment_method',
            'delivery_address',
        )
        read_only_fields = (
            'id',
            'total',
            'total_confirmed',
            'status',
        )
        write_only_fields = (
            'description',
        )

    def create(self, validated_data):
        return Order.create(
            **validated_data
        )


class OrderDetailSerializer(OrderSerializer):

    """Used for listing a specific or all orders."""

    store = lunch_serializers.StoreSerializer(
        read_only=True
    )
    orderedfood = OrderedFoodSerializer(
        many=True,
        read_only=True,
        source='orderedfood_set'
    )

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + (
            'placed',
            'description',
        )
        read_only_fields = OrderSerializer.Meta.read_only_fields + (
            'store',
            'placed',
            'receipt',
            'orderedfood',
            'description',
            'payment_method',
        )
        write_only_fields = ()


class UserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'phone',
        )
        write_only_fields = (
            'phone',
        )


class UserTokenLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserToken
        fields = (
            'device',
            'service',
            'registration_id',
        )
        write_only_fields = fields


class UserLoginSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(
        write_only=True
    )
    token = UserTokenLoginSerializer(
        write_only=True
    )
    name = serializers.CharField(
        max_length=255,
        required=False,
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'phone',
            'name',
            'pin',
            'token',
        )
        write_only_fields = fields


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'name',
        )


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Membership
        fields = (
            'id',
            'leader',
            'user',
        )


class GroupSerializer(serializers.ModelSerializer):
    memberships = MembershipSerializer(
        source='membership_set',
        many=True,
        read_only=True
    )
    user = serializers.HiddenField(
        default=CreateOnlyDefault(serializers.CurrentUserDefault())
    )

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'billing',
            'memberships',
            'user',
        )
        read_only_fields = (
            'memberships',
        )
        write_only_fields = (
            'user',
        )

    def create(self, validated_data):
        values = {
            'name': validated_data['name'],
            'user': validated_data['user']
        }
        if 'billing' in validated_data:
            values['billing'] = validated_data['billing']

        return Group.create(
            **values
        )


class GroupInviteSerializer(PrimaryModelSerializer):

    class Meta:
        model = Group
        fields = (
            'id',
            'name',
        )


class InviteSerializer(serializers.ModelSerializer):
    group = GroupInviteSerializer(
        queryset=Group.objects.all()
    )
    invited_by = UserSerializer(
        read_only=True,
        default=CreateOnlyDefault(serializers.CurrentUserDefault())
    )

    class Meta:
        model = Invite
        fields = (
            'id',
            'group',
            'user',
            'invited_by',
            'status',
        )
        read_only_fields = (
            'invited_by',
            'status',
        )


class InviteUpdateSerializer(InviteSerializer):

    class Meta:
        model = Invite
        fields = (
            'status',
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
        write_only_fields = (
            'phone',
            'pin',
            'device',
        )


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
            store=self.context['store']
        )

    def update(self, instance, validated_data):
        return PaymentLink.create(
            user=validated_data['user'],
            store=self.context['store'],
            instance=instance
        )
