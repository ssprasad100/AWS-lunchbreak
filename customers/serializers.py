from datetime import timedelta

from customers.exceptions import (AmountInvalid, CostCheckFailed,
                                  MinTimeExceeded, PastOrderDenied, StoreClosed)
from customers.models import Order, OrderedFood, User, UserToken
from django.utils import timezone
from lunch.exceptions import BadRequest
from lunch.models import Food, INPUT_AMOUNT, OpeningHours, Store
from lunch.serializers import (IngredientGroupSerializer,
                               ShortDefaultIngredientRelationSerializer,
                               StoreSerializer, TokenSerializer)
from rest_framework import serializers


class ShortStoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Store
        fields = ('id', 'name',)
        read_only_fields = ('name',)


class OrderedFoodSerializer(serializers.ModelSerializer):
    ingredientGroups = IngredientGroupSerializer(many=True, read_only=True)
    cost = serializers.DecimalField(decimal_places=2, max_digits=5)

    class Meta:
        model = OrderedFood
        fields = ('id', 'ingredients', 'amount', 'order', 'original', 'ingredientGroups', 'cost')
        read_only_fields = ('id', 'order', 'ingredientGroups',)


class OrderedFoodPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderedFood
        fields = ('ingredients', 'amount', 'original',)
        write_only_fields = fields


class ShortOrderSerializer(serializers.ModelSerializer):
    '''
    Used after placing an order for confirmation.
    '''

    orderedFood = OrderedFoodSerializer(many=True, write_only=True)

    def costCheck(self, order, orderedFood, amount, cost):
        if orderedFood.cost * amount != cost:
            order.delete()
            raise CostCheckFailed()

    def amountCheck(self, order, original, amount):
        if not float(amount).is_integer() and original.foodType.inputType == INPUT_AMOUNT:
            order.delete()
            raise AmountInvalid()

    def create(self, validated_data):
        pickupTime = validated_data['pickupTime']
        orderedFood = validated_data['orderedFood']
        store = validated_data['store']

        if len(orderedFood) == 0:
            raise BadRequest()

        if pickupTime < timezone.now():
            raise PastOrderDenied()

        if pickupTime - timezone.now() < timedelta(minutes=store.minTime):
            raise MinTimeExceeded()

        pickupDay = pickupTime.weekday()
        openingHours = OpeningHours.objects.filter(store=store, day=pickupDay)
        pTime = pickupTime.time()

        for o in openingHours:
            if o.opening <= pTime <= o.closing:
                break
        else:
            # If the for loop is not stopped by the break, it means that the time of pickup is never when the store is open.
            raise StoreClosed()

        user = self.context['user']

        order = Order(user=user, store=store, pickupTime=pickupTime)
        order.save()
        for f in orderedFood:
            original = f['original']
            amount = f['amount'] if 'amount' in f else 1
            self.amountCheck(order, original, amount)

            cost = f['cost']

            orderedF = OrderedFood(original=original, order=order, amount=amount)

            if 'ingredients' in f:
                orderedF.save()
                ingredients = f['ingredients']
                closestFood = Food.objects.closestFood(ingredients, original.foodType.id)
                orderedF.cost = OrderedFood.calculateCost(ingredients, closestFood)
                self.costCheck(order, orderedF, amount, cost)
            else:
                self.costCheck(order, original, amount, cost)
                orderedF.cost = original.cost

            orderedF.save()
        return order

    class Meta:
        model = Order
        fields = ('id', 'store', 'pickupTime', 'paid', 'total', 'orderedFood', 'status',)
        read_only_fields = ('id', 'paid', 'total', 'status',)


class OrderSerializer(serializers.ModelSerializer):
    '''
    Used for listing a specific or all orders.
    '''

    store = StoreSerializer(read_only=True)
    orderedfood = OrderedFoodSerializer(many=True, read_only=True, source='orderedfood_set')

    class Meta:
        model = Order
        fields = ('id', 'store', 'orderedTime', 'pickupTime', 'status', 'paid', 'total', 'orderedfood',)
        read_only_fields = ('id', 'store', 'orderedTime', 'pickupTime', 'status', 'paid', 'total', 'orderedfood',)


class UserSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(required=False, write_only=True)
    device = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'phone', 'pin', 'device',)
        read_only_fields = ('id',)
        write_only_fields = ('phone', 'pin', 'device',)


class UserTokenSerializer(TokenSerializer):
    user = UserSerializer()

    class Meta:
        model = UserToken
        fields = TokenSerializer.Meta.fields + ('user',)
        read_only_fields = TokenSerializer.Meta.read_only_fields + ('user',)
