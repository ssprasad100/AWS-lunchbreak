import math

from customers.config import RESERVATION_STATUS_PLACED, RESERVATION_STATUS_USER
from customers.exceptions import (AmountInvalid, CostCheckFailed,
                                  MinDaysExceeded)
from customers.models import Order, OrderedFood, Reservation, User, UserToken
from lunch import serializers as lunchSerializers
from lunch.config import INPUT_SI_SET, INPUT_SI_VARIABLE
from lunch.exceptions import BadRequest
from lunch.models import Food, IngredientGroup, Store
from rest_framework import serializers


class StoreHeartSerializer(lunchSerializers.StoreSerializer):
    hearted = serializers.BooleanField()

    class Meta:
        model = Store
        fields = lunchSerializers.StoreSerializer.Meta.fields + (
            'hearted',
        )
        read_only_fields = lunchSerializers.StoreSerializer.Meta.fields + (
            'hearted',
        )


class StoreHeartSerializerV3(lunchSerializers.StoreSerializer):
    minTime = serializers.IntegerField(
        source='minTimeV3'
    )
    hearted = serializers.BooleanField()

    class Meta:
        model = Store
        fields = lunchSerializers.StoreSerializer.Meta.fields + (
            'hearted',
        )
        read_only_fields = lunchSerializers.StoreSerializer.Meta.fields + (
            'hearted',
        )


class ReservationSerializer(serializers.ModelSerializer):
    user = serializers.ModelField(
        model_field=Reservation()._meta.get_field('user'),
        read_only=True,
        default=serializers.CurrentUserDefault()
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
    ingredientGroups = lunchSerializers.IngredientGroupSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = OrderedFood
        fields = (
            'id',
            'ingredients',
            'amount',
            'foodAmount',
            'order',
            'original',
            'ingredientGroups',
            'cost',
            'useOriginal',
            'comment',
        )
        read_only_fields = (
            'id',
            'foodAmount',
            'order',
            'ingredientGroups',
            'useOriginal',
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

    orderedFood = OrderedFoodSerializer(
        many=True,
        write_only=True
    )

    def costCheck(self, calculatedCost, food, amount, givenCost):
        if math.ceil(
            (
                calculatedCost * amount * (
                    food.amount
                    if food.foodType.inputType == INPUT_SI_SET
                    else 1
                )
            ) * 100) / 100.0 != float(givenCost):
            raise CostCheckFailed()

    def amountCheck(self, food, amount):
        if amount <= 0 or (
            not float(amount).is_integer() and
            food.foodType.inputType != INPUT_SI_VARIABLE
        ) or (
            food.quantity is not None and
            not food.quantity.amountMin <= amount <= food.quantity.amountMax
        ):
            raise AmountInvalid()

    def create(self, validated_data):
        pickupTime = validated_data['pickupTime']
        orderedFood = validated_data['orderedFood']
        store = validated_data['store']
        description = validated_data.get('description', '')

        if len(orderedFood) == 0:
            raise BadRequest('orderedFood empty.')

        Store.checkOpen(store, pickupTime)

        user = self.context['user']

        order = Order(user=user, store=store, pickupTime=pickupTime, description=description)
        order.save()

        try:
            for f in orderedFood:
                original = f['original']
                if not original.canOrder(pickupTime):
                    raise MinDaysExceeded()
                amount = f['amount'] if 'amount' in f else 1
                self.amountCheck(original, amount)
                cost = f['cost']
                foodAmount = original.amount if original.foodType.inputType == INPUT_SI_SET else 1
                comment = f['comment'] if 'comment' in f and original.canComment else ''

                orderedF = OrderedFood(
                    amount=amount,
                    foodAmount=foodAmount,
                    cost=cost,
                    order=order,
                    original=original,
                    comment=comment
                )

                if 'ingredients' in f:
                    orderedF.save()
                    ingredients = f['ingredients']

                    closestFood = Food.objects.closestFood(ingredients, original)
                    self.amountCheck(closestFood, amount)
                    IngredientGroup.checkIngredients(ingredients, closestFood)
                    calculatedCost = OrderedFood.calculateCost(ingredients, closestFood)
                    self.costCheck(calculatedCost, closestFood, amount, cost)

                    orderedF.cost = calculatedCost
                    orderedF.ingredients = ingredients
                else:
                    self.costCheck(original.cost, original, amount, cost)
                    orderedF.cost = original.cost
                    orderedF.useOriginal = True

                orderedF.save()
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
            'pickupTime',
            'paid',
            'total',
            'confirmedTotal',
            'orderedFood',
            'status',
            'description',
        )
        read_only_fields = (
            'id',
            'paid',
            'total',
            'confirmedTotal',
            'status',
        )
        write_only_fields = (
            'description',
        )


class ShortOrderSerializerOld(ShortOrderSerializer):
    total = serializers.DecimalField(
        source='eventualTotal',
        max_digits=7,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Order
        fields = (
            'id',
            'store',
            'pickupTime',
            'paid',
            'total',
            'orderedFood',
            'status',
            'description',
        )
        read_only_fields = (
            'id',
            'paid',
            'total',
            'status',
        )
        write_only_fields = (
            'description',
        )


class OrderSerializer(serializers.ModelSerializer):
    '''Used for listing a specific or all orders.'''

    store = lunchSerializers.StoreSerializer(
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
            'orderedTime',
            'pickupTime',
            'status',
            'paid',
            'total',
            'confirmedTotal',
            'orderedfood',
            'description',
        )
        read_only_fields = (
            'id',
            'store',
            'orderedTime',
            'pickupTime',
            'status',
            'paid',
            'total',
            'confirmedTotal',
            'orderedfood',
            'description',
        )


class OrderSerializerOld(OrderSerializer):
    total = serializers.DecimalField(
        source='eventualTotal',
        max_digits=7,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Order
        fields = (
            'id',
            'store',
            'orderedTime',
            'pickupTime',
            'status',
            'paid',
            'total',
            'orderedfood',
            'description',
        )
        read_only_fields = (
            'id',
            'store',
            'orderedTime',
            'pickupTime',
            'status',
            'paid',
            'total',
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


class MultiUserTokenSerializer(lunchSerializers.MultiTokenSerializer):
    user = UserSerializer(
        read_only=True
    )

    class Meta:
        model = UserToken
        fields = lunchSerializers.MultiTokenSerializer.Meta.fields + (
            'user',
        )
        read_only_fields = lunchSerializers.MultiTokenSerializer.Meta.read_only_fields + (
            'user',
        )


class UserTokenSerializer(lunchSerializers.TokenSerializer):
    user = UserSerializer()

    class Meta:
        model = UserToken
        fields = lunchSerializers.TokenSerializer.Meta.fields + (
            'user',
        )
        read_only_fields = lunchSerializers.TokenSerializer.Meta.read_only_fields + (
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
