import math

from lunch import serializers as lunch_serializers
from lunch.config import INPUT_SI_SET, INPUT_SI_VARIABLE
from lunch.exceptions import BadRequest
from lunch.models import Food, IngredientGroup, Store
from Lunchbreak.serializers import PrimaryModelSerializer
from rest_framework import serializers
from rest_framework.fields import *  # NOQA
from rest_framework.relations import *  # NOQA

from .config import RESERVATION_STATUS_PLACED, RESERVATION_STATUS_USER
from .exceptions import AmountInvalid, CostCheckFailed, MinDaysExceeded
from .models import (Group, Invite, Membership, Order, OrderedFood,
                     Reservation, User, UserToken)


class StoreHeartSerializer(lunch_serializers.StoreSerializer):
    hearted = serializers.BooleanField()

    class Meta:
        model = Store
        fields = lunch_serializers.StoreSerializer.Meta.fields + (
            'hearted',
        )
        read_only_fields = lunch_serializers.StoreSerializer.Meta.fields + (
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


class ShortOrderSerializer(serializers.ModelSerializer):

    '''Used after placing an order for confirmation.'''

    orderedfood = OrderedFoodSerializer(
        many=True,
        write_only=True
    )

    def check_cost(self, cost_calculated, food, amount, cost_given):
        if math.ceil(
                (
                    cost_calculated * amount * (
                        food.amount
                        if food.foodtype.inputtype == INPUT_SI_SET
                        else 1
                    )
                ) * 100) / 100.0 != float(cost_given):
            raise CostCheckFailed()

    def check_amount(self, food, amount):
        if amount <= 0 or (
            not float(amount).is_integer() and
            food.foodtype.inputtype != INPUT_SI_VARIABLE
        ) or (
            food.quantity is not None and
            not food.quantity.min <= amount <= food.quantity.max
        ):
            raise AmountInvalid()

    def create(self, validated_data):
        pickup = validated_data['pickup']
        user_orderedfood = validated_data['orderedfood']
        store = validated_data['store']
        description = validated_data.get('description', '')

        if len(user_orderedfood) == 0:
            raise BadRequest('"orderedfood" is empty.')

        Store.is_open(store, pickup)

        user = self.context['user']

        order = Order(
            user=user,
            store=store,
            pickup=pickup,
            description=description
        )
        order.save()

        try:
            for f in user_orderedfood:
                original = f['original']
                if not original.is_orderable(pickup):
                    raise MinDaysExceeded()
                amount = f['amount'] if 'amount' in f else 1
                self.check_amount(original, amount)
                cost = f['cost']
                comment = f['comment'] if 'comment' in f and original.commentable else ''

                orderedfood = OrderedFood(
                    amount=amount,
                    cost=cost,
                    order=order,
                    original=original,
                    comment=comment
                )

                if 'ingredients' in f:
                    orderedfood.save()
                    ingredients = f['ingredients']

                    closest = Food.objects.closest(ingredients, original)
                    self.check_amount(closest, amount)
                    IngredientGroup.check_ingredients(ingredients, closest)
                    cost_calculated = OrderedFood.calculate_cost(ingredients, closest)
                    self.check_cost(cost_calculated, closest, amount, cost)

                    orderedfood.cost = cost_calculated
                    orderedfood.ingredients = ingredients
                else:
                    self.check_cost(original.cost, original, amount, cost)
                    orderedfood.cost = original.cost
                    orderedfood.is_original = True

                orderedfood.save()
        except:
            order.delete()
            raise

        order.save()
        return order

    class Meta:
        model = Order
        fields = (
            'id',
            'store',
            'pickup',
            'paid',
            'total',
            'total_confirmed',
            'orderedfood',
            'status',
            'description',
        )
        read_only_fields = (
            'id',
            'paid',
            'total',
            'total_confirmed',
            'status',
        )
        write_only_fields = (
            'description',
        )


class OrderSerializer(serializers.ModelSerializer):

    '''Used for listing a specific or all orders.'''

    store = lunch_serializers.StoreSerializer(
        read_only=True
    )
    orderedfood = OrderedFoodSerializer(
        many=True,
        read_only=True,
        source='orderedfood_set'
    )

    class Meta:
        model = Order
        fields = (
            'id',
            'store',
            'placed',
            'pickup',
            'status',
            'paid',
            'total',
            'total_confirmed',
            'orderedfood',
            'description',
        )
        read_only_fields = (
            'id',
            'store',
            'placed',
            'pickup',
            'status',
            'paid',
            'total',
            'total_confirmed',
            'orderedfood',
            'description',
        )


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
    email = serializers.EmailField(
        required=False,
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            'phone',
            'name',
            'email',
            'pin',
            'token',
        )
        write_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
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
            'email',
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


class UserMembershipSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'name',
        )


class MembershipSerializer(serializers.ModelSerializer):
    user = UserMembershipSerializer()

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
    invited_by = UserMembershipSerializer(
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


class MultiUserTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserToken
        fields = (
            'id',
            'device',
            'active',
        )
        read_only_fields = fields


class UserTokenSerializer(lunch_serializers.TokenSerializer):
    user = UserSerializer()

    class Meta:
        model = UserToken
        fields = lunch_serializers.TokenSerializer.Meta.fields + (
            'user',
        )
        read_only_fields = lunch_serializers.TokenSerializer.Meta.read_only_fields + (
            'user',
        )


class UserTokenUpdateSerializer(UserTokenSerializer):
    user = UserSerializer(
        read_only=True
    )

    class Meta:
        model = UserTokenSerializer.Meta.model
        fields = UserTokenSerializer.Meta.fields
        read_only_fields = (
            'id',
            'identifier',
            'device',
            'active',
            'user',
        )
